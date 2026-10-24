import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_get_demo_messages():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/demo-messages")
        assert resp.status_code == 200
        data = resp.json()
        assert "messages" in data
        messages = data["messages"]
        # Hackathon requires exactly five fictitious messages
        assert len(messages) == 5

        categories = {m["category"] for m in messages}
        assert "credential_phishing" in categories
        assert "financial_fraud" in categories
        assert "url_spoofing" in categories
        assert "ambiguous_clarification" in categories
        assert "benign_routine" in categories


@pytest.mark.asyncio
async def test_demo_messages_can_be_investigated():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        demo_resp = await client.get("/api/demo-messages")
        messages = demo_resp.json()["messages"]

        # Run first demo message through investigate endpoint
        first_msg = messages[0]["message"]
        inv_resp = await client.post("/api/investigate", json={"message": first_msg})
        assert inv_resp.status_code == 200
        inv_data = inv_resp.json()
        assert inv_data["status"] == "ok"
        assert inv_data["risk"]["level"] == "high"
        assert len(inv_data["findings"]) > 0
