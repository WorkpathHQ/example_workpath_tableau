from dataclasses import dataclass
from enum import Enum
from typing import Iterator

import requests


class NotFoundError(Exception):
    """Raised when an entity is not found in the Workpath Connect API."""


class WorkpathType(Enum):
    KPI = "kpi"
    KEY_RESULT = "key_result"


@dataclass
class WorkpathEntity:
    type: WorkpathType
    id: str

    @classmethod
    def from_json(cls, json: dict) -> "WorkpathEntity":
        return cls(type=WorkpathType(json["type"]), id=json["id"])

    def __str__(self) -> str:
        return f"{self.type.value} {self.id}"


class ConnectAPI:
    """Client for the Workpath Connect API. Only covers the parts of the API that are needed for this demo."""

    def __init__(self, domain: str, token: str):
        self.base_url = f"https://{domain}/api/v2"
        self.token = token

    def update_entity(self, entity: WorkpathEntity, value: float) -> dict:
        """Update the current value of a KPI or key result."""
        if entity.type == WorkpathType.KPI:
            return self.update_kpi(entity.id, value)
        elif entity.type == WorkpathType.KEY_RESULT:
            return self.update_key_result(entity.id, value)
        else:
            raise ValueError(f"Unknown entity type {entity.type}")

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

    def update_key_result(self, key_result_id: str, value: float) -> dict:
        url = f"{self.base_url}/key_results/{key_result_id}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        data = {"current_value": value}
        response = requests.patch(url, headers=headers, json=data)
        if response.status_code == 404:
            raise NotFoundError(f"Key result {key_result_id} not found")
        response.raise_for_status()
        return response.json()

    @classmethod
    def paged_request(cls, url: str, headers: dict) -> Iterator[dict]:
        """Yield all entities from a paged API endpoint."""
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            json = response.json()
            yield from json
            url = response.headers.get("Pagination-Next-Page")

    def list_kpis(self) -> list[dict]:
        url = f"{self.base_url}/kpis"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        yield from self.paged_request(url, headers)

    def list_goals(self) -> Iterator[dict]:
        url = f"{self.base_url}/goals"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
        yield from self.paged_request(url, headers)
