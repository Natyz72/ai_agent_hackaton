from datetime import datetime, timedelta
from typing import Any
import uuid

from app.config import settings
from app.db.client import db_client


class Repository:
    def __init__(self):
        self.client = db_client.get_client()

    # Trusted domains
    def get_trusted_domains(self) -> list[dict[str, Any]]:
        if not self.client:
            return []
        try:
            res = self.client.table("trusted_domains").select("*").execute()
            return res.data or []
        except Exception:
            return []

    # Reputation
    def get_domain_reputation(self, hostname: str) -> dict[str, Any] | None:
        if not self.client:
            return None
        try:
            res = (
                self.client.table("domain_reputation")
                .select("*")
                .eq("hostname", hostname.lower())
                .limit(1)
                .execute()
            )
            data = res.data or []
            return data[0] if data else None
        except Exception:
            return None

    def get_all_reputation(self) -> list[dict[str, Any]]:
        if not self.client:
            return []
        try:
            res = self.client.table("domain_reputation").select("*").execute()
            return res.data or []
        except Exception:
            return []

    # Guidance
    def search_guidance(self, query: str) -> list[dict[str, Any]]:
        if not self.client:
            return []
        try:
            res = self.client.table("guidance_passages").select("*").execute()
            rows = res.data or []
            q = query.lower()
            out = []
            for r in rows:
                text = (r.get("content") or r.get("text") or "").lower()
                title = (r.get("title") or "").lower()
                if q in text or q in title:
                    out.append(r)
            return out
        except Exception:
            return []

    def get_guidance_by_id(self, gid: str) -> dict[str, Any] | None:
        if not self.client:
            return None
        try:
            res = (
                self.client.table("guidance_passages")
                .select("*")
                .eq("id", gid)
                .limit(1)
                .execute()
            )
            data = res.data or []
            return data[0] if data else None
        except Exception:
            return None

    # Investigation proposals
    def create_proposal(self, message: str, output_snapshot: dict[str, Any]) -> dict[str, Any]:
        proposal_id = str(uuid.uuid4())
        now = datetime.utcnow()
        expires = now + timedelta(minutes=settings.proposal_expiry_minutes)
        row = {
            "id": proposal_id,
            "status": "pending",
            "message": message,
            "output_snapshot": output_snapshot,
            "created_at": now.isoformat() + "Z",
            "expires_at": expires.isoformat() + "Z",
        }
        if self.client:
            try:
                self.client.table("investigation_proposals").insert(row).execute()
            except Exception:
                pass
        return row

    def get_proposal(self, proposal_id: str) -> dict[str, Any] | None:
        if not self.client:
            return None
        try:
            res = (
                self.client.table("investigation_proposals")
                .select("*")
                .eq("id", proposal_id)
                .limit(1)
                .execute()
            )
            data = res.data or []
            return data[0] if data else None
        except Exception:
            return None

    def update_proposal_status(self, proposal_id: str, status: str) -> bool:
        if not self.client:
            return False
        try:
            self.client.table("investigation_proposals").update({"status": status}).eq("id", proposal_id).execute()
            return True
        except Exception:
            return False

    # Incidents
    def create_incident(self, record: dict[str, Any]) -> str | None:
        if not self.client:
            return None
        try:
            res = self.client.table("incidents").insert(record).execute()
            data = res.data or []
            if data and isinstance(data[0], dict):
                return data[0].get("id")
            return record.get("id")
        except Exception:
            return None

    def list_incidents(self, page: int = 1, page_size: int = 20) -> tuple[list[dict[str, Any]], int]:
        if not self.client:
            return [], 0
        try:
            res = self.client.table("incidents").select("*", count="exact").order("created_at", desc=True).range((page - 1) * page_size, page * page_size - 1).execute()
            return res.data or [], res.count or 0
        except Exception:
            return [], 0

    def get_incident(self, incident_id: str) -> dict[str, Any] | None:
        if not self.client:
            return None
        try:
            res = self.client.table("incidents").select("*").eq("id", incident_id).limit(1).execute()
            data = res.data or []
            return data[0] if data else None
        except Exception:
            return None

    # Activity
    def log_activity(self, event: dict[str, Any]) -> None:
        if not self.client:
            return
        try:
            self.client.table("activity_log").insert(event).execute()
        except Exception:
            pass

    def get_activity_for_incident(self, incident_id: str) -> list[dict[str, Any]]:
        if not self.client:
            return []
        try:
            res = self.client.table("activity_log").select("*").eq("incident_id", incident_id).order("timestamp", desc=False).execute()
            return res.data or []
        except Exception:
            return []


repo = Repository()
