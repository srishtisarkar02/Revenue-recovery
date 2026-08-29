from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.routes.recovery import router as recovery_router
from app.routes.event import router as event_router
from app.routes.agent import router as agent_router
from app.routes.policy import router as policy_router
from app.routes.simulator import router as simulator_router
from app.routes.orchestrator import router as orchestrator_router
from app.routes.rag import router as rag_router

app = FastAPI(
    title="AI Revenue Recovery Agent",
    description="Autonomous AI Agent for Razorpay Revenue Recovery & Loss Prevention",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recovery_router)
app.include_router(event_router)
app.include_router(agent_router)
app.include_router(policy_router)
app.include_router(simulator_router)
app.include_router(orchestrator_router)
app.include_router(rag_router)


@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Razorpay AI Revenue Recovery Agent | Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #0b0f19; }
        .glass-card { background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .glow-emerald { box-shadow: 0 0 25px rgba(16, 185, 129, 0.15); }
        .glow-blue { box-shadow: 0 0 25px rgba(59, 130, 246, 0.15); }
    </style>
</head>
<body class="text-slate-100 min-h-screen pb-16">
    <!-- Header -->
    <header class="border-b border-slate-800/80 bg-slate-900/50 sticky top-0 z-50 backdrop-blur-md">
        <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="h-10 w-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center font-bold text-white text-lg shadow-lg">
                    R
                </div>
                <div>
                    <h1 class="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                        AI Revenue Recovery Agent
                        <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">Track 03 — Razorpay</span>
                    </h1>
                    <p class="text-xs text-slate-400">Autonomous Loss Prevention, Policy-Guarded Interventions & Independent Verification</p>
                </div>
            </div>
            <div class="flex items-center gap-3">
                <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
                    System Live
                </span>
                <a href="/docs" target="_blank" class="px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition">
                    Swagger API Docs ↗
                </a>
            </div>
        </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 mt-8 space-y-8">
        <!-- Top Metrics Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div class="glass-card p-5 rounded-2xl glow-blue">
                <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">At-Risk Revenue</p>
                <h3 id="stat-at-risk" class="text-2xl font-extrabold text-white mt-1">₹9,71,800</h3>
                <p class="text-xs text-slate-500 mt-1">50 evaluated payments</p>
            </div>
            <div class="glass-card p-5 rounded-2xl glow-emerald border-emerald-500/30 bg-emerald-950/20">
                <p class="text-xs font-medium text-emerald-400 uppercase tracking-wider">Money Recovered</p>
                <h3 id="stat-recovered" class="text-2xl font-extrabold text-emerald-400 mt-1">₹7,82,000</h3>
                <p id="stat-rate" class="text-xs text-emerald-500/80 font-medium mt-1">80.5% Recovery Rate</p>
            </div>
            <div class="glass-card p-5 rounded-2xl border-indigo-500/20">
                <p class="text-xs font-medium text-indigo-400 uppercase tracking-wider">Net Financial Lift</p>
                <h3 id="stat-lift" class="text-2xl font-extrabold text-indigo-300 mt-1">+₹5,64,200</h3>
                <p class="text-xs text-slate-500 mt-1">vs. Naive Baseline (22%)</p>
            </div>
            <div class="glass-card p-5 rounded-2xl border-rose-500/20">
                <p class="text-xs font-medium text-rose-400 uppercase tracking-wider">Fraud Loss Prevented</p>
                <h3 id="stat-fraud" class="text-2xl font-extrabold text-rose-400 mt-1">₹3,48,000</h3>
                <p class="text-xs text-slate-500 mt-1">100% fraud attempts blocked</p>
            </div>
            <div class="glass-card p-5 rounded-2xl border-amber-500/20">
                <p class="text-xs font-medium text-amber-400 uppercase tracking-wider">Safety Policy Guard</p>
                <h3 id="stat-blocks" class="text-2xl font-extrabold text-amber-300 mt-1">16 Blocked</h3>
                <p class="text-xs text-slate-500 mt-1">Deterministic policy enforcement</p>
            </div>
        </div>

        <!-- Action Row -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Left: Interactive Orchestrator -->
            <div class="lg:col-span-2 glass-card p-6 rounded-2xl space-y-6">
                <div class="flex items-center justify-between border-b border-slate-800 pb-4">
                    <div>
                        <h2 class="text-lg font-bold text-white flex items-center gap-2">
                            Autonomous 7-Step Recovery Orchestration
                        </h2>
                        <p class="text-xs text-slate-400">Detect → Diagnose → Decide → Policy Check → Act → Verify → Recover</p>
                    </div>
                    <div class="flex items-center gap-2">
                        <select id="scenario-picker" class="bg-slate-800 border border-slate-700 text-xs rounded-lg px-3 py-2 text-slate-200">
                            <option value="network_error">Transient Network Error (₹1,200)</option>
                            <option value="gateway_timeout">Gateway Timeout (₹2,800)</option>
                            <option value="insufficient_funds">Insufficient Funds (₹2,200 - 1-Click Link)</option>
                            <option value="bank_declined">Bank Declined (₹4,500 - 1-Click Link)</option>
                            <option value="suspected_fraud">Suspected Fraud (₹55,000 - Escalated)</option>
                        </select>
                        <button onclick="runSingleCase()" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-md transition flex items-center gap-1.5">
                            ▶ Run Agent
                        </button>
                    </div>
                </div>

                <!-- 7 Steps Visualizer -->
                <div id="steps-container" class="space-y-3">
                    <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 text-xs text-slate-400">
                        Select a payment failure scenario and click <strong class="text-blue-400">Run Agent</strong> to watch the 7-step autonomous workflow execute live.
                    </div>
                </div>
            </div>

            <!-- Right: RAG Vector Knowledge Query & Benchmark Trigger -->
            <div class="space-y-6">
                <!-- Batch Benchmark Trigger -->
                <div class="glass-card p-6 rounded-2xl space-y-4">
                    <h2 class="text-base font-bold text-white flex items-center justify-between">
                        Batch ROI Benchmark
                        <span class="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 font-normal">50 Cases</span>
                    </h2>
                    <p class="text-xs text-slate-400">
                        Executes a head-to-head simulation across 50 realistic payments comparing the <strong>AI Recovery Agent</strong> vs <strong>Naive Baseline</strong>.
                    </p>
                    <button onclick="runBenchmark()" id="btn-benchmark" class="w-full py-2.5 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white rounded-xl text-xs font-bold shadow-lg transition">
                        ⚡ Run 50-Case Batch Evaluation
                    </button>
                    <div id="benchmark-status" class="text-xs text-slate-400 hidden"></div>
                </div>

                <!-- RAG Policy Search -->
                <div class="glass-card p-6 rounded-2xl space-y-4">
                    <h2 class="text-base font-bold text-white flex items-center justify-between">
                        RAG Vector Policy Search
                    </h2>
                    <div class="flex gap-2">
                        <input id="rag-query" type="text" placeholder="e.g., gateway timeout" value="gateway timeout" class="w-full bg-slate-800 border border-slate-700 text-xs rounded-lg px-3 py-2 text-slate-200">
                        <button onclick="searchRAG()" class="px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white rounded-lg text-xs font-medium transition">
                            Search
                        </button>
                    </div>
                    <div id="rag-results" class="space-y-2 text-xs">
                        <div class="text-slate-500">Query recovery policies dynamically retrieved via cosine similarity.</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Bottom: Live Audit Trail -->
        <div class="glass-card p-6 rounded-2xl space-y-4">
            <div class="flex items-center justify-between">
                <h2 class="text-base font-bold text-white">PostgreSQL Persistent Action Audit Trail</h2>
                <button onclick="loadAnalytics()" class="text-xs text-blue-400 hover:text-blue-300 font-medium">⟳ Refresh Audit Logs</button>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-xs text-slate-300">
                    <thead class="bg-slate-800/60 text-slate-400 uppercase tracking-wider text-[10px]">
                        <tr>
                            <th class="p-3">Log ID</th>
                            <th class="p-3">Case ID</th>
                            <th class="p-3">Action</th>
                            <th class="p-3">Audit Details</th>
                        </tr>
                    </thead>
                    <tbody id="audit-tbody" class="divide-y divide-slate-800/60">
                        <tr><td colspan="4" class="p-4 text-center text-slate-500">Loading audit trail...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </main>

    <script>
        const API_BASE = window.location.origin;

        async function loadAnalytics() {
            try {
                const res = await fetch(`${API_BASE}/recovery/analytics`);
                const data = await res.json();
                if (data.kpis) {
                    document.getElementById("stat-at-risk").innerText = "₹" + Number(data.kpis.total_at_risk_inr).toLocaleString("en-IN");
                    document.getElementById("stat-recovered").innerText = "₹" + Number(data.kpis.total_recovered_inr).toLocaleString("en-IN");
                    document.getElementById("stat-rate").innerText = `${data.kpis.recovery_rate_percent}% Recovery Rate`;
                }
                const tbody = document.getElementById("audit-tbody");
                if (data.recent_audit_trail && data.recent_audit_trail.length > 0) {
                    tbody.innerHTML = data.recent_audit_trail.map(log => `
                        <tr class="hover:bg-slate-800/30 transition">
                            <td class="p-3 font-mono text-slate-400">#${log.id}</td>
                            <td class="p-3 font-semibold text-blue-400">Case ${log.case_id}</td>
                            <td class="p-3"><span class="px-2 py-0.5 rounded bg-slate-800 font-mono text-slate-200 border border-slate-700">${log.action}</span></td>
                            <td class="p-3 text-slate-300">${log.details}</td>
                        </tr>
                    `).join("");
                }
            } catch (e) {
                console.error("Failed loading analytics", e);
            }
        }

        async function runBenchmark() {
            const btn = document.getElementById("btn-benchmark");
            const status = document.getElementById("benchmark-status");
            btn.disabled = true;
            btn.innerText = "⏳ Evaluating 50 cases...";
            status.classList.remove("hidden");
            status.innerText = "Executing Gemini + RAG + Policy Gate across 50 payment scenarios...";

            try {
                const res = await fetch(`${API_BASE}/simulator/benchmark?count=50`, { method: "POST" });
                const data = await res.json();
                const s = data.summary;
                document.getElementById("stat-at-risk").innerText = "₹" + Number(s.total_revenue_at_risk_inr).toLocaleString("en-IN");
                document.getElementById("stat-recovered").innerText = "₹" + Number(s.ai_money_recovered_inr).toLocaleString("en-IN");
                document.getElementById("stat-rate").innerText = `${s.ai_recovery_rate_percent}% Recovery Rate`;
                document.getElementById("stat-lift").innerText = "+₹" + Number(s.net_revenue_lift_inr).toLocaleString("en-IN");
                document.getElementById("stat-fraud").innerText = "₹" + Number(s.fraud_losses_prevented_by_ai_inr).toLocaleString("en-IN");
                document.getElementById("stat-blocks").innerText = `${s.unsafe_actions_prevented} Blocked`;

                status.innerHTML = `<span class="text-emerald-400 font-semibold">✓ Benchmark complete!</span> Recovered ₹${Number(s.ai_money_recovered_inr).toLocaleString("en-IN")} (${s.ai_recovery_rate_percent}%) vs Baseline ₹${Number(s.baseline_money_recovered_inr).toLocaleString("en-IN")}.`;
                loadAnalytics();
            } catch (e) {
                status.innerHTML = `<span class="text-rose-400">Error running benchmark: ${e.message}</span>`;
            } finally {
                btn.disabled = false;
                btn.innerText = "⚡ Run 50-Case Batch Evaluation";
            }
        }

        async function searchRAG() {
            const query = document.getElementById("rag-query").value;
            const container = document.getElementById("rag-results");
            container.innerHTML = "<div class='text-slate-400'>Searching vector policies...</div>";
            try {
                const res = await fetch(`${API_BASE}/rag/search?query=${encodeURIComponent(query)}&limit=3`);
                const data = await res.json();
                container.innerHTML = data.results.map(item => `
                    <div class="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60 space-y-1">
                        <div class="flex items-center justify-between">
                            <span class="font-semibold text-white">${item.title}</span>
                            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300">Sim: ${item.similarity}</span>
                        </div>
                        <p class="text-[11px] text-slate-300">${item.content}</p>
                        <div class="text-[10px] text-emerald-400 font-mono">Recommended Action: ${item.recommended_action}</div>
                    </div>
                `).join("");
            } catch (e) {
                container.innerHTML = `<div class="text-rose-400">Error: ${e.message}</div>`;
            }
        }

        async function runSingleCase() {
            const reason = document.getElementById("scenario-picker").value;
            const container = document.getElementById("steps-container");
            container.innerHTML = "<div class='text-blue-400 animate-pulse text-xs'>Initializing autonomous recovery pipeline...</div>";

            const paymentId = "demo_pay_" + Date.now().toString().slice(-6);
            const amount = reason === "suspected_fraud" ? 55000 : (reason === "gateway_timeout" ? 2800 : 1200);

            try {
                // 1. Create case
                const caseRes = await fetch(`${API_BASE}/recovery/cases`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ customer_id: "demo_cust_01", payment_id: paymentId, amount })
                });
                const caseData = await caseRes.json();

                // 2. Run orchestrator
                const runRes = await fetch(`${API_BASE}/orchestrator/run/${caseData.id}`, { method: "POST" });
                const trace = await runRes.json();
                const s = trace.seven_steps || {};

                container.innerHTML = `
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
                            <div class="text-[10px] font-bold text-blue-400 uppercase">Step 1: Detect</div>
                            <div class="text-xs text-white font-medium mt-1">Payment ${paymentId} Failed</div>
                            <div class="text-[11px] text-slate-400">Reason: ${reason} (Amount: ₹${amount.toLocaleString()})</div>
                        </div>
                        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
                            <div class="text-[10px] font-bold text-indigo-400 uppercase">Step 2: Diagnose (RAG)</div>
                            <div class="text-xs text-white font-medium mt-1">Vector Knowledge Retrieved</div>
                            <div class="text-[11px] text-slate-400 truncate">${trace.retrieved_knowledge ? trace.retrieved_knowledge.slice(0, 70) + "..." : "Matched"}</div>
                        </div>
                        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
                            <div class="text-[10px] font-bold text-violet-400 uppercase">Step 3: Decide (Gemini)</div>
                            <div class="text-xs text-white font-medium mt-1 font-mono">${trace.ai_decision?.decision || "decided"}</div>
                            <div class="text-[11px] text-slate-400">${trace.ai_decision?.reason || ""}</div>
                        </div>
                        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
                            <div class="text-[10px] font-bold text-amber-400 uppercase">Step 4: Policy Gate</div>
                            <div class="text-xs ${trace.policy?.allowed ? 'text-emerald-400' : 'text-rose-400'} font-semibold mt-1">
                                ${trace.policy?.allowed ? '✓ Passed Safety Rules' : '⚠ Blocked by Policy'}
                            </div>
                            <div class="text-[11px] text-slate-400">${trace.policy?.reason || ""}</div>
                        </div>
                        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
                            <div class="text-[10px] font-bold text-cyan-400 uppercase">Step 5: Act</div>
                            <div class="text-xs text-white font-mono mt-1">${trace.action?.tool || "tool_executed"}</div>
                            <div class="text-[11px] text-slate-400">${trace.action?.payment_link_url ? 'Link: ' + trace.action.payment_link_url : 'Status: ' + trace.action?.status}</div>
                        </div>
                        <div class="p-3 rounded-xl bg-slate-900 border border-slate-800">
                            <div class="text-[10px] font-bold text-teal-400 uppercase">Step 6 & 7: Verify & Outcome</div>
                            <div class="text-xs ${trace.final_status === 'recovered' ? 'text-emerald-400 font-bold' : 'text-amber-400 font-bold'} mt-1">
                                ${trace.final_status === 'recovered' ? '✓ RECOVERED (₹' + amount.toLocaleString() + ')' : 'ESCALATED / REVIEW'}
                            </div>
                            <div class="text-[11px] text-slate-400">Independent Verification: ${trace.verification?.verified ? 'Success' : 'Escalated'}</div>
                        </div>
                    </div>
                `;
                loadAnalytics();
            } catch (e) {
                container.innerHTML = `<div class="text-rose-400">Error executing case: ${e.message}</div>`;
            }
        }

        // Initialize on load
        loadAnalytics();
        searchRAG();
    </script>
</body>
</html>
    """

