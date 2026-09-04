from fastapi import APIRouter
from app.services.gateway_health import gateway_monitor

router = APIRouter(
    prefix="/gateway",
    tags=["Bank Gateway Health"],
)


@router.get("/health")
def get_all_gateway_health():
    """
    Returns real-time health and degradation status across all monitored bank gateways.
    """
    return gateway_monitor.get_all_gateways()


@router.get("/check/{bank_code}")
def check_bank_health(bank_code: str):
    """
    Checks specific bank gateway health and advises whether retries should proceed or be held.
    """
    return gateway_monitor.check_bank_health(bank_code)
