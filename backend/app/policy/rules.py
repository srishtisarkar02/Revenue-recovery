MAX_RETRY_ATTEMPTS = 2
MAX_RECOVERY_MESSAGE_ATTEMPTS = 3

HIGH_VALUE_AMOUNT = 25_000

BLOCKED_FAILURE_REASONS = {
    "fraud",
    "suspected_fraud",
    "chargeback",
    "stolen_card",
}

TRANSIENT_FAILURE_REASONS = {
    "network_error",
    "timeout",
    "gateway_timeout",
    "temporary_failure",
    "connection_error",
}

MESSAGE_FAILURE_REASONS = {
    "insufficient_funds",
    "bank_declined",
    "expired_card",
    "payment_failed",
}
