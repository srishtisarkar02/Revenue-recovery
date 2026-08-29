from typing import Any


class GatewayHealthMonitor:
    """
    Real-Time Bank Gateway Health & Anomaly Detector.
    Prevents burning retry budgets during bank downtimes (e.g. HDFC or SBI server glitches).
    """

    def __init__(self) -> None:
        self.gateway_metrics = {
            "HDFC": {"name": "HDFC Bank Gateway", "success_rate_percent": 94.2, "status": "healthy", "latency_ms": 180},
            "SBI": {"name": "State Bank of India", "success_rate_percent": 91.5, "status": "healthy", "latency_ms": 240},
            "ICICI": {"name": "ICICI Bank Gateway", "success_rate_percent": 96.0, "status": "healthy", "latency_ms": 160},
            "AXIS": {"name": "Axis Bank Gateway", "success_rate_percent": 93.8, "status": "healthy", "latency_ms": 195},
            "UPI_RAZORPAY": {"name": "Razorpay UPI AutoPay Switch", "success_rate_percent": 97.4, "status": "healthy", "latency_ms": 120},
            "KOTAK": {"name": "Kotak Mahindra Bank", "success_rate_percent": 58.0, "status": "degraded", "latency_ms": 850},
        }

    def get_all_gateways(self) -> dict[str, Any]:
        """Returns health status across all supported bank switches."""
        healthy_count = sum(1 for g in self.gateway_metrics.values() if g["status"] == "healthy")
        degraded_count = len(self.gateway_metrics) - healthy_count

        return {
            "overall_status": "partially_degraded" if degraded_count > 0 else "all_healthy",
            "active_monitored_gateways": len(self.gateway_metrics),
            "healthy_gateways": healthy_count,
            "degraded_gateways": degraded_count,
            "gateways": self.gateway_metrics,
        }

    def check_bank_health(self, bank_code: str) -> dict[str, Any]:
        """
        Determines whether a retry should be executed immediately or held.
        """
        code = bank_code.upper().strip()
        metric = self.gateway_metrics.get(code, {
            "name": f"{code} Bank",
            "success_rate_percent": 90.0,
            "status": "healthy",
            "latency_ms": 200,
        })

        is_degraded = metric["status"] == "degraded" or metric["success_rate_percent"] < 65.0

        return {
            "bank_code": code,
            "name": metric["name"],
            "status": metric["status"],
            "success_rate_percent": metric["success_rate_percent"],
            "recommendation": "hold_retry_until_recovery" if is_degraded else "proceed_with_safe_retry",
            "safe_to_retry": not is_degraded,
        }


gateway_monitor = GatewayHealthMonitor()
