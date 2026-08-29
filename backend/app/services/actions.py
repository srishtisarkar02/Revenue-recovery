def send_recovery_message(customer_id: str, payment_id: str):
    return {
        "action": "send_recovery_message",
        "customer_id": customer_id,
        "payment_id": payment_id,
        "message": "Please retry your payment or use another payment method.",
        "status": "sent",
    }