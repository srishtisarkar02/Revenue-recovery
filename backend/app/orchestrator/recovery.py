from sqlalchemy.orm import Session

from app.agent.agent import get_agent
from app.agent.schemas import AgentContext

from app.ai.rag import RecoveryRAG

from app.models import RecoveryCase

from app.orchestrator.audit import (
    AgentActionLog,
)

from app.policy.evaluator import (
    PolicyContext,
    evaluate_policy,
)
from app.policy.rules import BLOCKED_FAILURE_REASONS

from app.services.context import (
    build_case_history,
    format_case_history,
)

from app.simulator.payments import (
    PaymentSimulator,
)

from app.tools.retry_payment import (
    retry_payment,
)

from app.tools.send_message import (
    send_recovery_message,
)

from app.tools.escalate import (
    escalate_case,
)

from app.tools.verify_payment import (
    verify_payment,
)


class RecoveryOrchestrator:

    def __init__(
        self,
        db: Session,
        simulator: PaymentSimulator,
    ):
        self.db = db
        self.simulator = simulator
        self.agent = get_agent()
        self.rag = RecoveryRAG(db)

    def run(
        self,
        case: RecoveryCase,
    ) -> dict:

        # --------------------------------------------------
        # STOPPING RULE — already recovered
        # --------------------------------------------------

        if case.status == "recovered":

            return {
                "case_id": case.id,
                "stopped": True,
                "reason": (
                    "Case is already recovered. "
                    "No further action permitted."
                ),
                "final_status": "recovered",
            }

        # --------------------------------------------------
        # 1. Payment state
        # --------------------------------------------------

        payment = self.simulator.get_payment(
            case.payment_id
        )

        failure_reason = payment[
            "failure_reason"
        ]

        # --------------------------------------------------
        # 2. Persistent case memory
        # --------------------------------------------------

        history = build_case_history(
            self.db,
            case,
        )

        history_context = (
            format_case_history(
                history
            )
        )

        retry_count = max(
            payment.get(
                "retry_count",
                0,
            ),
            history[
                "previous_retry_attempts"
            ],
        )

        recovery_attempts = history[
            "previous_recovery_attempts"
        ]

        # --------------------------------------------------
        # 3. Retrieve relevant knowledge
        # --------------------------------------------------

        knowledge_context = (
            self.rag.build_recovery_context(
                failure_reason=(
                    failure_reason
                ),
                amount=case.amount,
                currency=case.currency,
                previous_retry_attempts=(
                    retry_count
                ),
                previous_recovery_attempts=(
                    recovery_attempts
                ),
                risk_flags=[],
            )
        )

        # --------------------------------------------------
        # 4. Construct Gemini context
        # --------------------------------------------------

        context = AgentContext(
            payment_id=case.payment_id,
            customer_id=case.customer_id,
            amount=case.amount,
            currency=case.currency,
            failure_reason=(
                failure_reason
            ),
            previous_payment_count=0,
            previous_failed_payment_count=0,
            previous_recovery_attempts=(
                recovery_attempts
            ),
            previous_retry_attempts=(
                retry_count
            ),
            previous_successful_recoveries=(
                history[
                    "previous_successful_recoveries"
                ]
            ),
            customer_value="standard",
            risk_flags=[],
        )

        # --------------------------------------------------
        # 5. Gemini + RAG + memory
        # --------------------------------------------------

        ai_decision = self.agent.decide(
            context,
            knowledge_context=(
                knowledge_context
            ),
            history_context=(
                history_context
            ),
        )

        failure_category = payment.get("failure_category") or failure_reason
        risk_flags = []
        if failure_category in BLOCKED_FAILURE_REASONS or any(b in failure_reason.lower() for b in BLOCKED_FAILURE_REASONS):
            risk_flags.append(failure_category if failure_category in BLOCKED_FAILURE_REASONS else "suspected_fraud")

        policy_result = evaluate_policy(
            decision=ai_decision.decision,
            context=PolicyContext(
                amount=case.amount,
                failure_reason=failure_category,
                previous_recovery_attempts=recovery_attempts,
                previous_retry_attempts=retry_count,
                risk_flags=risk_flags,
            ),
        )


        # --------------------------------------------------
        # 7. Policy rejection
        # --------------------------------------------------

        if not policy_result.allowed:

            case.status = "escalated"

            blocked_record = (
                AgentActionLog(
                    case_id=case.id,
                    action="policy_blocked",
                    details=(
                        f"AI recommendation "
                        f"'{ai_decision.decision}' "
                        f"blocked. "
                        f"Violations: "
                        f"{policy_result.violated_rules}"
                    ),
                )
            )

            self.db.add(
                blocked_record
            )

            self.db.commit()

            return {
                "case_id": case.id,
                "rag_context": (
                    knowledge_context
                ),
                "case_memory": (
                    history_context
                ),
                "ai_decision": (
                    ai_decision.model_dump()
                ),
                "policy": {
                    "allowed": False,
                    "decision": (
                        policy_result.decision
                    ),
                    "reason": (
                        policy_result.reason
                    ),
                    "violated_rules": (
                        policy_result
                        .violated_rules
                    ),
                },
                "action": {
                    "tool": "policy_block",
                    "status": "blocked",
                },
                "verification": {
                    "verified": False,
                },
                "final_status": (
                    case.status
                ),
            }

        # --------------------------------------------------
        # 8. Execute approved intervention
        # --------------------------------------------------

        if (
            ai_decision.decision
            == "retry_payment"
        ):

            action_result = (
                retry_payment(
                    simulator=(
                        self.simulator
                    ),
                    payment_id=(
                        case.payment_id
                    ),
                )
            )

        elif (
            ai_decision.decision
            == "send_recovery_message"
        ):

            action_result = (
                send_recovery_message(
                    customer_id=(
                        case.customer_id
                    ),
                    payment_id=(
                        case.payment_id
                    ),
                    message=(
                        ai_decision
                        .customer_message
                    ),
                    amount=case.amount,
                    currency=case.currency,
                )
            )

        elif (
            ai_decision.decision
            == "escalate"
        ):

            action_result = (
                escalate_case(
                    case_id=case.id,
                    reason=(
                        ai_decision.reason
                    ),
                )
            )

            case.status = "escalated"

        else:

            action_result = {
                "tool": "no_action",
                "status": "no_action",
            }

        # --------------------------------------------------
        # 9. Persist action trace
        # --------------------------------------------------

        action_record = (
            AgentActionLog(
                case_id=case.id,
                action=(
                    ai_decision.decision
                ),
                details=str(
                    action_result
                ),
            )
        )

        self.db.add(
            action_record
        )

        # --------------------------------------------------
        # 10. Independent verification
        # --------------------------------------------------

        verification = verify_payment(
            simulator=self.simulator,
            payment_id=case.payment_id,
        )

        if verification["verified"]:

            case.status = "recovered"

            verification_record = (
                AgentActionLog(
                    case_id=case.id,
                    action=(
                        "payment_verified"
                    ),
                    details=(
                        "Payment recovery "
                        "successfully verified."
                    ),
                )
            )

            self.db.add(
                verification_record
            )

        elif (
            ai_decision.decision
            == "escalate"
        ):
            case.status = "escalated"

        else:
            case.status = "open"

        self.db.commit()

        # --------------------------------------------------
        # 11. Complete 7-Step Autonomous Recovery Trace
        # --------------------------------------------------

        return {
            "case_id": case.id,
            "status": case.status,
            "final_status": case.status,
            "seven_steps": {
                "step_1_detect": {
                    "payment_id": case.payment_id,
                    "customer_id": case.customer_id,
                    "amount": case.amount,
                    "currency": case.currency,
                    "failure_reason": failure_reason,
                },
                "step_2_diagnose": {
                    "retrieved_policies": knowledge_context,
                    "case_memory": history_context,
                },
                "step_3_decide": ai_decision.model_dump(),
                "step_4_policy_check": {
                    "allowed": policy_result.allowed,
                    "decision": policy_result.decision,
                    "reason": policy_result.reason,
                    "violated_rules": policy_result.violated_rules,
                },
                "step_5_act": action_result,
                "step_6_verify": verification,
                "step_7_recover": {
                    "final_status": case.status,
                    "recovered": case.status == "recovered",
                    "recovered_amount_inr": case.amount if case.status == "recovered" else 0,
                },
            },
            "retrieved_knowledge": knowledge_context,
            "case_memory": history_context,
            "ai_decision": ai_decision.model_dump(),
            "policy": {
                "allowed": policy_result.allowed,
                "decision": policy_result.decision,
                "reason": policy_result.reason,
                "violated_rules": policy_result.violated_rules,
            },
            "action": action_result,
            "verification": verification,
            "customer_name": payment.get("customer_name"),
            "customer_email": payment.get("customer_email"),
            "failure_category": failure_category,
            "failure_reason": failure_reason,
        }
