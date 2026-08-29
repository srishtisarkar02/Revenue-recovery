from app.simulator.payments import PaymentSimulator
from app.simulator.scenarios import load_demo_scenarios


class SimulationEngine:

    def __init__(self) -> None:
        self.simulator = PaymentSimulator()

    def setup_demo(self) -> None:
        load_demo_scenarios(self.simulator)

    def get_results(self) -> list[dict]:

        results = []

        for payment_id in self.simulator.payments:
            results.append(
                self.simulator.get_payment(payment_id)
            )

        return results