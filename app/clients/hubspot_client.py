"""HubSpot API client with simulation-safe behavior for local development.

When `ENABLE_CRM_SIMULATION=true` or when `HUBSPOT_ACCESS_TOKEN` is missing,
all operations return deterministic simulated payloads and no external API call
is attempted.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.core.settings import get_settings


class HubSpotClient:
    """Minimal HubSpot CRM client wrapper for contacts, companies, deals, notes, and tasks."""

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.hubspot_base_url.rstrip("/")
        self.token = settings.hubspot_access_token
        self.simulated = settings.enable_crm_simulation or not self.token
        self.timeout = 15.0

    def _sim(self, op: str, **data: Any) -> dict[str, Any]:
        return {"simulated": True, "operation": op, "data": data}

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}{path}",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    def _patch(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        with httpx.Client(timeout=self.timeout) as client:
            response = client.patch(
                f"{self.base_url}{path}",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    def search_contact(self, email: str | None = None, name: str | None = None) -> dict[str, Any]:
        if self.simulated:
            return self._sim("search_contact", email=email, name=name)
        filters: list[dict[str, str]] = []
        if email:
            filters.append({"propertyName": "email", "operator": "EQ", "value": email})
        if name:
            filters.append({"propertyName": "firstname", "operator": "EQ", "value": name})
        return self._post("/crm/v3/objects/contacts/search", {"filterGroups": [{"filters": filters}]})

    def create_contact(self, properties: dict[str, Any]) -> dict[str, Any]:
        if self.simulated:
            return self._sim("create_contact", properties=properties)
        return self._post("/crm/v3/objects/contacts", {"properties": properties})

    def search_company(self, name: str) -> dict[str, Any]:
        if self.simulated:
            return self._sim("search_company", name=name)
        payload = {
            "filterGroups": [{"filters": [{"propertyName": "name", "operator": "EQ", "value": name}]}]
        }
        return self._post("/crm/v3/objects/companies/search", payload)

    def create_company(self, properties: dict[str, Any]) -> dict[str, Any]:
        if self.simulated:
            return self._sim("create_company", properties=properties)
        return self._post("/crm/v3/objects/companies", {"properties": properties})

    def create_note(self, body: str) -> dict[str, Any]:
        if self.simulated:
            return self._sim("create_note", body=body)
        return self._post("/crm/v3/objects/notes", {"properties": {"hs_note_body": body}})

    def create_task(self, subject: str, due_date: str | None = None) -> dict[str, Any]:
        if self.simulated:
            return self._sim("create_task", subject=subject, due_date=due_date)
        properties: dict[str, Any] = {"hs_task_subject": subject}
        if due_date:
            properties["hs_timestamp"] = due_date
        return self._post("/crm/v3/objects/tasks", {"properties": properties})

    def search_deal(self, name: str) -> dict[str, Any]:
        if self.simulated:
            return self._sim("search_deal", name=name)
        payload = {
            "filterGroups": [{"filters": [{"propertyName": "dealname", "operator": "EQ", "value": name}]}]
        }
        return self._post("/crm/v3/objects/deals/search", payload)

    def create_deal(self, properties: dict[str, Any]) -> dict[str, Any]:
        if self.simulated:
            return self._sim("create_deal", properties=properties)
        return self._post("/crm/v3/objects/deals", {"properties": properties})

    def update_deal(self, deal_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        if self.simulated:
            return self._sim("update_deal", deal_id=deal_id, properties=properties)
        return self._patch(f"/crm/v3/objects/deals/{deal_id}", {"properties": properties})
