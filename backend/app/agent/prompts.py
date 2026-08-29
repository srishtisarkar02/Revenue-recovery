SYSTEM_PROMPT = """
You are an expert AI Revenue Recovery Agent designed for enterprise payment systems like Razorpay.
Your mission is to analyze payment failures, diagnose the root cause, and select the safest, highest-ROI recovery intervention to win back lost revenue.

Core Operational Rules:
1. Never retry payments with fraud flags, chargeback risks, or stolen card signals. Choose 'escalate'.
2. For transient infrastructure errors (gateway timeouts, network disconnects), recommend 'retry_payment'.
3. For customer-side declines (insufficient funds, bank decline, expired cards), recommend 'send_recovery_message' with actionable guidance.
4. For high-value transactions (>= 25,000 INR) with any risk or ambiguity, prefer 'escalate'.
5. If the maximum retry budget (2) is reached, choose 'escalate'.
6. If the payment is already verified as recovered, choose 'no_action'.

Provide an explainable reason, confidence score (0.0 - 1.0), tailored customer_message (if communicating), and clear next_step.
"""


def build_case_prompt(
    context,
    recovery_knowledge=None,
    knowledge_context: str | None = None,
    history_context: str | None = None,
) -> str:
    knowledge_text = ""
    if knowledge_context:
        knowledge_text = f"\n\n{knowledge_context}\n"
    elif recovery_knowledge:
        knowledge_text = "\n\nRELEVANT RECOVERY POLICIES:\n"
        for item in recovery_knowledge:
            knowledge_text += f"""
Policy: {item.get("title", "")}
Failure reason: {item.get("failure_reason", "")}
Recommended action: {item.get("recommended_action", "")}
Policy guidance: {item.get("content", "")}
Similarity: {item.get("similarity", 0)}
---
"""

    history_text = f"\n\n{history_context}\n" if history_context else ""

    return f"""
PAYMENT RECOVERY CASE

Payment ID: {context.payment_id}
Customer ID: {context.customer_id}
Amount: {context.amount} {context.currency}

Failure Reason:
{context.failure_reason}

Customer Profile:
- Previous Payments: {context.previous_payment_count}
- Previous Failed Payments: {context.previous_failed_payment_count}
- Previous Recovery Attempts: {context.previous_recovery_attempts}
- Previous Retry Attempts: {context.previous_retry_attempts}
- Previous Successful Recoveries: {context.previous_successful_recoveries}
- Customer Value Tier: {context.customer_value}
- Risk Flags: {context.risk_flags}
{history_text}
{knowledge_text}

Using the case context, historical attempts, and retrieved RAG recovery policies, decide the most appropriate action:
- retry_payment
- send_recovery_message
- escalate
- no_action

Return ONLY the required structured JSON response.
"""