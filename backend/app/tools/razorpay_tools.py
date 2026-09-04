import hashlib
import hmac
import os
import uuid
from typing import Any
from pathlib import Path
from dotenv import load_dotenv

# Robustly load project-root .env based on __file__
_project_root_env = Path(__file__).resolve().parents[3] / ".env"
if _project_root_env.exists():
    load_dotenv(_project_root_env, override=True)
else:
    load_dotenv()

# Use httpx if available, fallback to requests
try:
    import httpx
    _HTTP_CLIENT = "httpx"
except ImportError:
    import requests
    _HTTP_CLIENT = "requests"


class RazorpayClient:
    """
    Official Razorpay REST API Client for AI Revenue Recovery.
    Uses direct REST endpoints:
      - POST https://api.razorpay.com/v1/orders
      - POST https://api.razorpay.com/v1/payment_links
    with HTTP Basic Auth (RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET).
    Stores created order IDs server-side for secure signature validation.
    NEVER generates fake fallback order IDs or fake payment links.
    """

    BASE_URL = "https://api.razorpay.com/v1"

    def __init__(self) -> None:
        self.key_id = os.getenv("RAZORPAY_KEY_ID", "")
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
        self.webhook_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")
        
        # Server-side registry of created orders: order_id -> order details
        self._server_orders: dict[str, dict[str, Any]] = {}
        self._receipt_to_order: dict[str, str] = {}

    def _http_post(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """Helper to make authenticated HTTP POST request to Razorpay REST API. Raises on failure."""
        if not self.key_id or not self.key_secret:
            raise RuntimeError(
                "RAZORPAY_KEY_ID or RAZORPAY_KEY_SECRET is not configured in .env. "
                "Please configure valid Razorpay Test Mode credentials."
            )

        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        auth = (self.key_id, self.key_secret)

        try:
            if _HTTP_CLIENT == "httpx":
                with httpx.Client(timeout=10.0) as client:
                    resp = client.post(url, json=data, auth=auth)
            else:
                import requests
                resp = requests.post(url, json=data, auth=auth, timeout=10.0)
        except Exception as net_err:
            raise RuntimeError(f"Network error communicating with Razorpay API: {net_err}")

        if resp.status_code in (200, 201):
            return resp.json()

        # Parse Razorpay error response
        err_msg = f"HTTP {resp.status_code}"
        try:
            err_json = resp.json()
            if "error" in err_json:
                err_msg = err_json["error"].get("description") or err_json["error"].get("code") or str(err_json)
            else:
                err_msg = resp.text
        except Exception:
            err_msg = resp.text or err_msg

        raise RuntimeError(f"Razorpay API Error ({resp.status_code}): {err_msg}")

    def create_order(
        self,
        *,
        amount: int,
        currency: str = "INR",
        receipt: str,
        notes: dict[str, str] | None = None,
        case_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Creates a REAL Razorpay Order via REST POST https://api.razorpay.com/v1/orders
        Stores order_id server-side for tamper-proof signature verification.
        Does NOT generate fake fallback order IDs.
        """
        amount_paise = int(amount * 100)
        order_notes = notes or {}
        order_notes["source"] = "RecoveryOS_Control_Plane"
        if case_id:
            order_notes["recovery_case_id"] = str(case_id)

        payload = {
            "amount": amount_paise,
            "currency": currency,
            "receipt": receipt[:40],
            "notes": order_notes,
            "payment_capture": 1,
        }

        # Make real Razorpay REST API call - will raise RuntimeError if failed
        api_res = self._http_post("orders", payload)

        if not api_res or "id" not in api_res:
            raise RuntimeError("Razorpay API returned invalid order response without order ID")

        order_id = api_res["id"]

        order_record = {
            "key_id": self.key_id,
            "order_id": order_id,
            "id": order_id,
            "entity": "order",
            "amount": api_res.get("amount", amount_paise),
            "amount_paid": api_res.get("amount_paid", 0),
            "amount_due": api_res.get("amount_due", amount_paise),
            "currency": currency,
            "receipt": receipt,
            "status": api_res.get("status", "created"),
            "notes": order_notes,
            "case_id": case_id,
        }

        # Store in server registry
        self._server_orders[order_id] = order_record
        self._receipt_to_order[receipt] = order_id

        return order_record

    def get_server_order(self, order_id: str) -> dict[str, Any] | None:
        """Retrieve server-verified order record."""
        return self._server_orders.get(order_id)

    def get_order_by_receipt(self, receipt: str) -> str | None:
        """Find server-stored order ID for a given receipt / payment ID."""
        return self._receipt_to_order.get(receipt)

    def register_server_order(self, order_id: str, details: dict[str, Any]) -> None:
        """Manually register an order in server registry (used by tests/mock environments)."""
        self._server_orders[order_id] = details
        if "receipt" in details:
            self._receipt_to_order[details["receipt"]] = order_id

    def create_payment_link(
        self,
        *,
        amount: int,
        currency: str = "INR",
        customer_id: str,
        payment_id: str,
        description: str = "Invoice Revenue Recovery Link",
    ) -> dict[str, Any]:
        """
        Creates a REAL Razorpay Payment Link via REST POST https://api.razorpay.com/v1/payment_links
        Does NOT generate fake short URLs.
        """
        amount_paise = int(amount * 100)
        payload = {
            "amount": amount_paise,
            "currency": currency,
            "accept_partial": False,
            "reference_id": payment_id,
            "description": description,
            "customer": {
                "name": customer_id.replace("_", " ").title(),
                "email": f"{customer_id}@example.com",
                "contact": "+919876543210",
            },
            "notify": {"sms": True, "email": True, "whatsapp": True},
            "reminder_enable": True,
            "notes": {"recovery_source": "RecoveryOS_AI_Agent", "customer_id": customer_id},
        }

        api_res = self._http_post("payment_links", payload)

        if not api_res or "id" not in api_res:
            raise RuntimeError("Razorpay API returned invalid payment link response without ID")

        return {
            "id": api_res.get("id"),
            "short_url": api_res.get("short_url"),
            "amount": amount,
            "currency": currency,
            "customer_id": customer_id,
            "reference_id": payment_id,
            "description": description,
            "status": api_res.get("status", "created"),
        }

    def verify_payment_signature(
        self,
        *,
        order_id: str,
        payment_id: str,
        signature: str,
    ) -> bool:
        """
        Verifies Razorpay standard checkout payment signature using HMAC-SHA256:
          expected_sig = HMAC-SHA256(order_id + "|" + payment_id, key_secret)
        Uses hmac.compare_digest for constant-time comparison.
        """
        if not signature or not payment_id or not order_id or not self.key_secret:
            return False

        data = f"{order_id}|{payment_id}"
        expected = hmac.new(
            self.key_secret.encode(),
            data.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def verify_webhook_signature(self, body: str, signature: str) -> bool:
        """
        Verifies Razorpay webhook HMAC-SHA256 signature for security:
          expected = HMAC-SHA256(body, webhook_secret)
        """
        if not signature or not self.webhook_secret:
            return False

        expected = hmac.new(
            self.webhook_secret.encode(),
            body.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def get_status(self) -> dict[str, Any]:
        """Returns real-time connection telemetry for Integrations console."""
        is_configured = bool(self.key_id and self.key_secret and self.key_id.startswith("rzp_test_"))
        return {
            "environment": "Test Mode" if not self.key_id.startswith("rzp_live_") else "Live Production",
            "key_id": f"{self.key_id[:8]}••••{self.key_id[-4:]}" if len(self.key_id) > 12 else (self.key_id or "Not Configured"),
            "connected": is_configured,
            "capabilities": {
                "payment_orders": True,
                "payment_links": True,
                "signature_verification": True,
                "webhook_ingestion": True,
            },
            "http_client": _HTTP_CLIENT,
        }


razorpay_client = RazorpayClient()




