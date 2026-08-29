from app.simulator.payments import PaymentSimulator


def load_demo_scenarios(
    simulator: PaymentSimulator,
) -> None:

    simulator.add_payment(
        payment_id="sim_network_001",
        customer_id="sim_customer_001",
        amount=1000,
        currency="INR",
        failure_reason="network_error",
    )

    simulator.add_payment(
        payment_id="sim_funds_001",
        customer_id="sim_customer_002",
        amount=1500,
        currency="INR",
        failure_reason="insufficient_funds",
    )

    simulator.add_payment(
        payment_id="sim_timeout_001",
        customer_id="sim_customer_003",
        amount=2500,
        currency="INR",
        failure_reason="timeout",
    )

    simulator.add_payment(
        payment_id="sim_fraud_001",
        customer_id="sim_customer_004",
        amount=50000,
        currency="INR",
        failure_reason="suspected_fraud",
    )

    simulator.add_payment(
        payment_id="sim_declined_001",
        customer_id="sim_customer_005",
        amount=3000,
        currency="INR",
        failure_reason="bank_declined",
    )