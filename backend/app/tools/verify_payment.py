from app.simulator.payments import PaymentSimulator


def verify_payment(
    simulator: PaymentSimulator,
    payment_id: str,
) -> dict:
    """
    Verify the actual payment state.

    This is deliberately separate from retry_payment.
    The agent must never assume that an action succeeded.
    """

    payment = simulator.get_payment(payment_id)

    return {
        "tool": "verify_payment",
        "payment_id": payment_id,
        "status": payment["status"],
        "verified": payment["status"] == "recovered",
    }