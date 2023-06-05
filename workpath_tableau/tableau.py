import csv
from dataclasses import dataclass
from typing import Iterator


from tableauserverclient import Pager, PersonalAccessTokenAuth, ViewItem
from tableauserverclient.server.server import Server


@dataclass
class TableauKPI:
    """Identify a KPI in a Tableau view by its position in the exported CSV data."""

    view_id: str
    csv_row: int
    csv_col: int

    @classmethod
    def from_json(cls, json: dict) -> "TableauKPI":
        return cls(**json)

    def __str__(self) -> str:
        return f"KPI in view {self.view_id} at row {self.csv_row}, column {self.csv_col}"


class KPIError(Exception):
    """Raised when a KPI cannot be found in the CSV data, or isn't in numeric format."""


def sign_in(tableau_domain: str, site_id: str, pat_name: str, pat: str) -> Server:
    auth = PersonalAccessTokenAuth(pat_name, pat, site_id)
    server = Server(f"https://{tableau_domain}", use_server_version=True)
    server.auth.sign_in(auth)
    return server


def list_views(server: Server) -> Iterator[ViewItem]:
    yield from Pager(server.views)


def get_view_data(server: Server, view_id: str) -> Iterator[list[str]]:
    view = server.views.get_by_id(view_id)
    server.views.populate_csv(view)
    csv_raw = b"".join(view.csv).decode("utf-8")
    csv_lines = csv_raw.splitlines()
    return csv.reader(csv_lines)


def get_kpi_data(server: Server, kpi: TableauKPI) -> float:
    data = get_view_data(server, kpi.view_id)

    try:
        for _ in range(kpi.csv_row):
            next(data)
        row = next(data)
        kpi_data_raw = row[kpi.csv_col]
    except (StopIteration, IndexError):
        raise KPIError(f"KPI {kpi} not found in CSV data")
    else:
        try:
            kpi_data = float(kpi_data_raw)
        except ValueError:
            raise KPIError(f"KPI {kpi} is not numeric")
        else:
            return kpi_data
