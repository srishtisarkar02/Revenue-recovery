import json
from app.database import SessionLocal
from app.models import RecoveryCase
from app.ai.rag import RecoveryRAG
from app.orchestrator.recovery import RecoveryOrchestrator
from app.simulator.benchmark import run_batch_benchmark
from app.simulator.scenarios import load_demo_scenarios
from app.simulator.shared import simulator
from app.services.recovery import create_recovery_case

def test_pipeline():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("1. TESTING RAG KNOWLEDGE SEEDING & SEARCH")
        print("=" * 60)
        rag = RecoveryRAG(db)
        seeded = rag.seed_knowledge()
        print(f"Seeded knowledge items: {seeded}")

        search_res = rag.search("payment gateway timeout", limit=2)
        print(f"RAG Search query 'payment gateway timeout':")
        for item in search_res:
            print(f" - [{item['title']}] (Similarity: {item['similarity']}) -> Action: {item['recommended_action']}")

        print("\n" + "=" * 60)
        print("2. TESTING SINGLE-CASE ORCHESTRATION (TRANSIENT NETWORK)")
        print("=" * 60)
        import uuid
        test_net_pay_id = f"sim_net_{uuid.uuid4().hex[:6]}"
        simulator.add_payment(
            payment_id=test_net_pay_id,
            customer_id="sim_customer_test",
            amount=1000,
            currency="INR",
            failure_reason="network_error",
        )
        case_network = create_recovery_case(
            db=db,
            customer_id="sim_customer_test",
            payment_id=test_net_pay_id,
            amount=1000,
        )
        orchestrator = RecoveryOrchestrator(db=db, simulator=simulator)
        res_network = orchestrator.run(case_network)
        if "ai_decision" in res_network:
            print(f"AI Decision: {res_network['ai_decision']['decision']} (Confidence: {res_network['ai_decision']['confidence']})")
            print(f"Policy Allowed: {res_network['policy']['allowed']}")
            print(f"Action Executed: {res_network['action']}")
            print(f"Verification: {res_network['verification']}")
        else:
            print(f"Stopping Rule Activated: {res_network.get('reason')}")
        print(f"Final Status: {res_network['final_status']}")

        print("\n" + "=" * 60)
        print("3. TESTING SINGLE-CASE ORCHESTRATION (FRAUD RISK BLOCK)")
        print("=" * 60)
        test_fraud_pay_id = f"sim_fraud_{uuid.uuid4().hex[:6]}"
        simulator.add_payment(
            payment_id=test_fraud_pay_id,
            customer_id="sim_customer_fraud",
            amount=50000,
            currency="INR",
            failure_reason="suspected_fraud",
        )
        case_fraud = create_recovery_case(
            db=db,
            customer_id="sim_customer_fraud",
            payment_id=test_fraud_pay_id,
            amount=50000,
        )
        res_fraud = orchestrator.run(case_fraud)
        if "ai_decision" in res_fraud:
            print(f"AI Decision: {res_fraud['ai_decision']['decision']}")
            print(f"Policy Allowed: {res_fraud['policy']['allowed']}")
            print(f"Violated Rules: {res_fraud['policy'].get('violated_rules', [])}")
        else:
            print(f"Policy Block: {res_fraud.get('reason')}")
        print(f"Final Status: {res_fraud['final_status']}")

        print("\n" + "=" * 60)
        print("4. RUNNING BATCH BENCHMARK (50 CASES - AI VS BASELINE)")
        print("=" * 60)
        benchmark_results = run_batch_benchmark(db=db, count=50)
        summary = benchmark_results["summary"]
        print(f"Total Evaluated Cases: {summary['total_evaluated_cases']}")
        print(f"Total Revenue At Risk: INR {summary['total_revenue_at_risk_inr']:,}")
        print(f"AI Money Recovered:    INR {summary['ai_money_recovered_inr']:,} ({summary['ai_recovery_rate_percent']}%)")
        print(f"Baseline Recovered:    INR {summary['baseline_money_recovered_inr']:,} ({summary['baseline_recovery_rate_percent']}%)")
        print(f"Net Revenue Lift:      INR {summary['net_revenue_lift_inr']:,}")
        print(f"Fraud Loss Prevented:  INR {summary['fraud_losses_prevented_by_ai_inr']:,}")
        print(f"Unsafe Actions Blocked: {summary['unsafe_actions_prevented']}")

        print("\n" + "=" * 60)
        print("PIPELINE TEST PASSED SUCCESSFULLY!")
        print("=" * 60)
    finally:
        db.close()

if __name__ == "__main__":
    test_pipeline()
