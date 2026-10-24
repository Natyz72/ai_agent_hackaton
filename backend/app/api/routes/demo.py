from fastapi import APIRouter
from app.schemas.common import DemoMessage, DemoMessagesResponse

router = APIRouter()

DEMO_MESSAGES: list[DemoMessage] = [
    DemoMessage(
        id="DEMO-01",
        title="Credential Harvest via Deceptive Subdomain",
        category="credential_phishing",
        description="Urgent IT password expiration notice directing to a spoofed subdomain",
        expected_risk="high",
        message=(
            "URGENT IT SECURITY NOTICE: Your corporate account password will expire in 2 hours. "
            "Failure to update credentials immediately will result in permanent account suspension. "
            "Click here to verify and update your credentials: http://login.company.example.phishy.example/auth/reset"
        ),
    ),
    DemoMessage(
        id="DEMO-02",
        title="Payment Wire Fraud via Direct IP URL",
        category="financial_fraud",
        description="Executive wire transfer notice directing to a raw IP address destination",
        expected_risk="high",
        message=(
            "URGENT: Executive payment wire instructions have been updated for vendor invoice #98124. "
            "Please re-route the pending transfer immediately to avoid penalty charges. "
            "Confirm the transaction details at: http://192.168.1.100/invoices/wire_update.php"
        ),
    ),
    DemoMessage(
        id="DEMO-03",
        title="Host Spoof via User-Info Trick (@)",
        category="url_spoofing",
        description="Security alert using '@' symbol to mask malicious host behind a trusted domain name",
        expected_risk="high",
        message=(
            "Security Alert: Unauthorized sign-in detected on your corporate account from an unrecognized IP. "
            "If this was not you, verify your identity immediately: "
            "http://trusted.example@suspicious.example/session/verify"
        ),
    ),
    DemoMessage(
        id="DEMO-04",
        title="Ambiguous / Incomplete Message",
        category="ambiguous_clarification",
        description="Vague request with missing indicators (demonstrates clarification workflow)",
        expected_risk="low",
        message=(
            "Hey team, please review the file from yesterday whenever you have a chance."
        ),
    ),
    DemoMessage(
        id="DEMO-05",
        title="Benign Corporate Announcement",
        category="benign_routine",
        description="Legitimate internal notice from trusted domain (absence of flags != proof of safety)",
        expected_risk="low",
        message=(
            "Hello team, this is a reminder about our monthly lunch-and-learn tomorrow at 12:00 PM "
            "in the main conference room. Details are available on the intranet at https://company.example/events."
        ),
    ),
]


@router.get("/demo-messages", response_model=DemoMessagesResponse)
async def get_demo_messages():
    """
    GET /api/demo-messages
    Returns the 5 fictitious demo messages designed for hackathon demonstration.
    """
    return DemoMessagesResponse(messages=DEMO_MESSAGES)
