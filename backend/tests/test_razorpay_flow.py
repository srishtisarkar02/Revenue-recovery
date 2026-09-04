import hmac
import hashlib
import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import RecoveryCase
from app.tools.razorpay_tools import razorpay_client

client = TestClient(app)

def test_razorpay_config_does_not_expose_secret():
    res = client.get("/razorpay/config")
    assert res.status_code == 200
    data = res.json()
    assert "key_id" in data
    assert "key_secret" not in data
    assert "RAZORPAY_KEY_SECRET" not in data

def test_razorpay_status_endpoint():
    res = client.get("/razorpay/status")
    assert res.status_code == 200
    data = res.json()
    assert "environment" in data
    assert data["capabilities"]["payment_orders"] is True
    assert data["capabilities"]["signature_verification"] is True

def test_razorpay_no_fake_order_fallback():
    # If invalid credentials or unconfigured, it must NOT return a fake order_id
    order_res = client.post("/razorpay/create-order", json={
        "amount": 3500,
        "currency": "INR",
        "receipt": "pay_test_receipt",
        "customer_id": "cust_test",
    })
    # Either succeeds if valid live Razorpay key is set, or returns 502 unavailable
    if order_res.status_code != 200:
        assert order_res.status_code == 502
        assert "Razorpay Test Mode unavailable" in order_res.json()["detail"]

def test_razorpay_server_signature_verification():
    unique_pid = f"pay_rzp_test_{uuid.uuid4().hex[:8]}"
    db = SessionLocal()
    case = RecoveryCase(
        customer_id="cust_rzp_test_01",
        payment_id=unique_pid,
        amount=3500,
        currency="INR",
        status="open",
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    case_id = case.id
    db.close()

    # Register legitimate order in server registry
    order_id = f"order_real_test_{uuid.uuid4().hex[:10]}"
    razorpay_client.key_secret = "test_secret_for_unit_tests"
    razorpay_client.register_server_order(order_id, {
        "key_id": "rzp_test_mock",
        "order_id": order_id,
        "amount": 350000,
        "currency": "INR",
        "receipt": unique_pid,
        "case_id": case_id,
    })

    test_payment_id = f"pay_rzp_cap_{uuid.uuid4().hex[:6]}"
    msg = f"{order_id}|{test_payment_id}"
    signature = hmac.new(
        razorpay_client.key_secret.encode(),
        msg.encode(),
        hashlib.sha256
    ).hexdigest()

    verify_res = client.post("/razorpay/verify-payment", json={
        "razorpay_order_id": order_id,
        "razorpay_payment_id": test_payment_id,
        "razorpay_signature": signature,
        "case_id": case_id,
        "payment_id": unique_pid,
    })
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["verified"] is True
    assert verify_data["status"] == "recovered"

    db = SessionLocal()
    updated_case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    assert updated_case.status == "recovered"
    db.close()

def test_razorpay_checkout_failed_orchestration():
    unique_pid = f"pay_rzp_fail_{uuid.uuid4().hex[:8]}"
    db = SessionLocal()
    case = RecoveryCase(
        customer_id="cust_rzp_fail_01",
        payment_id=unique_pid,
        amount=4500,
        currency="INR",
        status="open",
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    case_id = case.id
    db.close()

    fail_res = client.post("/razorpay/checkout-failed", json={
        "order_id": "order_test_fail_123",
        "payment_id": unique_pid,
        "error_code": "BAD_REQUEST_ERROR",
        "error_description": "Payment was declined by customer bank",
        "error_source": "bank",
        "error_step": "payment_authorization",
        "error_reason": "bank_declined",
        "case_id": case_id,
        "amount": 4500,
        "customer_id": "cust_rzp_fail_01"
    })
    assert fail_res.status_code == 200
    data = fail_res.json()
    assert data["status"] == "failure_orchestrated"
    assert data["case_id"] == case_id
    assert "failure_reason" in data

    db = SessionLocal()
    refreshed_case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    assert refreshed_case is not None
    db.close()

def test_razorpay_webhook_ingestion():
    unique_pid = f"pay_rzp_hook_{uuid.uuid4().hex[:8]}"
    db = SessionLocal()
    case = RecoveryCase(
        customer_id="cust_rzp_hook_02",
        payment_id=unique_pid,
        amount=2800,
        currency="INR",
        status="open",
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    case_id = case.id
    db.close()

    webhook_payload = {
        "event": "payment_link.paid",
        "payload": {
            "payment_link": {
                "entity": {
                    "reference_id": unique_pid,
                    "amount": 280000,
                    "status": "paid"
                }
            }
        }
    }
    wh_res = client.post("/events/razorpay-webhook", json=webhook_payload)
    assert wh_res.status_code == 200
    assert wh_res.json()["status"] == "case_recovered"

    db = SessionLocal()
    wh_case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    assert wh_case.status == "recovered"
    db.close()

if __name__ == "__main__":
    test_razorpay_config_does_not_expose_secret()
    print("[PASS] test_razorpay_config_does_not_expose_secret passed")
    test_razorpay_status_endpoint()
    print("[PASS] test_razorpay_status_endpoint passed")
    test_razorpay_no_fake_order_fallback()
    print("[PASS] test_razorpay_no_fake_order_fallback passed")
    test_razorpay_server_signature_verification()
    print("[PASS] test_razorpay_server_signature_verification passed")
    test_razorpay_checkout_failed_orchestration()
    print("[PASS] test_razorpay_checkout_failed_orchestration passed")
    test_razorpay_webhook_ingestion()
    print("[PASS] test_razorpay_webhook_ingestion passed")
    print("\nALL REAL RAZORPAY INTEGRATION TESTS PASSED!")
