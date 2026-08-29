from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.simulator.benchmark import run_batch_benchmark
from app.simulator.scenarios import load_demo_scenarios
from app.simulator.shared import simulator

router = APIRouter(
    prefix="/simulator",
    tags=["Simulator"],
)


@router.post("/setup")
def setup_simulation():
    load_demo_scenarios(simulator)
    return {
        "status": "ready",
        "count": len(simulator.payments),
    }


@router.get("/payments")
def get_simulated_payments():
    return {
        "payments": [
            simulator.get_payment(payment_id)
            for payment_id in simulator.payments
        ],
        "count": len(simulator.payments),
    }


@router.post("/benchmark")
@router.post("/run-batch")
def execute_benchmark(
    count: int = Query(default=50, ge=5, le=100),
    db: Session = Depends(get_db),
):
    """
    Executes a complete batch recovery simulation across N failed payments.
    Evaluates AI Agent vs. Naive Baseline and calculates measured ₹ recovered.
    """
    return run_batch_benchmark(db=db, count=count)