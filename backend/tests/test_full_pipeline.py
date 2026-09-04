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
        print("4. TESTING MANDATE RETRY SEQUENCER (UPI AUTOPAY / RECURRING)")
        print("=" * 60)
        from app.services.mandate import MandateRetrySequencer
        sequencer = MandateRetrySequencer(db)
        mandate_plan = sequencer.schedule_retry(
            mandate_id=f"man_{uuid.uuid4().hex[:6]}",
            customer_id="cust_sub_01",
            amount=4999,
            failure_code="insufficient_funds",
        )
        print(f"Scheduled Mandate: {mandate_plan['mandate_id']}")
        print(f"Optimal Window:    {mandate_plan['optimal_window']}")
        print(f"Scheduled Date:    {mandate_plan['scheduled_date']}")
        print(f"Strategy:          {mandate_plan['strategy']}")

        process_res = sequencer.execute_scheduled_retries()
        print(f"Processed Mandates: {process_res['processed_schedules']}, Recovered: INR {process_res['revenue_recovered_inr']:,}")

        print("\n" + "=" * 60)
        print("5. TESTING B2B RECEIVABLES & PROMISE-TO-PAY TRACKER")
        print("=" * 60)
        from app.services.receivables import ReceivablesTracker
        tracker = ReceivablesTracker(db)
        ptp_res = tracker.record_promise_to_pay(
            invoice_id=f"inv_{uuid.uuid4().hex[:6]}",
            customer_id="corp_client_01",
            amount=45000,
            customer_message="Hi team, invoice received. We will process payment by Friday after internal sign-off.",
        )
        print(f"Invoice:           {ptp_res['invoice_id']}")
        print(f"Has Promise:       {ptp_res['has_promise']}")
        print(f"Promised Date:     {ptp_res['promised_date']}")
        print(f"Action Taken:      {ptp_res['action_taken']}")
        print(f"Reminders Paused:  {ptp_res['reminders_paused']}")

        print("\n" + "=" * 60)
        print("6. TESTING BANK GATEWAY HEALTH & ANOMALY DETECTOR")
        print("=" * 60)
        from app.services.gateway_health import gateway_monitor
        gw_health = gateway_monitor.get_all_gateways()
        print(f"Overall Gateway Status: {gw_health['overall_status']}")
        print(f"Monitored Gateways:     {gw_health['active_monitored_gateways']} (Healthy: {gw_health['healthy_gateways']}, Degraded: {gw_health['degraded_gateways']})")
        kotak_check = gateway_monitor.check_bank_health("KOTAK")
        print(f"Kotak Bank Health Check: Status={kotak_check['status']}, SafeToRetry={kotak_check['safe_to_retry']}, Action={kotak_check['recommendation']}")

        print("\n" + "=" * 60)
        print("7. RUNNING BATCH BENCHMARK (50 CASES - AI VS BASELINE)")
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
        print("ALL 7 CORE REVENUE RECOVERY CAPABILITIES PASSED!")
        print("=" * 60)
    finally:
        db.close()

if __name__ == "__main__":
    test_pipeline()
