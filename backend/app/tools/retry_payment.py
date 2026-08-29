from app.simulator.payments import PaymentSimulator

def retry_payment(
    simulator: PaymentSimulator,
    payment_id: str,
) -> dict:
    """
    Ask the payment provider/simulator to retry a payment.

    The tool does not decide whether retrying is safe.
    Policy must approve the action before this tool is called.
    """

    result = simulator.retry_payment(payment_id)

    return {
        "tool": "retry_payment",
        **result,
    }