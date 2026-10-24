import pytest
import httpx
from app.main import app
from app.db.repositories import repo


@pytest.mark.asyncio
async def test_investigate_does_not_persist_incident():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        initial_incidents, _ = repo.list_incidents()
        initial_count = len(initial_incidents)

        resp = await client.post(
            "/api/investigate",
            json={"message": "Urgent! Click hxxp://phishy.example to unlock your account immediately."},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "proposal_id" in data
        assert data["status"] == "ok"

        # Verify NO incident was saved during investigate
        incidents_after, _ = repo.list_incidents()
        assert len(incidents_after) == initial_count


@pytest.mark.asyncio
async def test_approval_gate_rejects_unapproved_request():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Create a proposal first
        inv_resp = await client.post("/api/investigate", json={"message": "Urgent suspension warning."})
        proposal_id = inv_resp.json()["proposal_id"]

        # Attempt to save with approved: False
        save_resp = await client.post(
            "/api/incidents",
            json={"proposal_id": proposal_id, "approved": False},
        )
        assert save_resp.status_code == 400
        assert "approval is required" in save_resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_approval_gate_rejects_invalid_proposal():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        save_resp = await client.post(
            "/api/incidents",
            json={"proposal_id": "non-existent-uuid-12345", "approved": True},
        )
        assert save_resp.status_code == 400
        assert "not found" in save_resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_approval_gate_happy_path_and_duplicate_rejection():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # 1. Investigate message
        inv_resp = await client.post(
            "/api/investigate",
            json={"message": "Security Alert: Verify your login at hxxp://evil.example now."},
        )
        assert inv_resp.status_code == 200
        proposal_id = inv_resp.json()["proposal_id"]

        # 2. Approve and save incident
        save_resp = await client.post(
            "/api/incidents",
            json={
                "proposal_id": proposal_id,
                "approved": True,
                "analyst_notes": "Confirmed malicious phishing campaign.",
            },
        )
        assert save_resp.status_code == 200
        save_data = save_resp.json()
        assert save_data["success"] is True
        incident_id = save_data["incident_id"]
        assert incident_id is not None

        # 3. Duplicate save attempt should be REJECTED
        dup_resp = await client.post(
            "/api/incidents",
            json={"proposal_id": proposal_id, "approved": True},
        )
        assert dup_resp.status_code == 400
        assert "duplicate" in dup_resp.json()["detail"].lower()

        # 4. Fetch incident history
        list_resp = await client.get("/api/incidents")
        assert list_resp.status_code == 200
        list_data = list_resp.json()
        assert list_data["total"] >= 1
        assert any(i["id"] == incident_id for i in list_data["incidents"])

        # 5. Fetch incident detail
        detail_resp = await client.get(f"/api/incidents/{incident_id}")
        assert detail_resp.status_code == 200
        detail_data = detail_resp.json()
        assert detail_data["id"] == incident_id
        assert detail_data["analyst_notes"] == "Confirmed malicious phishing campaign."

        # 6. Fetch incident activity
        act_resp = await client.get(f"/api/incidents/{incident_id}/activity")
        assert act_resp.status_code == 200
        act_data = act_resp.json()
        assert len(act_data["activity"]) >= 1
