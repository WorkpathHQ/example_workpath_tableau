import requests


class NotFoundError(Exception):
    """Raised when an entity is not found in the Workpath Connect API."""


class ConnectAPI:
    """Client for the Workpath Connect API. Only covers the parts of the API that are needed for this demo."""

    def __init__(self, domain: str, token: str):
        self.base_url = f"https://{domain}/api/v2"
        self.token = token

    def list_kpis(self) -> list[dict]:
        url = f"{self.base_url}/kpis"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def update_kpi(self, kpi_id: str, value: float) -> dict:
        url = f"{self.base_url}/kpis/{kpi_id}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        data = {"current_value": value}
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 404:
            raise NotFoundError(f"KPI {kpi_id} not found")
        response.raise_for_status()
        return response.json()
