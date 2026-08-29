from app.tools.razorpay_tools import razorpay_client


def send_recovery_message(
    customer_id: str,
    payment_id: str,
    message: str,
    amount: int = 1000,
    currency: str = "INR",
) -> dict:
    """
    Multi-channel customer recovery tool with 1-Click Razorpay Payment Link.
    Attaches a secure payment link so the customer can instantly recover.
    """
    payment_link = razorpay_client.create_payment_link(
        amount=amount,
        currency=currency,
        customer_id=customer_id,
        payment_id=payment_id,
        description=f"Recovery for payment {payment_id}",
    )

    full_message = message.strip()
    if payment_link["short_url"] not in full_message:
        full_message += f" Instant recovery link: {payment_link['short_url']}"

    return {
        "tool": "send_recovery_message",
        "customer_id": customer_id,
        "payment_id": payment_id,
        "message": full_message,
        "payment_link_url": payment_link["short_url"],
        "payment_link_id": payment_link["id"],
        "channel": "whatsapp_and_sms",
        "status": "sent",
    }