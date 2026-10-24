from datetime import datetime, timedelta, timezone
from typing import Any
import uuid

from app.config import settings
from app.db.client import db_client


class Repository:
    def __init__(self):
        self.client = db_client.get_client()
        # In-memory storage for offline/test environments when client is None
        self._in_memory_proposals: dict[str, dict[str, Any]] = {}
        self._in_memory_incidents: dict[str, dict[str, Any]] = {}
        self._in_memory_activity: list[dict[str, Any]] = []

    # Trusted domains
    def get_trusted_domains(self) -> list[dict[str, Any]]:
        if not self.client:
            return [
                {"domain": "example.com", "reason": "Synthetic trusted domain"},
                {"domain": "trusted.example", "reason": "Synthetic trusted domain"},
                {"domain": "company.example", "reason": "Synthetic trusted domain"},
            ]
        try:
            res = self.client.table("trusted_domains").select("*").execute()
            return res.data or []
        except Exception:
            return []

    # Reputation
    def get_domain_reputation(self, hostname: str) -> dict[str, Any] | None:
        if not self.client:
            synthetic_reputation = {
                "suspicious.example": {"hostname": "suspicious.example", "status": "suspicious", "source": "synthetic_demo", "reason": "Synthetic demo entry - flagged pattern"},
                "phishy.example": {"hostname": "phishy.example", "status": "suspicious", "source": "synthetic_demo", "reason": "Synthetic demo entry - suspicious indicators"},
                "unknown-site.example": {"hostname": "unknown-site.example", "status": "unknown", "source": "synthetic_demo", "reason": "Synthetic demo entry - no data"},
                "trusted.example": {"hostname": "trusted.example", "status": "known_trusted", "source": "synthetic_demo", "reason": "Synthetic trusted domain"},
                "example.com": {"hostname": "example.com", "status": "known_trusted", "source": "synthetic_demo", "reason": "Synthetic trusted domain"},
                "company.example": {"hostname": "company.example", "status": "known_trusted", "source": "synthetic_demo", "reason": "Synthetic trusted domain"},
            }
            return synthetic_reputation.get(hostname.lower())
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
            default_passages = [
                {"id": "SEC-01", "title": "Verify sender identity", "content": "Always verify the sender through a separate channel before taking action on urgent requests. Attackers often impersonate trusted contacts.", "excerpt": "Verify sender through a separate channel."},
                {"id": "SEC-02", "title": "Be cautious with urgent requests", "content": "Urgency and pressure are common social engineering tactics. Take time to verify before clicking links or providing credentials.", "excerpt": "Urgency is a common red flag."},
                {"id": "SEC-03", "title": "Inspect URLs carefully", "content": "Check URLs for misspellings, unusual domains, and user-info tricks. Do not trust display text alone.", "excerpt": "Inspect URLs for anomalies."},
                {"id": "SEC-04", "title": "Never share credentials via email/SMS", "content": "Legitimate organizations will not ask for passwords or MFA codes via email or text message.", "excerpt": "Never share credentials via message."},
                {"id": "SEC-05", "title": "Report suspicious messages", "content": "Report suspected phishing to your security team. Preserve the message for investigation.", "excerpt": "Report and preserve suspicious messages."},
                {"id": "SEC-06", "title": "Use official channels for payments", "content": "Always confirm payment changes through official channels. Attackers often request urgent payment redirects.", "excerpt": "Confirm payment changes via official channels."},
            ]
            q = query.lower()
            return [
                p for p in default_passages
                if q in p["title"].lower() or q in p["content"].lower()
            ]
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
            for p in self.search_guidance(""):
                if p["id"] == gid:
                    return p
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
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=settings.proposal_expiry_minutes)
        row = {
            "id": proposal_id,
            "status": "pending",
            "message": message,
            "output_snapshot": output_snapshot,
            "created_at": now.isoformat(),
            "expires_at": expires.isoformat(),
        }
        if self.client:
            try:
                self.client.table("investigation_proposals").insert(row).execute()
            except Exception:
                pass
        else:
            self._in_memory_proposals[proposal_id] = row
        return row

    def get_proposal(self, proposal_id: str) -> dict[str, Any] | None:
        if not self.client:
            return self._in_memory_proposals.get(proposal_id)
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
            if proposal_id in self._in_memory_proposals:
                self._in_memory_proposals[proposal_id]["status"] = status
                return True
            return False
        try:
            self.client.table("investigation_proposals").update({"status": status}).eq("id", proposal_id).execute()
            return True
        except Exception:
            return False

    # Incidents
    def create_incident(self, record: dict[str, Any]) -> str | None:
        if not self.client:
            inc_id = record.get("id") or str(uuid.uuid4())
            record["id"] = inc_id
            self._in_memory_incidents[inc_id] = record
            return inc_id
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
            all_records = list(self._in_memory_incidents.values())
            # Sort newest first
            all_records.sort(key=lambda r: r.get("created_at", ""), reverse=True)
            start = (page - 1) * page_size
            end = start + page_size
            return all_records[start:end], len(all_records)
        try:
            res = self.client.table("incidents").select("*", count="exact").order("created_at", desc=True).range((page - 1) * page_size, page * page_size - 1).execute()
            return res.data or [], res.count or 0
        except Exception:
            return [], 0

    def get_incident(self, incident_id: str) -> dict[str, Any] | None:
        if not self.client:
            return self._in_memory_incidents.get(incident_id)
        try:
            res = self.client.table("incidents").select("*").eq("id", incident_id).limit(1).execute()
            data = res.data or []
            return data[0] if data else None
        except Exception:
            return None

    # Activity
    def log_activity(self, event: dict[str, Any]) -> None:
        if not self.client:
            self._in_memory_activity.append(event)
            return
        try:
            self.client.table("activity_log").insert(event).execute()
        except Exception:
            pass

    def get_activity_for_incident(self, incident_id: str) -> list[dict[str, Any]]:
        if not self.client:
            return [e for e in self._in_memory_activity if e.get("incident_id") == incident_id]
        try:
            res = self.client.table("activity_log").select("*").eq("incident_id", incident_id).order("timestamp", desc=False).execute()
            return res.data or []
        except Exception:
            return []


repo = Repository()
