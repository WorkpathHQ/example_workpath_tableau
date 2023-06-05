import logging
import os
from argparse import ArgumentParser, Namespace

import yaml

from .connect import ConnectAPI, NotFoundError, WorkpathEntity
from .tableau import get_kpi_data, list_views as _list_views, sign_in, KPIError, TableauKPI, Server


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
    return [(TableauKPI.from_json(kpi["tableau"]), WorkpathEntity.from_json(kpi["workpath"])) for kpi in kpis_yaml]


def connect_to_tableau(args: Namespace) -> Server:
    logger.info("Connect to Tableau at %s", args.tableau_domain)
    return sign_in(args.tableau_domain, args.site_id, args.pat_name, args.pat)


def connect_to_connect_api(args: Namespace) -> ConnectAPI:
    logger.info("Connect to Workpath API at %s", args.connect_domain)
    return ConnectAPI(args.connect_domain, args.connect_token)


def sync_kpis():
    """Sync KPIs from Tableau to Workpath KPIs or Key Results."""
    set_up_logging()
    args = parse_args()

    tableau_server = connect_to_tableau(args)
    connect_client = connect_to_connect_api(args)

    logger.info("Load list of KPIs to sync from %s", args.kpis_path)
    connected_kpis = load_connected_kpis(args.kpis_path)

    logger.info("Start update of %d KPIs", len(connected_kpis))
    for tableau_kpi, workpath_entity in connected_kpis:
        logger.info("Get %s from Tableau", tableau_kpi)
        try:
            current_value = get_kpi_data(tableau_server, tableau_kpi)
        except KPIError as e:
            logger.warning("Could not get %s from Tableau: %s", tableau_kpi, e)
        else:
            logger.info("Update %s in Connect API with its value", workpath_entity)
            try:
                connect_client.update_entity(workpath_entity, current_value)
            except NotFoundError:
                logger.warning("Entity %s not found in Connect API", workpath_entity)

    logger.info("Done, sign out of Tableau")
    tableau_server.auth.sign_out()


def list_views():
    """List all views available from Tableau Server."""
    set_up_logging()
    args = parse_args()

    tableau_server = connect_to_tableau(args)

    for view in _list_views(tableau_server):
        print(f"View {view.id} {view.name}")


def list_kpis():
    """List all KPIs available from Workpath Connect API."""
    set_up_logging()
    args = parse_args()

    connect_client = connect_to_connect_api(args)

    for kpi in connect_client.list_kpis():
        print(f"KPI {kpi['id']} {kpi['title']}")


def list_goals():
    """List all Goals and Key Results available from Connect API."""
    set_up_logging()
    args = parse_args()

    connect_client = connect_to_connect_api(args)

    for goal in connect_client.list_goals():
        print(f"Goal {goal['id']} {goal['title']}")
        for kr in goal["key_results"]:
            print(f"- KR {kr['id']} {kr['title']}")
        print()
