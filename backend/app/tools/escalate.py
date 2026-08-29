def escalate_case(
    case_id: int | str,
    reason: str,
) -> dict:
    """
    Escalate a recovery case to human operations.
    """

    return {
        "tool": "escalate",
        "case_id": case_id,
        "status": "escalated",
        "reason": reason,
    }