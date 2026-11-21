"""Home serverdagi lab-agent bilan WireGuard tunnel orqali gaplashuvchi klient."""
from __future__ import annotations

from typing import Any

import httpx

from .config import settings


class LabAgentError(RuntimeError):
    pass


async def _request(method: str, path: str, json: dict[str, Any] | None = None, timeout: float = 15) -> Any:
    if not settings.labs_enabled:
        raise LabAgentError("Laboratoriya agenti sozlanmagan (LAB_AGENT_URL / LAB_AGENT_TOKEN).")
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.request(
                method,
                f"{settings.lab_agent_url}{path}",
                json=json,
                headers={"Authorization": f"Bearer {settings.lab_agent_token}"},
            )
    except httpx.HTTPError as exc:
        raise LabAgentError(f"Lab serverga ulanib bo'lmadi: {exc.__class__.__name__}") from exc
    if resp.status_code == 404:
        return None
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        raise LabAgentError(f"Lab agent xatosi ({resp.status_code}): {detail}")
    return resp.json() if resp.content else {}


async def create_lab(lab_id: str, topology: str, ttl_minutes: int) -> dict[str, Any]:
    return await _request("POST", "/labs", {"id": lab_id, "topology": topology, "ttl_minutes": ttl_minutes})


async def lab_status(lab_id: str) -> dict[str, Any] | None:
    return await _request("GET", f"/labs/{lab_id}")


async def destroy_lab(lab_id: str) -> None:
    await _request("DELETE", f"/labs/{lab_id}", timeout=120)


async def run_checks(lab_id: str) -> dict[str, Any]:
    return await _request("POST", f"/labs/{lab_id}/check", timeout=60)


async def agent_health() -> dict[str, Any] | None:
    return await _request("GET", "/health", timeout=5)
