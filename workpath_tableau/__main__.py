import logging
import os
from argparse import ArgumentParser

import yaml

from .connect import ConnectAPI, NotFoundError
from .tableau import get_kpi_data, sign_in, KPIError, TableauKPI


logger = logging.getLogger(__name__)


def set_up_logging():
    logging.getLogger("tableau").setLevel(logging.WARNING)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s\t%(levelname)s\t%(message)s",
    )


def parse_args():
    def add_arg_with_env_default(arg_name, default=None, **kwargs):
        """Add an argument to the parser with a default value from an environment variable."""
        env_var = arg_name.upper().replace("-", "_")
        default = os.getenv(env_var) or default
        if default is None:
            parser.add_argument(f"--{arg_name}", required=True, **kwargs)
        else:
            parser.add_argument(f"--{arg_name}", default=default, **kwargs)

    parser = ArgumentParser()

    # List of KPIs to sync
    parser.add_argument(
        "--kpis_path",
        default="connected_kpis.yml",
        help="Path to YAML file containing list of KPIs to sync",
    )

    # Tableau connection details
    add_arg_with_env_default("tableau_domain", help="Tableau Server domain, e.g. tableau.acme.com")
    add_arg_with_env_default("site_id", help="Tableau site ID")
    add_arg_with_env_default("pat_name", help="Tableau Personal Access Token name")
    add_arg_with_env_default("pat", help="Tableau Personal Access Token")

    # Workpath Connect API connection details
    add_arg_with_env_default(
        "connect_domain",
        default="connect.workpath.com",
        help="Workpath Connect domain, defaults to connect.workpath.com",
    )
    add_arg_with_env_default("connect_token", help="Workpath Connect API token")

    return parser.parse_args()


def load_connected_kpis(path: str) -> list[tuple[TableauKPI, str]]:
    """Load information on connected KPIs from YAML file."""
    with open(path) as f:
        kpis_yaml = yaml.safe_load(f)
    return [(TableauKPI(**kpi["tableau"]), kpi["connect_id"]) for kpi in kpis_yaml]


def sync_kpis():
    set_up_logging()

    args = parse_args()

    logger.info("Connect to Tableau at %s", args.tableau_domain)
    tableau_server = sign_in(args.tableau_domain, args.site_id, args.pat_name, args.pat)

    logger.info("Connect to Workpath API at %s", args.connect_domain)
    connect_client = ConnectAPI(args.connect_domain, args.connect_token)

    logger.info("Load list of KPIs to sync from %s", args.kpis_path)
    connected_kpis = load_connected_kpis(args.kpis_path)

    logger.info("Start update of %d KPIs", len(connected_kpis))
    for tableau_kpi, connect_kpi_id in connected_kpis:
        logger.info("Get KPI %s from Tableau", tableau_kpi)

        try:
            current_value = get_kpi_data(tableau_server, tableau_kpi)
        except KPIError as e:
            logger.warning("Could not get KPI %s from Tableau: %s", tableau_kpi, e)
        else:
            logger.info("Update KPI %s in Connect with its value", connect_kpi_id)
            try:
                connect_client.update_kpi(connect_kpi_id, current_value)
            except NotFoundError:
                logger.warning("KPI %s not found in Connect API", connect_kpi_id)

    logger.info("Done, sign out of Tableau")
    tableau_server.auth.sign_out()
