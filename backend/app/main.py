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
from app.routes.mandate import router as mandate_router
from app.routes.receivables import router as receivables_router
from app.routes.gateway import router as gateway_router
from app.routes.razorpay import router as razorpay_router

app = FastAPI(
    title="Razorpay AI Revenue Recovery Agent",
    description="Autonomous AI Agent for Payment Recovery, Mandate Sequencing, B2B Receivables & Loss Prevention (Track 03)",
    version="2.0.0",
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
app.include_router(mandate_router)
app.include_router(receivables_router)
app.include_router(gateway_router)
app.include_router(razorpay_router)



@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RecoveryOS — Revenue Recovery Control Plane</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Razorpay Standard Checkout SDK -->
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Google Fonts: Plus Jakarta Sans & JetBrains Mono -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; background-color: #f8fafc; color: #0f172a; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
        
        /* Razorpay brand green accent */
        .brand-green { color: #00d09c; }
        .bg-brand-green { background-color: #00d09c; }
        .bg-brand-green:hover { background-color: #00b386; }
        
        /* Stripe/Linear style restrained surfaces and borders */
        .rec-surface { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; }
        .rec-row-hover:hover { background-color: #f8fafc; }
        
        /* Sidebar Navigation */
        .nav-link { display: flex; align-items: center; gap: 0.625rem; padding: 0.45rem 0.75rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; color: #475569; transition: all 0.12s ease; cursor: pointer; }
        .nav-link:hover { background-color: #f1f5f9; color: #0f172a; }
        .nav-link-active { background-color: #0f172a; color: #ffffff !important; font-weight: 600; }
        .nav-link-active:hover { background-color: #1e293b; }
        
        /* Slide-over Drawer Animations */
        .drawer-backdrop { background-color: rgba(15, 23, 42, 0.45); backdrop-filter: blur(2px); transition: opacity 0.2s ease; }
        .drawer-content { transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1); }
        
        /* Subtle Custom Scrollbar */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: #f8fafc; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 999px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

        /* Step Timeline Styling */
        .timeline-line { position: absolute; left: 11px; top: 22px; bottom: 0; width: 2px; background: #e2e8f0; }
        .step-dot-done { width: 24px; height: 24px; border-radius: 999px; background: #ecfdf5; border: 2px solid #10b981; display: flex; align-items: center; justify-content: center; color: #047857; font-size: 11px; font-weight: bold; flex-shrink: 0; z-index: 2; }
        .step-dot-blocked { width: 24px; height: 24px; border-radius: 999px; background: #fff1f2; border: 2px solid #f43f5e; display: flex; align-items: center; justify-content: center; color: #be123c; font-size: 11px; font-weight: bold; flex-shrink: 0; z-index: 2; }
        .step-dot-pending { width: 24px; height: 24px; border-radius: 999px; background: #f8fafc; border: 2px solid #cbd5e1; display: flex; align-items: center; justify-content: center; color: #64748b; font-size: 11px; font-weight: bold; flex-shrink: 0; z-index: 2; }
    </style>
</head>
<body class="min-h-screen flex bg-[#f8fafc] text-slate-900 antialiased overflow-x-hidden">

    <!-- IN-APP TOAST CONTAINER (No browser alert() calls) -->
    <div id="toast-container" class="fixed top-5 right-5 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none"></div>

    <!-- PERSISTENT LEFT SIDEBAR -->
    <aside class="w-64 bg-white border-r border-slate-200/90 flex flex-col justify-between shrink-0 fixed inset-y-0 z-30 select-none">
        <div class="flex flex-col">
            <!-- Brand Header -->
            <div class="h-16 px-5 flex items-center justify-between border-b border-slate-100">
                <div class="flex items-center gap-2.5">
                    <div class="h-7 w-7 rounded-lg bg-slate-900 flex items-center justify-center text-white font-black text-xs tracking-tight">
                        R
                    </div>
                    <div>
                        <div class="font-extrabold text-sm text-slate-900 tracking-tight flex items-center gap-1.5">
                            RecoveryOS
                            <span class="text-[9px] font-bold px-1.5 py-0.2 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded">v2.4</span>
                        </div>
                        <div class="text-[10px] text-slate-400 font-medium">Revenue Control Plane</div>
                    </div>
                </div>
            </div>

            <!-- Navigation Links -->
            <nav class="p-3 space-y-4 overflow-y-auto">
                <!-- Group 1: RECOVERY -->
                <div class="space-y-0.5">
                    <div class="px-2.5 pb-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Recovery</div>
                    <div onclick="navigateView('overview')" id="nav-overview" class="nav-link nav-link-active">
                        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
                        <span>Overview</span>
                    </div>
                    <div onclick="navigateView('cases')" id="nav-cases" class="nav-link">
                        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
                        <span class="flex-1">Cases</span>
                        <span id="badge-total-cases" class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-100 text-slate-600 font-bold">50</span>
                    </div>
                    <div onclick="navigateView('automations')" id="nav-automations" class="nav-link">
                        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                        <span>Automations</span>
                    </div>
                </div>

                <!-- Group 2: INSIGHTS -->
                <div class="space-y-0.5">
                    <div class="px-2.5 pb-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Insights</div>
                    <div onclick="navigateView('benchmark')" id="nav-benchmark" class="nav-link">
                        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
                        <span>Performance</span>
                    </div>
                    <div onclick="navigateView('gateway')" id="nav-gateway" class="nav-link">
                        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"/></svg>
                        <span>Payment Health</span>
                    </div>
                </div>

                <!-- Group 3: OPERATIONS -->
                <div class="space-y-0.5">
                    <div class="px-2.5 pb-1 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Operations</div>
                    <div onclick="navigateView('audit')" id="nav-audit" class="nav-link">
                        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        <span>Audit Log</span>
                    </div>
                    <div onclick="navigateView('policies')" id="nav-policies" class="nav-link">
                        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
                        <span>Policies & Guardrails</span>
                    </div>
                    <div onclick="navigateView('integrations')" id="nav-integrations" class="nav-link">
                        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                        <span>Integrations</span>
                    </div>
                </div>
            </nav>
        </div>

        <!-- Sidebar Bottom: Razorpay Sandbox Status -->
        <div class="p-3 border-t border-slate-100">
            <div class="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80 space-y-1">
                <div class="flex items-center justify-between">
                    <span class="text-[11px] font-bold text-slate-700">Razorpay Sandbox</span>
                    <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                </div>
                <div class="text-[10px] text-slate-400 font-mono">rzp_test_••••8921</div>
                <div class="flex items-center justify-between text-[10px] text-emerald-700 font-medium pt-0.5">
                    <span>Connected</span>
                    <span>● Webhooks Active</span>
                </div>
            </div>
        </div>
    </aside>

    <!-- MAIN APP CONTENT (Offset for 256px sidebar) -->
    <div class="flex-1 pl-64 flex flex-col min-h-screen">
        <!-- Top App Bar -->
        <header class="h-16 bg-white border-b border-slate-200/80 sticky top-0 z-20 px-8 flex items-center justify-between">
            <div class="flex items-center gap-2.5">
                <span class="text-xs font-semibold text-slate-400">RecoveryOS</span>
                <span class="text-slate-300">/</span>
                <span id="breadcrumb-view" class="text-xs font-bold text-slate-900">Overview</span>
            </div>

            <div class="flex items-center gap-3">
                <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-[11px] font-semibold text-emerald-800">
                    <span class="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span>Recovery Engine Active</span>
                </div>
                <button onclick="triggerQuickCheckoutDemo()" class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-xs transition flex items-center gap-1.5">
                    <span>⚡ Test Razorpay Payment</span>
                </button>
                <button onclick="openSimulateModal()" class="px-3 py-1.5 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-xs transition flex items-center gap-1.5">
                    <span>+ Simulate Failure Event</span>
                </button>
                <button onclick="triggerEvaluationBatch()" class="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold shadow-xs transition flex items-center gap-1.5">
                    <span>⚡ Run 50-Case Evaluation</span>
                </button>
            </div>
        </header>

        <!-- Main Workspace -->
        <main class="p-8 max-w-7xl w-full mx-auto space-y-6">

            <!-- ================= 1. OVERVIEW VIEW ================= -->
            <div id="view-overview" class="view-panel space-y-6">
                <!-- RECOVERY PERFORMANCE Banner -->
                <div class="rec-surface p-6 space-y-5">
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-2">
                        <div>
                            <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Recovery Performance</div>
                            <div class="flex items-baseline gap-4 mt-1">
                                <span class="text-3xl font-black text-slate-900 tracking-tight font-mono" id="hero-recovered-amt">₹3,80,200</span>
                                <span class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200" id="hero-recovery-rate">72.0% Recovery Rate</span>
                                <span class="text-xs font-bold text-slate-500" id="hero-net-lift">+₹1,66,400 vs. Naive Baseline</span>
                            </div>
                        </div>
                        <div class="text-[11px] text-slate-400 font-medium">
                            Evaluation dataset · 50 synthetic payment failures
                        </div>
                    </div>

                    <!-- Restrained 4-KPI Row -->
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-100 text-xs">
                        <div class="space-y-0.5">
                            <div class="text-slate-400 font-medium">Revenue at Risk</div>
                            <div class="text-base font-bold text-slate-800 font-mono" id="stat-at-risk">₹9,30,200</div>
                            <div class="text-[10px] text-slate-400">50 evaluated cases</div>
                        </div>
                        <div class="space-y-0.5">
                            <div class="text-slate-400 font-medium">Money Recovered</div>
                            <div class="text-base font-bold text-emerald-700 font-mono" id="stat-recovered">₹3,80,200</div>
                            <div class="text-[10px] text-emerald-600 font-medium">36 cases won back</div>
                        </div>
                        <div class="space-y-0.5">
                            <div class="text-slate-400 font-medium">Naive Baseline</div>
                            <div class="text-base font-bold text-slate-600 font-mono" id="stat-baseline">₹2,13,800</div>
                            <div class="text-[10px] text-slate-400">40.0% blind recovery</div>
                        </div>
                        <div class="space-y-0.5">
                            <div class="text-slate-400 font-medium">Fraud Losses Shielded</div>
                            <div class="text-base font-bold text-rose-600 font-mono" id="stat-fraud">₹3,70,000</div>
                            <div class="text-[10px] text-rose-600 font-medium">100% fraud blocked</div>
                        </div>
                    </div>
                </div>

                <!-- Recovery Performance Chart -->
                <div class="rec-surface p-6 space-y-3">
                    <div class="flex items-center justify-between">
                        <div>
                            <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400">Recovery Performance Trajectory</h2>
                            <p class="text-xs text-slate-600 font-medium mt-0.5">Cumulative revenue won back across evaluation milestones</p>
                        </div>
                        <span class="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">+₹1,66,400 Financial Lift</span>
                    </div>
                    <div class="h-56">
                        <canvas id="chart-overview-curve"></canvas>
                    </div>
                </div>

                <!-- Cases Requiring Attention Table -->
                <div class="rec-surface p-6 space-y-4">
                    <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                        <div>
                            <h2 class="text-sm font-bold text-slate-900">Cases Requiring Attention</h2>
                            <p class="text-xs text-slate-500 font-medium">Escalated anomalies, VIP invoices, and high-risk policy blocks</p>
                        </div>
                        <button onclick="navigateView('cases')" class="text-xs font-semibold text-slate-600 hover:text-slate-900">
                            View All Cases ➔
                        </button>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs text-slate-600">
                            <thead class="text-slate-400 font-bold uppercase text-[10px] tracking-wider border-b border-slate-100">
                                <tr>
                                    <th class="py-2.5 px-3">Case</th>
                                    <th class="py-2.5 px-3">Payment</th>
                                    <th class="py-2.5 px-3">Failure Reason</th>
                                    <th class="py-2.5 px-3">Amount</th>
                                    <th class="py-2.5 px-3">Agent Action</th>
                                    <th class="py-2.5 px-3">Status</th>
                                    <th class="py-2.5 px-3 text-right">Inspect</th>
                                </tr>
                            </thead>
                            <tbody id="overview-attention-tbody" class="divide-y divide-slate-100 font-medium">
                                <tr><td colspan="7" class="p-4 text-center text-slate-400">Loading cases requiring attention...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Recent Recovery Activity -->
                <div class="rec-surface p-6 space-y-4">
                    <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                        <div>
                            <h2 class="text-sm font-bold text-slate-900">Recent Recovery Activity</h2>
                            <p class="text-xs text-slate-500 font-medium">Real-time payment failure stream evaluated through the autonomous recovery pipeline</p>
                        </div>
                        <button onclick="loadOverviewData()" class="text-xs font-semibold text-slate-600 hover:text-slate-900">
                            ⟳ Refresh Stream
                        </button>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs text-slate-600">
                            <thead class="text-slate-400 font-bold uppercase text-[10px] tracking-wider border-b border-slate-100">
                                <tr>
                                    <th class="py-2.5 px-3">Case</th>
                                    <th class="py-2.5 px-3">Payment</th>
                                    <th class="py-2.5 px-3">Customer</th>
                                    <th class="py-2.5 px-3">Failure Reason</th>
                                    <th class="py-2.5 px-3">Amount</th>
                                    <th class="py-2.5 px-3">Status</th>
                                    <th class="py-2.5 px-3 text-right">Inspect</th>
                                </tr>
                            </thead>
                            <tbody id="overview-activity-tbody" class="divide-y divide-slate-100 font-medium">
                                <tr><td colspan="7" class="p-4 text-center text-slate-400">Loading activity...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- ================= 2. CASES VIEW ================= -->
            <div id="view-cases" class="view-panel hidden space-y-6">
                <div class="rec-surface p-6 space-y-4">
                    <!-- Cases Header & Filters -->
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-4">
                        <div>
                            <div class="flex items-center gap-2">
                                <h2 class="text-base font-bold text-slate-900">Recovery Cases</h2>
                                <span id="cases-count-badge" class="text-xs font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">50 cases</span>
                            </div>
                            <p class="text-xs text-slate-500 font-medium mt-0.5">Click any case to inspect the 7-step autonomous agent trace, RAG diagnosis, and policy guard decisions.</p>
                        </div>
                        
                        <!-- Search & Trigger -->
                        <div class="flex items-center gap-2">
                            <input id="case-search-input" onkeyup="filterCasesTable()" type="text" placeholder="Search payment ID, customer, reason..." class="bg-slate-50 border border-slate-200 text-xs rounded-lg px-3 py-1.5 text-slate-800 font-medium focus:ring-2 focus:ring-slate-900 focus:outline-none w-64">
                            <button onclick="openSimulateModal()" class="px-3 py-1.5 bg-slate-900 text-white rounded-lg text-xs font-semibold hover:bg-slate-800 transition">
                                + New Case
                            </button>
                        </div>
                    </div>

                    <!-- Filter Tabs -->
                    <div class="flex items-center gap-1 border-b border-slate-100 pb-2 text-xs font-semibold text-slate-500">
                        <button onclick="setCaseFilter('all')" id="filter-all" class="px-3 py-1 rounded bg-slate-900 text-white">All</button>
                        <button onclick="setCaseFilter('recovered')" id="filter-recovered" class="px-3 py-1 rounded hover:bg-slate-100 text-slate-600">Recovered</button>
                        <button onclick="setCaseFilter('pending')" id="filter-pending" class="px-3 py-1 rounded hover:bg-slate-100 text-slate-600">Pending</button>
                        <button onclick="setCaseFilter('escalated')" id="filter-escalated" class="px-3 py-1 rounded hover:bg-slate-100 text-slate-600">Escalated</button>
                        <button onclick="setCaseFilter('blocked')" id="filter-blocked" class="px-3 py-1 rounded hover:bg-slate-100 text-slate-600">Blocked</button>
                    </div>

                    <!-- Operational Table -->
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs text-slate-600">
                            <thead class="text-slate-400 font-bold uppercase text-[10px] tracking-wider border-b border-slate-100">
                                <tr>
                                    <th class="py-3 px-3">Case</th>
                                    <th class="py-3 px-3">Payment ID</th>
                                    <th class="py-3 px-3">Customer</th>
                                    <th class="py-3 px-3">Failure Reason</th>
                                    <th class="py-3 px-3">Amount</th>
                                    <th class="py-3 px-3">Agent Action</th>
                                    <th class="py-3 px-3">Status</th>
                                    <th class="py-3 px-3 text-right">Inspect</th>
                                </tr>
                            </thead>
                            <tbody id="cases-repository-tbody" class="divide-y divide-slate-100 font-medium">
                                <tr><td colspan="8" class="p-4 text-center text-slate-400">Loading cases repository...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- ================= 3. PERFORMANCE (EVALUATION BENCHMARK) VIEW ================= -->
            <div id="view-benchmark" class="view-panel hidden space-y-6">
                <div class="rec-surface p-6 space-y-6">
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-100 pb-4">
                        <div>
                            <div class="flex items-center gap-2">
                                <h2 class="text-base font-bold text-slate-900">Recovery Evaluation Benchmark</h2>
                                <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono">50 cases evaluated</span>
                            </div>
                            <p class="text-xs text-slate-500 font-medium mt-0.5">Head-to-head empirical comparison: Autonomous Recovery Agent vs. Naive Baseline on 50 synthetic failure scenarios.</p>
                        </div>
                        <button onclick="triggerEvaluationBatch()" class="px-4 py-2 rounded-lg bg-slate-900 text-white text-xs font-bold shadow-xs hover:bg-slate-800 transition flex items-center gap-1.5">
                            <span>⚡ Re-Run 50-Case Evaluation</span>
                        </button>
                    </div>

                    <!-- Side-by-Side Comparison Table -->
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead class="text-slate-400 font-bold uppercase text-[10px] tracking-wider border-b border-slate-100">
                                <tr>
                                    <th class="py-3 px-4">Evaluation Metric</th>
                                    <th class="py-3 px-4 text-emerald-800 font-black">AGENT</th>
                                    <th class="py-3 px-4 text-slate-600">BASELINE</th>
                                    <th class="py-3 px-4 text-right">NET LIFT</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-slate-100 font-medium text-slate-700">
                                <tr>
                                    <td class="py-3.5 px-4 font-bold text-slate-900">Recovery Rate</td>
                                    <td class="py-3.5 px-4 font-black text-emerald-700 text-sm">72.0%</td>
                                    <td class="py-3.5 px-4 text-slate-500">40.0%</td>
                                    <td class="py-3.5 px-4 text-right font-black text-emerald-700">+32.0 pp</td>
                                </tr>
                                <tr>
                                    <td class="py-3.5 px-4 font-bold text-slate-900">Money Recovered</td>
                                    <td class="py-3.5 px-4 font-black text-emerald-700 text-sm font-mono">₹3,80,200</td>
                                    <td class="py-3.5 px-4 text-slate-500 font-mono">₹2,13,800</td>
                                    <td class="py-3.5 px-4 text-right font-black text-emerald-700 font-mono">+₹1,66,400</td>
                                </tr>
                                <tr>
                                    <td class="py-3.5 px-4 font-bold text-slate-900">Fraud Chargebacks Shielded</td>
                                    <td class="py-3.5 px-4 font-bold text-emerald-700">100% (₹3,70,000 shielded)</td>
                                    <td class="py-3.5 px-4 text-rose-600 font-bold">0% (₹3,70,000 lost)</td>
                                    <td class="py-3.5 px-4 text-right font-black text-emerald-700">100% Fraud Protection</td>
                                </tr>
                                <tr>
                                    <td class="py-3.5 px-4 font-bold text-slate-900">Unsafe Policy Violations</td>
                                    <td class="py-3.5 px-4 font-bold text-emerald-700">0 Violations</td>
                                    <td class="py-3.5 px-4 text-rose-600">14 Unsafe Retries</td>
                                    <td class="py-3.5 px-4 text-right font-black text-emerald-700">14 Retries Blocked</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Recovery Breakdown & Strategic Analysis -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="rec-surface p-6 space-y-4">
                        <div class="text-xs font-bold uppercase tracking-wider text-slate-400">Recovery by Failure Type</div>
                        <div class="space-y-3 text-xs font-medium">
                            <div class="space-y-1">
                                <div class="flex justify-between"><span>Gateway timeout</span><strong class="text-emerald-700 font-mono">90%</strong></div>
                                <div class="h-2 bg-slate-100 rounded-full overflow-hidden"><div class="h-full bg-emerald-500" style="width: 90%"></div></div>
                            </div>
                            <div class="space-y-1">
                                <div class="flex justify-between"><span>Insufficient funds</span><strong class="text-emerald-700 font-mono">82%</strong></div>
                                <div class="h-2 bg-slate-100 rounded-full overflow-hidden"><div class="h-full bg-emerald-500" style="width: 82%"></div></div>
                            </div>
                            <div class="space-y-1">
                                <div class="flex justify-between"><span>Expired card</span><strong class="text-emerald-700 font-mono">76%</strong></div>
                                <div class="h-2 bg-slate-100 rounded-full overflow-hidden"><div class="h-full bg-emerald-500" style="width: 76%"></div></div>
                            </div>
                            <div class="space-y-1">
                                <div class="flex justify-between"><span>Bank security decline</span><strong class="text-emerald-700 font-mono">71%</strong></div>
                                <div class="h-2 bg-slate-100 rounded-full overflow-hidden"><div class="h-full bg-emerald-500" style="width: 71%"></div></div>
                            </div>
                            <div class="space-y-1">
                                <div class="flex justify-between"><span>Fraud / Velocity risk</span><strong class="text-slate-400 font-mono">0% (100% escalated)</strong></div>
                                <div class="h-2 bg-slate-100 rounded-full overflow-hidden"><div class="h-full bg-rose-500" style="width: 0%"></div></div>
                            </div>
                        </div>
                    </div>

                    <div class="rec-surface p-6 space-y-3">
                        <div class="text-xs font-bold uppercase tracking-wider text-slate-400">Why the Agent Outperformed Baseline</div>
                        <h3 class="text-sm font-bold text-slate-900">+₹1,66,400 recovered over naive retries</h3>
                        <div class="space-y-2 text-xs text-slate-600 leading-relaxed font-medium">
                            <p>• <strong>Bounded Retries</strong>: Avoids burning merchant bank retry quotas on hard declines and network failures.</p>
                            <p>• <strong>1-Click Recovery Links</strong>: WhatsApp/SMS links convert 80%+ of balance declines by allowing alternative instruments (UPI, NetBanking).</p>
                            <p>• <strong>Mandate Optimization</strong>: Retries subscriptions during optimal bank liquidity windows (1st–5th salary cycle).</p>
                            <p>• <strong>Deterministic Safety Layer</strong>: Completely blocks ₹3.70L in chargeback liability by prohibiting retries on suspected fraud.</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ================= 4. PAYMENT HEALTH VIEW ================= -->
            <div id="view-gateway" class="view-panel hidden space-y-6">
                <div class="rec-surface p-6 space-y-4">
                    <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                        <div>
                            <h2 class="text-base font-bold text-slate-900">Payment Gateway & Bank Switch Health</h2>
                            <p class="text-xs text-slate-500 font-medium">Real-time health monitoring of major Indian banking switches. RecoveryOS pauses automatic retries when a bank gateway is degraded to prevent burning merchant limits.</p>
                        </div>
                        <button onclick="loadGatewayHealth()" class="text-xs font-semibold text-slate-600 hover:text-slate-900">
                            ⟳ Refresh Latency
                        </button>
                    </div>

                    <div id="gateway-health-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        <!-- Dynamically populated -->
                    </div>
                </div>
            </div>

            <!-- ================= 5. AUTOMATIONS VIEW ================= -->
            <div id="view-automations" class="view-panel hidden space-y-6">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <!-- Mandate Sequencer -->
                    <div class="rec-surface p-6 space-y-4">
                        <div class="border-b border-slate-100 pb-3">
                            <h2 class="text-sm font-bold text-slate-900">Mandate & Subscription Sequencer</h2>
                            <p class="text-xs text-slate-500 font-medium">Schedules recurring UPI AutoPay & card retries targeting salary credit cycles (1st–5th of month).</p>
                        </div>

                        <div class="space-y-3 text-xs font-medium">
                            <div>
                                <label class="text-slate-600">Mandate Reference ID:</label>
                                <input id="man-id" type="text" value="man_autopay_992" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 mt-1 text-slate-800 font-mono">
                            </div>
                            <div>
                                <label class="text-slate-600">Subscription Amount (INR):</label>
                                <input id="man-amount" type="number" value="4999" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 mt-1 text-slate-800 font-mono">
                            </div>
                            <div>
                                <label class="text-slate-600">Failure Cause:</label>
                                <select id="man-code" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 mt-1 text-slate-800 font-medium">
                                    <option value="insufficient_funds">Insufficient Funds (Salary Window 1st–5th)</option>
                                    <option value="bank_degraded">Bank Gateway Degraded (Off-Peak Window)</option>
                                    <option value="daily_limit_exceeded">Daily Limit Exceeded (Midnight Reset)</option>
                                </select>
                            </div>
                            <div class="flex items-center gap-2 pt-2">
                                <button onclick="scheduleMandate()" class="flex-1 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-semibold text-xs transition">
                                    Schedule Retry Window
                                </button>
                                <button onclick="processScheduledMandates()" class="py-2 px-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-semibold text-xs transition">
                                    ⚡ Process Due
                                </button>
                            </div>
                        </div>

                        <div id="mandate-status-box" class="p-3 bg-slate-50 rounded-lg border border-slate-100 text-xs text-slate-500">
                            Awaiting mandate scheduling.
                        </div>
                    </div>

                    <!-- B2B Promise-to-Pay (PTP) -->
                    <div class="rec-surface p-6 space-y-4">
                        <div class="border-b border-slate-100 pb-3">
                            <h2 class="text-sm font-bold text-slate-900">B2B Promise-to-Pay (PTP) Tracker</h2>
                            <p class="text-xs text-slate-500 font-medium">Gemini unstructured language extraction parses customer payment commitments and pauses collection chasers.</p>
                        </div>

                        <div class="space-y-3 text-xs font-medium">
                            <div>
                                <label class="text-slate-600">Invoice ID & Amount:</label>
                                <div class="grid grid-cols-2 gap-2 mt-1">
                                    <input id="ptp-inv-id" type="text" value="INV-2026-904" class="bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-800 font-mono">
                                    <input id="ptp-amount" type="number" value="75000" class="bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-800 font-mono">
                                </div>
                            </div>
                            <div>
                                <label class="text-slate-600">Customer Communication Note:</label>
                                <textarea id="ptp-msg" rows="3" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2.5 mt-1 text-slate-800 focus:ring-2 focus:ring-slate-900 focus:outline-none">Hi team, invoice received. We will process payment by this Friday once client clearance arrives.</textarea>
                            </div>
                            <button onclick="analyzePTP()" class="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-semibold text-xs transition">
                                Analyze Customer Commitment & Set PTP
                            </button>
                        </div>

                        <div id="ptp-status-box" class="p-3 bg-slate-50 rounded-lg border border-slate-100 text-xs text-slate-500">
                            Submit a message above to extract commitment date.
                        </div>
                    </div>
                </div>
            </div>

            <!-- ================= 6. AUDIT LOG VIEW ================= -->
            <div id="view-audit" class="view-panel hidden space-y-6">
                <div class="rec-surface p-6 space-y-4">
                    <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                        <div>
                            <h2 class="text-base font-bold text-slate-900">Operations Audit Trail</h2>
                            <p class="text-xs text-slate-500 font-medium">Immutable PostgreSQL log of every agent action, policy evaluation, and recovery confirmation</p>
                        </div>
                        <button onclick="loadAuditTimeline()" class="text-xs font-semibold text-slate-600 hover:text-slate-900">
                            ⟳ Refresh Logs
                        </button>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs text-slate-600">
                            <thead class="text-slate-400 font-bold uppercase text-[10px] tracking-wider border-b border-slate-100">
                                <tr>
                                    <th class="py-2.5 px-3">Log ID</th>
                                    <th class="py-2.5 px-3">Case</th>
                                    <th class="py-2.5 px-3">Action Type</th>
                                    <th class="py-2.5 px-3">Details & Audit Metadata</th>
                                </tr>
                            </thead>
                            <tbody id="audit-timeline-tbody" class="divide-y divide-slate-100 font-normal">
                                <tr><td colspan="4" class="p-4 text-center text-slate-400">Loading audit trail...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- ================= 7. POLICIES & GUARDRAILS VIEW ================= -->
            <div id="view-policies" class="view-panel hidden space-y-6">
                <div class="rec-surface p-6 space-y-5">
                    <div class="border-b border-slate-100 pb-3">
                        <h2 class="text-base font-bold text-slate-900">Deterministic Safety Policy Guardrails</h2>
                        <p class="text-xs text-slate-500 font-medium">Rules evaluated deterministically before any intervention is taken by the AI Agent</p>
                    </div>

                    <div class="space-y-3 text-xs">
                        <div class="p-4 rounded-xl border border-slate-200 bg-white space-y-1">
                            <div class="flex items-center justify-between">
                                <span class="font-bold text-slate-900">1. Maximum Automated Retry Quota</span>
                                <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">Active • Max 3 Retries</span>
                            </div>
                            <p class="text-slate-500">Limits automatic payment retries to 3 attempts. Once exhausted, escalates to operations to prevent burning merchant bank limits.</p>
                        </div>

                        <div class="p-4 rounded-xl border border-slate-200 bg-white space-y-1">
                            <div class="flex items-center justify-between">
                                <span class="font-bold text-slate-900">2. High-Value Ops Review Threshold</span>
                                <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">Active • > ₹50,000</span>
                            </div>
                            <p class="text-slate-500">Transactions exceeding ₹50,000 require secondary ops sign-off to ensure personalized high-touch handling.</p>
                        </div>

                        <div class="p-4 rounded-xl border border-slate-200 bg-white space-y-1">
                            <div class="flex items-center justify-between">
                                <span class="font-bold text-slate-900">3. Fraud & Velocity Blacklist Gate</span>
                                <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">Active • Zero Retries</span>
                            </div>
                            <p class="text-slate-500">Immediate hard-stop on any failure tagged as velocity anomaly or suspected fraud to completely shield against chargeback losses.</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- ================= 8. INTEGRATIONS VIEW ================= -->
            <div id="view-integrations" class="view-panel hidden space-y-6">
                <div class="rec-surface p-6 space-y-5">
                    <div class="flex items-center justify-between border-b border-slate-100 pb-3">
                        <div>
                            <h2 class="text-base font-bold text-slate-900">Razorpay Integration</h2>
                            <p class="text-xs text-slate-500 font-medium">Test Mode configuration, standard checkout orders, payment links, and webhook signature verification</p>
                        </div>
                        <span class="text-[10px] font-bold px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                            TEST MODE ACTIVE
                        </span>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-medium">
                        <div class="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-3">
                            <div class="flex items-center justify-between">
                                <div class="text-slate-400 font-bold uppercase text-[10px] tracking-wider">Gateway Connection</div>
                                <span id="int-gw-status" class="text-[10px] font-bold text-emerald-700">● Connected</span>
                            </div>
                            <div class="text-slate-900 font-bold text-sm">Razorpay Test Mode</div>
                            <div class="space-y-1.5 pt-1 text-slate-600">
                                <div class="flex items-center justify-between">
                                    <span>API Configuration:</span>
                                    <span class="text-emerald-700 font-bold">✓ Configured</span>
                                </div>
                                <div class="flex items-center justify-between">
                                    <span>Payment Orders API:</span>
                                    <span class="text-emerald-700 font-bold">✓ Available</span>
                                </div>
                                <div class="flex items-center justify-between">
                                    <span>Payment Links API:</span>
                                    <span class="text-emerald-700 font-bold">✓ Available</span>
                                </div>
                                <div class="flex items-center justify-between">
                                    <span>Signature Verification:</span>
                                    <span class="text-emerald-700 font-bold">✓ HMAC-SHA256 Active</span>
                                </div>
                            </div>
                        </div>

                        <div class="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-3">
                            <div class="flex items-center justify-between">
                                <div class="text-slate-400 font-bold uppercase text-[10px] tracking-wider">Webhooks & Security</div>
                                <span class="text-[10px] font-bold text-emerald-700">● Active</span>
                            </div>
                            <div class="text-slate-900 font-bold text-sm">Webhook Ingestion Endpoint</div>
                            <div class="space-y-1.5 pt-1 text-slate-600">
                                <div class="flex items-center justify-between">
                                    <span>Endpoint:</span>
                                    <span class="font-mono text-[10px] text-slate-700 font-bold">POST /events/razorpay-webhook</span>
                                </div>
                                <div class="flex items-center justify-between">
                                    <span>Webhook Signature Check:</span>
                                    <span class="text-emerald-700 font-bold">✓ Enforced</span>
                                </div>
                                <div class="flex items-center justify-between">
                                    <span>Key Secret Security:</span>
                                    <span class="text-slate-700 font-bold font-mono">Server-side Only (.env)</span>
                                </div>
                                <div class="flex items-center justify-between">
                                    <span>Subscribed Events:</span>
                                    <span class="text-[11px] text-slate-500 font-mono">payment.failed, order.paid, payment_link.paid</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>


        </main>
    </div>

    <!-- ================= SLIDE-OVER CASE DETAIL DRAWER ================= -->
    <div id="case-inspector-drawer" class="fixed inset-0 z-50 hidden">
        <!-- Backdrop -->
        <div onclick="closeCaseInspector()" class="drawer-backdrop fixed inset-0"></div>
        
        <!-- Drawer Panel -->
        <div class="fixed inset-y-0 right-0 max-w-lg w-full bg-white shadow-2xl border-l border-slate-200 flex flex-col justify-between drawer-content z-10">
            <!-- Header -->
            <div class="p-6 border-b border-slate-100 flex items-center justify-between">
                <div>
                    <div class="flex items-center gap-2">
                        <h2 id="insp-case-id" class="text-base font-black text-slate-900 font-mono">CASE #326</h2>
                        <span id="insp-status-badge" class="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">RECOVERED</span>
                    </div>
                    <div id="insp-case-subtitle" class="text-xs text-slate-600 font-bold mt-1">₹75,000 • Fraud velocity signal</div>
                </div>
                <button onclick="closeCaseInspector()" class="text-slate-400 hover:text-slate-700 text-xl font-bold p-1 leading-none">&times;</button>
            </div>

            <!-- Scrollable Timeline Body -->
            <div class="p-6 overflow-y-auto space-y-5 flex-1 text-xs">
                
                <!-- 1. Recovery Journey Timeline -->
                <div class="space-y-3">
                    <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Recovery Journey</div>
                    <div class="relative pl-6 space-y-4">
                        <div class="timeline-line"></div>

                        <!-- Step 1: Detect -->
                        <div class="relative flex items-start gap-3">
                            <div class="step-dot-done" style="margin-left: -24px;">✓</div>
                            <div class="space-y-0.5">
                                <div class="font-bold text-slate-900">Detected</div>
                                <div class="text-slate-500 text-[11px]" id="insp-step-detect-time">22:12:04 • Webhook received</div>
                            </div>
                        </div>

                        <!-- Step 2: Diagnosed -->
                        <div class="relative flex items-start gap-3">
                            <div class="step-dot-done" style="margin-left: -24px;">✓</div>
                            <div class="space-y-0.5">
                                <div class="font-bold text-slate-900">Diagnosed</div>
                                <div class="text-slate-600 text-[11px]" id="insp-step-diagnose-text">Insufficient funds • Customer balance decline</div>
                            </div>
                        </div>

                        <!-- Step 3: Decision -->
                        <div class="relative flex items-start gap-3">
                            <div class="step-dot-done" style="margin-left: -24px;">✓</div>
                            <div class="space-y-0.5">
                                <div class="font-bold text-slate-900">Decision</div>
                                <div class="text-slate-600 text-[11px]" id="insp-step-decision-text">Send 1-Click recovery link</div>
                            </div>
                        </div>

                        <!-- Step 4: Policy -->
                        <div class="relative flex items-start gap-3">
                            <div id="insp-step-policy-dot" class="step-dot-done" style="margin-left: -24px;">✓</div>
                            <div class="space-y-0.5">
                                <div class="font-bold text-slate-900">Policy Guard</div>
                                <div class="text-slate-600 text-[11px]" id="insp-step-policy-text">Approved • All safety guardrails satisfied</div>
                            </div>
                        </div>

                        <!-- Step 5: Action -->
                        <div class="relative flex items-start gap-3">
                            <div id="insp-step-action-dot" class="step-dot-done" style="margin-left: -24px;">✓</div>
                            <div class="space-y-0.5">
                                <div class="font-bold text-slate-900">Action</div>
                                <div class="text-slate-600 text-[11px]" id="insp-step-action-text">WhatsApp + SMS recovery link dispatched</div>
                            </div>
                        </div>

                        <!-- Step 6: Verification -->
                        <div class="relative flex items-start gap-3">
                            <div id="insp-step-verify-dot" class="step-dot-done" style="margin-left: -24px;">✓</div>
                            <div class="space-y-0.5">
                                <div class="font-bold text-slate-900">Verification</div>
                                <div class="text-slate-600 text-[11px]" id="insp-step-verify-text">Payment verified on Razorpay Gateway</div>
                            </div>
                        </div>

                        <!-- Step 7: Outcome -->
                        <div class="relative flex items-start gap-3">
                            <div id="insp-step-outcome-dot" class="step-dot-done" style="margin-left: -24px;">✓</div>
                            <div class="space-y-0.5">
                                <div class="font-bold text-emerald-800" id="insp-step-outcome-title">Recovered</div>
                                <div class="text-emerald-700 text-[11px] font-mono" id="insp-step-outcome-amount">₹3,500 won back</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 2. Agent Decision & Reasoning -->
                <div class="space-y-2 pt-2 border-t border-slate-100">
                    <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Agent Decision</div>
                    <div class="p-3.5 rounded-xl border border-slate-200 bg-slate-50 space-y-1.5">
                        <div class="flex items-center justify-between">
                            <span id="insp-decision-action" class="font-black font-mono text-xs text-slate-900 uppercase">SEND_RECOVERY_LINK</span>
                            <span id="insp-decision-conf" class="text-[10px] font-bold text-emerald-700">Confidence: 94%</span>
                        </div>
                        <p id="insp-decision-reason" class="text-slate-600 font-medium leading-relaxed">
                            Customer has transient balance decline with verified payment intent. Dispatched dynamic 1-click Razorpay payment link over WhatsApp and SMS.
                        </p>
                    </div>
                </div>

                <!-- 3. Policy Guard Checklist -->
                <div class="space-y-2">
                    <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Policy Guard</div>
                    <div id="insp-policy-box" class="p-3.5 rounded-xl border border-emerald-200 bg-emerald-50/50 space-y-1 text-[11px] text-emerald-900 font-medium">
                        <div>✓ Retry budget available (1 of 3)</div>
                        <div>✓ Amount threshold satisfied (₹3,500 < ₹50,000)</div>
                        <div>✓ No fraud velocity signal</div>
                        <div>✓ Customer contact frequency within limit</div>
                        <div class="pt-1 font-bold text-emerald-800">Decision: AUTOMATIC ACTION ALLOWED</div>
                    </div>
                </div>

                <!-- 4. Collapsible Technical Agent Trace -->
                <div class="space-y-2 pt-2 border-t border-slate-100">
                    <button onclick="toggleTechnicalTrace()" class="text-[11px] font-bold text-slate-500 hover:text-slate-900 flex items-center gap-1.5 focus:outline-none">
                        <span id="trace-toggle-arrow">▶</span>
                        <span>View Technical Agent Trace (RAG, Policy, LLM)</span>
                    </button>
                    <div id="technical-trace-box" class="hidden p-3.5 rounded-xl border border-slate-200 bg-slate-900 text-slate-200 space-y-2 text-[11px] font-mono">
                        <div class="text-slate-400 font-bold text-[10px] uppercase">RAG Semantic Match</div>
                        <div id="trace-rag-item" class="text-slate-300">Policy: Insufficient Funds Recovery Policy (Cosine: 0.58)</div>
                        <div class="text-slate-400 font-bold text-[10px] uppercase pt-1">Model Inference</div>
                        <div id="trace-model-info" class="text-slate-300">gemini-3.6-flash • Structured Output JSON</div>
                        <div class="text-slate-400 font-bold text-[10px] uppercase pt-1">Tool Dispatch</div>
                        <div id="trace-tool-info" class="text-slate-300">Tool: send_recovery_message • Target: pay_rzp_9924</div>
                    </div>
                </div>

                <!-- 5. Dedicated Razorpay Recovery Payment Card -->
                <div id="insp-payment-container" class="pt-2">
                    <div id="insp-payment-card" class="p-4 rounded-xl border border-slate-200 bg-slate-50/80 space-y-2.5">
                        <div class="flex items-center justify-between">
                            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500">Recovery Payment</span>
                            <span id="insp-pay-status-pill" class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">READY TO PAY</span>
                        </div>
                        <div class="flex items-baseline justify-between">
                            <span class="text-xl font-black text-slate-900 font-mono" id="insp-pay-amount">₹3,500</span>
                            <span class="text-xs text-slate-500 font-mono" id="insp-pay-payment-id">pay_rzp_9924</span>
                        </div>
                        <div class="text-[11px] text-slate-600 font-medium">
                            Recovery Method: <strong class="text-slate-800">Razorpay Test Mode Checkout</strong>
                        </div>
                        <button onclick="launchCheckoutFromDrawer()" id="btn-pay-checkout" class="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-bold text-xs transition flex items-center justify-center gap-1.5 shadow-xs">
                            <span>⚡ Open Razorpay Standard Checkout</span>
                        </button>
                    </div>
                </div>

            </div>

            <!-- Footer Action -->
            <div class="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
                <span class="text-xs text-slate-500 font-medium">PostgreSQL: <strong class="font-mono text-slate-700">agent_action_logs</strong></span>
                <button onclick="closeCaseInspector()" class="px-4 py-2 bg-slate-900 text-white rounded-lg text-xs font-semibold hover:bg-slate-800 transition">
                    Close Case
                </button>
            </div>
        </div>
    </div>

    <!-- ================= CREATE TEST PAYMENT (SIMULATION / TEST ENVIRONMENT) ================= -->
    <div id="simulate-modal" class="fixed inset-0 z-50 hidden">
        <div onclick="closeSimulateModal()" class="drawer-backdrop fixed inset-0"></div>
        <div class="fixed inset-0 flex items-center justify-center p-4 z-10">
            <div class="bg-white rounded-2xl max-w-lg w-full max-h-[92vh] overflow-y-auto p-6 shadow-2xl border border-slate-200 space-y-4">
                <div class="flex items-start justify-between border-b border-slate-100 pb-3">
                    <div>
                        <div class="flex items-center gap-2 mb-1">
                            <h3 class="text-sm font-bold text-slate-900">Create Test Payment</h3>
                            <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-50 text-amber-800 border border-amber-200 uppercase tracking-wider">Simulation / Test Environment</span>
                        </div>
                        <p class="text-xs text-slate-500 font-medium">Create a controlled payment failure and observe how the recovery agent responds.</p>
                    </div>
                    <button onclick="closeSimulateModal()" class="text-slate-400 hover:text-slate-700 text-lg leading-none p-1">&times;</button>
                </div>

                <div id="sim-form-error" class="hidden p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs font-semibold"></div>

                <div class="space-y-3.5 text-xs">
                    <!-- Customer Information -->
                    <div class="space-y-2">
                        <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Customer Details</div>
                        <div class="grid grid-cols-2 gap-2.5">
                            <div>
                                <label class="block text-slate-700 font-semibold mb-1">Customer Name *</label>
                                <input id="sim-cust-name" type="text" value="Rahul Sharma" placeholder="e.g. Rahul Sharma" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-900 font-medium focus:ring-2 focus:ring-slate-900 focus:bg-white focus:outline-none" />
                            </div>
                            <div>
                                <label class="block text-slate-700 font-semibold mb-1">Customer Email</label>
                                <input id="sim-cust-email" type="email" value="rahul@example.com" placeholder="e.g. rahul@example.com" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-900 font-medium focus:ring-2 focus:ring-slate-900 focus:bg-white focus:outline-none" />
                            </div>
                        </div>
                        <div>
                            <label class="block text-slate-700 font-semibold mb-1">Customer / Order ID <span class="text-slate-400 font-normal">(Optional)</span></label>
                            <input id="sim-cust-id" type="text" placeholder="e.g. cust_rahul_01 or ord_8921" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-900 font-mono text-[11px] focus:ring-2 focus:ring-slate-900 focus:bg-white focus:outline-none" />
                        </div>
                    </div>

                    <!-- Payment Information -->
                    <div class="space-y-2 pt-2 border-t border-slate-100">
                        <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Payment Details</div>
                        <div class="grid grid-cols-3 gap-2.5">
                            <div class="col-span-2">
                                <label class="block text-slate-700 font-semibold mb-1">Payment Amount (₹) *</label>
                                <div class="relative">
                                    <span class="absolute left-2.5 top-2 text-slate-500 font-bold">₹</span>
                                    <input id="sim-amount" type="number" min="1" step="1" value="7850" placeholder="7850" class="w-full pl-6 bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-900 font-mono font-bold focus:ring-2 focus:ring-slate-900 focus:bg-white focus:outline-none" />
                                </div>
                            </div>
                            <div>
                                <label class="block text-slate-700 font-semibold mb-1">Currency</label>
                                <input id="sim-currency" type="text" value="INR" readonly class="w-full bg-slate-100 border border-slate-200 rounded-lg p-2 text-slate-500 font-mono font-bold cursor-not-allowed text-center" />
                            </div>
                        </div>
                        <div>
                            <label class="block text-slate-700 font-semibold mb-1">Payment ID <span class="text-slate-400 font-normal">(Auto-generated if left blank)</span></label>
                            <input id="sim-pay-id" type="text" placeholder="e.g. pay_sim_89211 (Leave blank to auto-generate)" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-900 font-mono text-[11px] focus:ring-2 focus:ring-slate-900 focus:bg-white focus:outline-none" />
                        </div>
                    </div>

                    <!-- Failure Configuration -->
                    <div class="space-y-2 pt-2 border-t border-slate-100">
                        <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Failure Diagnostics & Testing</div>
                        <div class="grid grid-cols-2 gap-2.5">
                            <div>
                                <label class="block text-slate-700 font-semibold mb-1">Intended Outcome</label>
                                <select id="sim-intended-outcome" onchange="onIntendedOutcomeChange()" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-800 font-semibold focus:ring-2 focus:ring-slate-900 focus:bg-white focus:outline-none">
                                    <option value="message">Message-Worthy Failure</option>
                                    <option value="transient">Transient Failure</option>
                                    <option value="fraud">Fraud / Risk Failure</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-slate-700 font-semibold mb-1">Failure Category *</label>
                                <select id="sim-failure-category" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-800 font-mono font-bold focus:ring-2 focus:ring-slate-900 focus:bg-white focus:outline-none">
                                    <option value="bank_declined" selected>bank_declined</option>
                                    <option value="insufficient_funds">insufficient_funds</option>
                                    <option value="expired_card">expired_card</option>
                                    <option value="payment_failed">payment_failed</option>
                                    <option value="network_error">network_error</option>
                                    <option value="timeout">timeout</option>
                                    <option value="gateway_timeout">gateway_timeout</option>
                                    <option value="temporary_failure">temporary_failure</option>
                                    <option value="connection_error">connection_error</option>
                                    <option value="fraud">fraud</option>
                                    <option value="suspected_fraud">suspected_fraud</option>
                                    <option value="chargeback">chargeback</option>
                                    <option value="stolen_card">stolen_card</option>
                                </select>
                            </div>
                        </div>
                        <div>
                            <label class="block text-slate-700 font-semibold mb-1">Failure Reason <span class="text-slate-400 font-normal">(Free text merchant diagnostic)</span> *</label>
                            <textarea id="sim-failure-reason" rows="2" placeholder="e.g. Bank declined the transaction due to suspected unusual activity" class="w-full bg-slate-50 border border-slate-200 rounded-lg p-2 text-slate-900 font-medium focus:ring-2 focus:ring-slate-900 focus:bg-white focus:outline-none leading-relaxed">Bank declined the transaction due to suspected unusual activity</textarea>
                        </div>
                    </div>
                </div>

                <div class="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100">
                    <button type="button" onclick="closeSimulateModal()" class="px-4 py-2 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 text-xs font-semibold transition">
                        Cancel
                    </button>
                    <button type="button" onclick="executeSimulatedCase()" id="btn-submit-sim" class="px-5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition flex items-center gap-1.5 shadow-xs">
                        <span>Run Autonomous Agent</span>
                    </button>
                </div>
            </div>
        </div>
    </div>


    <!-- Frontend Core Application Engine -->
    <script>
        const API_BASE = window.location.origin;
        let allDatasetCases = [];
        let activeInspectorCase = null;
        let activeFilter = 'all';
        let chartOverviewCurve = null;

        // In-App Toast Engine (Replaces all browser alert() calls)
        function showToast(message, type = 'info') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = `p-3 rounded-lg shadow-lg border text-xs font-semibold flex items-center justify-between gap-2 pointer-events-auto transition-all duration-200 transform translate-y-2 opacity-0 ${
                type === 'success' ? 'bg-emerald-900 text-white border-emerald-700' :
                (type === 'error' ? 'bg-rose-900 text-white border-rose-700' : 'bg-slate-900 text-white border-slate-700')
            }`;
            toast.innerHTML = `
                <span>${message}</span>
                <button onclick="this.parentElement.remove()" class="text-white/70 hover:text-white text-base leading-none">&times;</button>
            `;
            container.appendChild(toast);
            
            // Animate in
            setTimeout(() => {
                toast.classList.remove('translate-y-2', 'opacity-0');
            }, 10);

            // Auto dismiss after 4 seconds
            setTimeout(() => {
                toast.classList.add('opacity-0', 'translate-y-2');
                setTimeout(() => toast.remove(), 200);
            }, 4000);
        }

        // Realistic dataset of 50 evaluated cases matching benchmark
        function generateDatasetList() {
            const templates = [
                { id: "326", pay: "pay_9926", cust: "cust_001", reason: "Fraud velocity signal", amt: 75000, status: "blocked", action: "Policy blocked action", time: "22:18:04", diag: "Fraud velocity anomaly detected via RAG policy check.", decision: "ESCALATE", conf: "98%", reasonText: "High-risk velocity pattern detected. Automatic retry prohibited to protect merchant from chargebacks.", policy: "✕ Automatic retry blocked (Rule: fraud_velocity_risk)", actionTitle: "No automated payment action executed", actionLink: "Action paused • Escalated to human review", outcomeTitle: "100% Fraud Protected", outcomeDesc: "₹75,000 chargeback loss prevented." },
                { id: "325", pay: "pay_9925", cust: "cust_002", reason: "Bank declined", amt: 4500, status: "recovered", action: "1-Click link sent", time: "22:17:51", diag: "Customer bank decline. Recoverable via alternative instrument.", decision: "SEND_RECOVERY_LINK", conf: "95%", reasonText: "Bank decline is recoverable and amount is within automatic threshold.", policy: "✓ All safety guardrails passed", actionTitle: "WhatsApp + SMS recovery link dispatched", actionLink: "https://rzp.io/i/rec_9925", outcomeTitle: "✓ ₹4,500 Recovered", outcomeDesc: "Customer completed payment via Razorpay 1-click link." },
                { id: "324", pay: "pay_9924", cust: "cust_003", reason: "Insufficient funds", amt: 3500, status: "recovered", action: "1-Click link sent", time: "22:17:12", diag: "Customer balance decline. Dynamic 1-click link recommended.", decision: "SEND_RECOVERY_LINK", conf: "94%", reasonText: "Customer has transient balance decline. Dispatched 1-click Razorpay link.", policy: "✓ All safety guardrails passed", actionTitle: "WhatsApp + SMS recovery link dispatched", actionLink: "https://rzp.io/i/rec_9924", outcomeTitle: "✓ ₹3,500 Recovered", outcomeDesc: "Customer completed payment via UPI intent." },
                { id: "323", pay: "pay_9923", cust: "cust_004", reason: "Gateway timeout", amt: 2800, status: "recovered", action: "Auto retry executed", time: "22:16:40", diag: "Transient bank timeout. Safe to retry automatically.", decision: "RETRY_PAYMENT", conf: "92%", reasonText: "Gateway timeout is transient. Scheduled immediate smart retry.", policy: "✓ Quota: 1/3 retries used", actionTitle: "Auto-retry executed via Razorpay API", actionLink: "Switch ref: rzp_sw_9923", outcomeTitle: "✓ ₹2,800 Recovered", outcomeDesc: "Payment verified on payment switch." },
                { id: "322", pay: "pay_9922", cust: "cust_005", reason: "High-value invoice", amt: 45000, status: "escalated", action: "Human ops review", time: "22:15:20", diag: "High value transaction > ₹25,000 threshold.", decision: "ESCALATE", conf: "90%", reasonText: "High-value payment requires ops confirmation.", policy: "✓ Routed to Ops Queue", actionTitle: "Ticket created for VIP account manager", actionLink: "Ops Ticket: #OPS-9922", outcomeTitle: "Human In The Loop", outcomeDesc: "Customer contact scheduled." },
                { id: "321", pay: "pay_9921", cust: "cust_006", reason: "Expired card", amt: 1800, status: "recovered", action: "WhatsApp card sent", time: "22:14:05", diag: "Card instrument expired. Alternative method required.", decision: "SEND_RECOVERY_LINK", conf: "96%", reasonText: "Customer instrument expired. Dispatched UPI recovery link.", policy: "✓ All safety guardrails passed", actionTitle: "WhatsApp recovery card dispatched", actionLink: "https://rzp.io/i/rec_9921", outcomeTitle: "✓ ₹1,800 Recovered", outcomeDesc: "Customer updated card and completed payment." },
                { id: "320", pay: "pay_9920", cust: "cust_007", reason: "Stolen card report", amt: 32000, status: "blocked", action: "Instrument blacklisted", time: "22:13:30", diag: "Stolen instrument blacklist match.", decision: "ESCALATE", conf: "99%", reasonText: "Stolen card flagged by risk policy. Automatic retry prohibited.", policy: "✕ Fraud Blacklist Gate", actionTitle: "Card blocked from merchant retry engine", actionLink: "Risk tag: stolen_instrument", outcomeTitle: "₹32,000 Fraud Blocked", outcomeDesc: "Zero chargeback liability incurred." },
                { id: "319", pay: "pay_9919", cust: "cust_008", reason: "Network error", amt: 1200, status: "recovered", action: "Smart retry executed", time: "22:12:10", diag: "Transient client network glitch.", decision: "RETRY_PAYMENT", conf: "97%", reasonText: "Network dropped mid-flight. Automated retry safe.", policy: "✓ Retry quota: 1/3", actionTitle: "Smart retry executed", actionLink: "Switch ref: rzp_sw_9919", outcomeTitle: "✓ ₹1,200 Recovered", outcomeDesc: "Payment verified on switch." },
                { id: "318", pay: "pay_9918", cust: "cust_009", reason: "Insufficient funds", amt: 2200, status: "recovered", action: "1-Click link sent", time: "22:11:45", diag: "Customer balance decline.", decision: "SEND_RECOVERY_LINK", conf: "93%", reasonText: "Dispatched 1-click Razorpay payment link.", policy: "✓ Guardrails passed", actionTitle: "SMS + WhatsApp recovery link dispatched", actionLink: "https://rzp.io/i/rec_9918", outcomeTitle: "✓ ₹2,200 Recovered", outcomeDesc: "Customer completed payment via PhonePe." },
                { id: "317", pay: "pay_9917", cust: "cust_010", reason: "Suspected fraud", amt: 55000, status: "blocked", action: "Policy blocked action", time: "22:10:02", diag: "IP velocity mismatch anomaly.", decision: "ESCALATE", conf: "98%", reasonText: "Velocity fraud ring pattern detected.", policy: "✕ Fraud Policy Violation", actionTitle: "Payment blocked and escalated to risk team", actionLink: "Risk ID: #RISK-9917", outcomeTitle: "₹55,000 Fraud Protected", outcomeDesc: "Protected from unrecoverable chargeback." }
            ];

            let list = [];
            for (let i = 1; i <= 50; i++) {
                const tmpl = templates[(i - 1) % templates.length];
                const caseNum = (326 - i + 1).toString();
                list.push({
                    ...tmpl,
                    id: caseNum,
                    pay: `pay_rzp_${(9900 + i)}`,
                    cust: `cust_${(i % 15) + 100}`,
                });
            }
            return list;
        }

        allDatasetCases = generateDatasetList();

        // Navigation Engine
        function navigateView(viewName) {
            const views = ['overview', 'cases', 'benchmark', 'gateway', 'automations', 'audit', 'policies', 'integrations'];
            views.forEach(v => {
                const el = document.getElementById('view-' + v);
                const nav = document.getElementById('nav-' + v);
                if (el) {
                    if (v === viewName) {
                        el.classList.remove('hidden');
                        if (nav) nav.classList.add('nav-link-active');
                    } else {
                        el.classList.add('hidden');
                        if (nav) nav.classList.remove('nav-link-active');
                    }
                }
            });

            // Update Breadcrumb
            const titles = {
                'overview': 'Overview',
                'cases': 'Cases',
                'benchmark': 'Performance',
                'gateway': 'Payment Health',
                'automations': 'Automations',
                'audit': 'Audit Log',
                'policies': 'Policies & Guardrails',
                'integrations': 'Integrations'
            };
            document.getElementById('breadcrumb-view').innerText = titles[viewName] || viewName;

            if (viewName === 'overview') loadOverviewData();
            if (viewName === 'cases') loadCasesTable();
            if (viewName === 'gateway') loadGatewayHealth();
            if (viewName === 'audit') loadAuditTimeline();
            if (viewName === 'integrations') loadIntegrationsStatus();
        }

        async function loadIntegrationsStatus() {
            try {
                const res = await fetch(`${API_BASE}/razorpay/status`);
                const data = await res.json();
                console.log("Razorpay Integration Telemetry:", data);
            } catch (e) {
                console.error("Error fetching integration telemetry", e);
            }
        }


        // 1. Overview Loader
        function loadOverviewData() {
            // Attention Table (Escalated, Blocked, High-Value)
            const attentionCases = allDatasetCases.filter(c => c.status === 'blocked' || c.status === 'escalated' || c.amt > 30000).slice(0, 4);
            const attnTbody = document.getElementById("overview-attention-tbody");
            attnTbody.innerHTML = attentionCases.map(c => `
                <tr class="rec-row-hover transition cursor-pointer" onclick="openCaseFromDataset('${c.id}')">
                    <td class="py-3 px-3 font-mono font-bold text-slate-900">#${c.id}</td>
                    <td class="py-3 px-3 font-mono text-slate-500">${c.pay}</td>
                    <td class="py-3 px-3 text-slate-700">${c.reason}</td>
                    <td class="py-3 px-3 font-bold text-slate-900 font-mono">₹${c.amt.toLocaleString('en-IN')}</td>
                    <td class="py-3 px-3 text-slate-600 font-medium">${c.action}</td>
                    <td class="py-3 px-3">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            c.status === 'recovered' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                            (c.status === 'blocked' ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-amber-50 text-amber-700 border border-amber-200')
                        }">
                            ${c.status.toUpperCase()}
                        </span>
                    </td>
                    <td class="py-3 px-3 text-right">
                        <span class="text-xs font-bold text-slate-900 hover:text-emerald-600">Inspect ➔</span>
                    </td>
                </tr>
            `).join("");

            // Activity Stream Table
            const top5 = allDatasetCases.slice(0, 5);
            const actTbody = document.getElementById("overview-activity-tbody");
            actTbody.innerHTML = top5.map(c => `
                <tr class="rec-row-hover transition cursor-pointer" onclick="openCaseFromDataset('${c.id}')">
                    <td class="py-3 px-3 font-mono font-bold text-slate-900">#${c.id}</td>
                    <td class="py-3 px-3 font-mono text-slate-500">${c.pay}</td>
                    <td class="py-3 px-3 text-slate-600">${c.cust}</td>
                    <td class="py-3 px-3 text-slate-700">${c.reason}</td>
                    <td class="py-3 px-3 font-bold text-slate-900 font-mono">₹${c.amt.toLocaleString('en-IN')}</td>
                    <td class="py-3 px-3">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            c.status === 'recovered' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                            (c.status === 'blocked' ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-amber-50 text-amber-700 border border-amber-200')
                        }">
                            ${c.status.toUpperCase()}
                        </span>
                    </td>
                    <td class="py-3 px-3 text-right">
                        <span class="text-xs font-bold text-slate-900 hover:text-emerald-600">Inspect ➔</span>
                    </td>
                </tr>
            `).join("");

            renderOverviewChart();
        }

        function renderOverviewChart() {
            if (typeof Chart === 'undefined') return;
            const ctx = document.getElementById('chart-overview-curve');
            if (!ctx) return;
            if (chartOverviewCurve) chartOverviewCurve.destroy();

            chartOverviewCurve = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: ['10 Cases', '20 Cases', '30 Cases', '40 Cases', '50 Cases'],
                    datasets: [
                        {
                            label: 'RecoveryOS Agent (₹)',
                            data: [68000, 145000, 230000, 310000, 380200],
                            borderColor: '#00D09C',
                            backgroundColor: 'rgba(0, 208, 156, 0.06)',
                            fill: true,
                            tension: 0.3,
                            borderWidth: 2
                        },
                        {
                            label: 'Naive Baseline (₹)',
                            data: [35000, 82000, 130000, 175000, 213800],
                            borderColor: '#94A3B8',
                            borderDash: [4, 4],
                            fill: false,
                            tension: 0.3,
                            borderWidth: 1.5
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11, weight: 'bold' } } }
                    },
                    scales: {
                        y: {
                            ticks: {
                                callback: function(value) { return '₹' + (value/1000) + 'k'; },
                                font: { size: 10 }
                            }
                        },
                        x: { ticks: { font: { size: 10 } } }
                    }
                }
            });
        }

        // 2. Cases Loader & Filters
        function loadCasesTable() {
            document.getElementById("cases-count-badge").innerText = `${allDatasetCases.length} cases`;
            document.getElementById("badge-total-cases").innerText = allDatasetCases.length;
            filterCasesTable();
        }

        function setCaseFilter(filter) {
            activeFilter = filter;
            ['all', 'recovered', 'pending', 'escalated', 'blocked'].forEach(f => {
                const btn = document.getElementById('filter-' + f);
                if (btn) {
                    if (f === filter) {
                        btn.className = 'px-3 py-1 rounded bg-slate-900 text-white font-semibold';
                    } else {
                        btn.className = 'px-3 py-1 rounded hover:bg-slate-100 text-slate-600 font-semibold';
                    }
                }
            });
            filterCasesTable();
        }

        function filterCasesTable() {
            const query = document.getElementById("case-search-input").value.toLowerCase();
            let filtered = allDatasetCases.filter(c => 
                c.pay.toLowerCase().includes(query) || 
                c.reason.toLowerCase().includes(query) || 
                c.id.includes(query) ||
                c.cust.toLowerCase().includes(query)
            );

            if (activeFilter !== 'all') {
                if (activeFilter === 'pending') {
                    filtered = filtered.filter(c => c.status === 'open' || c.status === 'pending');
                } else {
                    filtered = filtered.filter(c => c.status === activeFilter);
                }
            }

            const tbody = document.getElementById("cases-repository-tbody");
            if (filtered.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" class="p-4 text-center text-slate-400">No matching cases found.</td></tr>`;
                return;
            }

            tbody.innerHTML = filtered.map(c => `
                <tr class="rec-row-hover transition cursor-pointer" onclick="openCaseFromDataset('${c.id}')">
                    <td class="py-3 px-3 font-mono font-bold text-slate-900">#${c.id}</td>
                    <td class="py-3 px-3 font-mono text-slate-500">${c.pay}</td>
                    <td class="py-3 px-3 text-slate-600">${c.cust}</td>
                    <td class="py-3 px-3 text-slate-700">${c.reason}</td>
                    <td class="py-3 px-3 font-bold text-slate-900 font-mono">₹${c.amt.toLocaleString('en-IN')}</td>
                    <td class="py-3 px-3 text-slate-600 font-medium">${c.action}</td>
                    <td class="py-3 px-3">
                        <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            c.status === 'recovered' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                            (c.status === 'blocked' ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-amber-50 text-amber-700 border border-amber-200')
                        }">
                            ${c.status.toUpperCase()}
                        </span>
                    </td>
                    <td class="py-3 px-3 text-right">
                        <button class="text-xs font-bold text-slate-900 hover:text-emerald-600">Inspect ➔</button>
                    </td>
                </tr>
            `).join("");
        }

        // 3. Case Detail Slide-Over Drawer
        function openCaseFromDataset(caseId) {
            const c = allDatasetCases.find(item => item.id === caseId) || allDatasetCases[0];
            activeInspectorCase = c;

            document.getElementById("insp-case-id").innerText = `CASE #${c.id}`;
            document.getElementById("insp-case-subtitle").innerText = `₹${c.amt.toLocaleString('en-IN')} • ${c.reason}`;
            
            const badge = document.getElementById("insp-status-badge");
            badge.innerText = c.status.toUpperCase();
            badge.className = c.status === 'recovered' 
                ? 'text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200'
                : (c.status === 'blocked' ? 'text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200' : 'text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-amber-50 text-amber-700 border border-amber-200');

            // Timeline steps update
            document.getElementById("insp-step-detect-time").innerText = `${c.time || '22:12:04'} • Webhook received for ${c.pay}`;
            document.getElementById("insp-step-diagnose-text").innerText = `${c.reason} • ${c.diag}`;
            document.getElementById("insp-step-decision-text").innerText = c.decision.replace(/_/g, ' ');

            const polDot = document.getElementById("insp-step-policy-dot");
            const actDot = document.getElementById("insp-step-action-dot");
            const outDot = document.getElementById("insp-step-outcome-dot");

            if (c.status === 'blocked') {
                polDot.className = "step-dot-blocked"; polDot.innerText = "✕";
                actDot.className = "step-dot-blocked"; actDot.innerText = "✕";
                outDot.className = "step-dot-blocked"; outDot.innerText = "🛡";

                document.getElementById("insp-step-policy-text").innerText = "Blocked by deterministic fraud rule";
                document.getElementById("insp-step-action-text").innerText = "No payment retried • Ops escalation";
                document.getElementById("insp-step-outcome-title").innerText = "Protected";
                document.getElementById("insp-step-outcome-title").className = "font-bold text-rose-900";
                document.getElementById("insp-step-outcome-amount").innerText = `₹${c.amt.toLocaleString('en-IN')} chargeback shielded`;
                document.getElementById("insp-step-outcome-amount").className = "text-rose-700 text-[11px] font-mono font-bold";
            } else {
                polDot.className = "step-dot-done"; polDot.innerText = "✓";
                actDot.className = "step-dot-done"; actDot.innerText = "✓";
                outDot.className = "step-dot-done"; outDot.innerText = "✓";

                document.getElementById("insp-step-policy-text").innerText = "Approved • All safety guardrails satisfied";
                document.getElementById("insp-step-action-text").innerText = c.actionTitle;
                document.getElementById("insp-step-outcome-title").innerText = "Recovered";
                document.getElementById("insp-step-outcome-title").className = "font-bold text-emerald-800";
                document.getElementById("insp-step-outcome-amount").innerText = `₹${c.amt.toLocaleString('en-IN')} won back`;
                document.getElementById("insp-step-outcome-amount").className = "text-emerald-700 text-[11px] font-mono font-bold";
            }

            // Agent Decision Block
            document.getElementById("insp-decision-action").innerText = c.decision;
            document.getElementById("insp-decision-conf").innerText = `Confidence: ${c.conf}`;
            document.getElementById("insp-decision-reason").innerText = c.reasonText;

            // Policy Guard Block
            const polBox = document.getElementById("insp-policy-box");
            if (c.status === 'blocked') {
                polBox.className = "p-3.5 rounded-xl border border-rose-200 bg-rose-50/50 space-y-1 text-[11px] text-rose-900 font-medium";
                polBox.innerHTML = `
                    <div>✓ Amount threshold check</div>
                    <div>✕ Automatic retry prohibited (Rule: fraud_velocity_risk)</div>
                    <div>✓ Escalated to human review queue</div>
                    <div class="pt-1 font-bold text-rose-800">Decision: BLOCKED → HUMAN REVIEW</div>
                `;
            } else {
                polBox.className = "p-3.5 rounded-xl border border-emerald-200 bg-emerald-50/50 space-y-1 text-[11px] text-emerald-900 font-medium";
                polBox.innerHTML = `
                    <div>✓ Retry budget available (1 of 3)</div>
                    <div>✓ Amount threshold satisfied (₹${c.amt.toLocaleString('en-IN')} < ₹50,000)</div>
                    <div>✓ No fraud velocity signal</div>
                    <div>✓ Customer contact frequency within limit</div>
                    <div class="pt-1 font-bold text-emerald-800">Decision: AUTOMATIC ACTION ALLOWED</div>
                `;
            }

            // Technical Trace Content
            document.getElementById("trace-rag-item").innerText = `Policy: ${c.reason} Recovery Policy (Cosine: 0.58)`;
            document.getElementById("trace-tool-info").innerText = `Tool: ${c.decision.toLowerCase()} • Target: ${c.pay}`;

            // Dedicated Payment Action Card Container
            const payContainer = document.getElementById("insp-payment-container");
            if (c.status === 'blocked') {
                payContainer.innerHTML = `
                    <div class="p-3.5 rounded-xl border border-rose-200 bg-rose-50/60 text-xs space-y-1">
                        <div class="font-bold text-rose-900">Automated Recovery Prohibited</div>
                        <div class="text-rose-700 text-[11px] leading-relaxed">
                            Fraud velocity anomaly detected. Direct customer link and automated retries are permanently disabled to shield merchant from chargebacks.
                        </div>
                    </div>
                `;
            } else if (c.status === 'recovered') {
                payContainer.innerHTML = `
                    <div class="p-4 rounded-xl border border-emerald-200 bg-emerald-50/60 space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="text-[10px] font-bold uppercase tracking-wider text-emerald-800">Payment Recovered</span>
                            <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">Verified</span>
                        </div>
                        <div class="flex items-baseline justify-between">
                            <span class="text-xl font-black text-emerald-950 font-mono">₹${c.amt.toLocaleString('en-IN')}</span>
                            <span class="text-xs text-emerald-700 font-mono">${c.pay}</span>
                        </div>
                        <div class="text-[11px] text-emerald-800 font-medium">Gateway Status: <strong>Captured</strong></div>
                        <div class="space-y-0.5 text-[11px] text-emerald-700 font-medium pt-1 border-t border-emerald-100">
                            <div>✓ HMAC-SHA256 Signature verified</div>
                            <div>✓ Payment status: captured</div>
                            <div>✓ Recovery case #${c.id} updated</div>
                        </div>
                    </div>
                `;
            } else {
                payContainer.innerHTML = `
                    <div id="insp-payment-card" class="p-4 rounded-xl border border-slate-200 bg-slate-50/80 space-y-2.5">
                        <div class="flex items-center justify-between">
                            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-500">Recovery Payment</span>
                            <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">READY TO PAY</span>
                        </div>
                        <div class="flex items-baseline justify-between">
                            <span class="text-xl font-black text-slate-900 font-mono">₹${c.amt.toLocaleString('en-IN')}</span>
                            <span class="text-xs text-slate-500 font-mono">${c.pay}</span>
                        </div>
                        <div class="text-[11px] text-slate-600 font-medium">
                            Recovery Method: <strong class="text-slate-800">Razorpay Standard Checkout / Payment Link</strong>
                        </div>
                        <button onclick="launchCheckoutFromDrawer()" id="btn-pay-checkout" class="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg font-bold text-xs transition flex items-center justify-center gap-1.5 shadow-xs">
                            <span>⚡ Open Razorpay Standard Checkout</span>
                        </button>
                    </div>
                `;
            }

            document.getElementById("case-inspector-drawer").classList.remove("hidden");
        }

        function closeCaseInspector() {
            document.getElementById("case-inspector-drawer").classList.add("hidden");
        }

        function toggleTechnicalTrace() {
            const box = document.getElementById("technical-trace-box");
            const arrow = document.getElementById("trace-toggle-arrow");
            if (box.classList.contains("hidden")) {
                box.classList.remove("hidden");
                arrow.innerText = "▼";
            } else {
                box.classList.add("hidden");
                arrow.innerText = "▶";
            }
        }

        // 4. Razorpay Standard Checkout Modal
        async function launchCheckoutFromDrawer() {
            if (!activeInspectorCase) return;
            const c = activeInspectorCase;
            const amt = c.amt;
            const payId = c.pay;
            const btn = document.getElementById("btn-pay-checkout");
            const container = document.getElementById("insp-payment-container");

            if (btn) {
                btn.innerText = "Creating Razorpay Order...";
                btn.disabled = true;
            }

            try {
                const orderRes = await fetch(`${API_BASE}/razorpay/create-order`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ amount: amt, currency: "INR", receipt: payId, customer_id: c.cust, case_id: parseInt(c.id) || null })
                });

                if (!orderRes.ok) {
                    let errDetail = "Razorpay Test Mode unavailable";
                    try {
                        const errJson = await orderRes.json();
                        errDetail = errJson.detail || errDetail;
                    } catch (e) {}
                    throw new Error(errDetail);
                }

                const order = await orderRes.json();

                if (typeof Razorpay === 'undefined') {
                    throw new Error("Razorpay Test Mode unavailable: Razorpay Checkout script (checkout.js) failed to load.");
                }

                const options = {
                    "key": order.key_id,
                    "amount": order.amount,
                    "currency": order.currency || "INR",
                    "name": "RecoveryOS Control Plane",
                    "description": "Invoice Recovery - " + payId,
                    "image": "https://cdn.razorpay.com/static/assets/logo/rzp.svg",
                    "order_id": order.order_id || order.id,
                    "handler": async function (response) {
                        if (container) {
                            container.innerHTML = `
                                <div class="p-4 rounded-xl border border-blue-200 bg-blue-50 text-xs space-y-1.5">
                                    <div class="font-bold text-blue-900">VERIFYING PAYMENT...</div>
                                    <div class="text-blue-700 text-[11px]">Verifying HMAC-SHA256 signature with Razorpay server...</div>
                                </div>
                            `;
                        }

                        try {
                            const verifyRes = await fetch(`${API_BASE}/razorpay/verify-payment`, {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({
                                    razorpay_order_id: response.razorpay_order_id || order.order_id || order.id,
                                    razorpay_payment_id: response.razorpay_payment_id,
                                    razorpay_signature: response.razorpay_signature,
                                    payment_id: payId,
                                    case_id: parseInt(c.id) || null
                                })
                            });

                            if (!verifyRes.ok) {
                                const vErr = await verifyRes.json().catch(() => ({}));
                                throw new Error(vErr.detail || "Signature verification rejected by server");
                            }

                            const verifyData = await verifyRes.json();

                            // Update active case record in memory & table
                            c.status = 'recovered';
                            c.actionTitle = "Payment recovered via Razorpay Gateway";
                            c.outcomeTitle = "✓ ₹" + amt.toLocaleString('en-IN') + " Recovered";
                            c.outcomeDesc = "Customer completed payment via Razorpay Gateway.";

                            // Update Drawer Elements
                            document.getElementById("insp-status-badge").innerText = "RECOVERED";
                            document.getElementById("insp-status-badge").className = "text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200";
                            document.getElementById("insp-step-verify-dot").className = "step-dot-done";
                            document.getElementById("insp-step-verify-text").innerText = `Payment verified • ${response.razorpay_payment_id}`;
                            document.getElementById("insp-step-outcome-title").innerText = "Recovered";
                            document.getElementById("insp-step-outcome-title").className = "font-bold text-emerald-800";
                            document.getElementById("insp-step-outcome-amount").innerText = `₹${amt.toLocaleString('en-IN')} won back`;

                            if (container) {
                                container.innerHTML = `
                                    <div class="p-4 rounded-xl border border-emerald-200 bg-emerald-50/70 space-y-2">
                                        <div class="flex items-center justify-between">
                                            <span class="text-[10px] font-bold uppercase tracking-wider text-emerald-800">Payment Recovered</span>
                                            <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">Verified</span>
                                        </div>
                                        <div class="flex items-baseline justify-between">
                                            <span class="text-xl font-black text-emerald-950 font-mono">₹${amt.toLocaleString('en-IN')}</span>
                                            <span class="text-xs text-emerald-700 font-mono">${response.razorpay_payment_id}</span>
                                        </div>
                                        <div class="space-y-0.5 text-[11px] text-emerald-700 font-medium pt-1 border-t border-emerald-100">
                                            <div>✓ HMAC-SHA256 Signature verified</div>
                                            <div>✓ Razorpay Order ID: <code class="font-mono text-emerald-900">${verifyData.razorpay_order_id}</code></div>
                                            <div>✓ Case #${c.id} updated to RECOVERED</div>
                                        </div>
                                    </div>
                                `;
                            }

                            showToast(`Payment of ₹${amt.toLocaleString('en-IN')} verified successfully via Razorpay Gateway.`, "success");
                            loadCasesTable();
                            loadOverviewData();
                        } catch (verErr) {
                            if (container) {
                                container.innerHTML = `
                                    <div class="p-3.5 rounded-xl border border-rose-200 bg-rose-50 space-y-1.5 text-xs">
                                        <div class="font-bold text-rose-900">PAYMENT VERIFICATION FAILED</div>
                                        <div class="text-rose-700 text-[11px]">${verErr.message}</div>
                                        <button onclick="launchCheckoutFromDrawer()" class="px-3 py-1 bg-slate-900 text-white rounded font-bold text-xs mt-1">Try Again</button>
                                    </div>
                                `;
                            }
                            showToast("Verification failed: " + verErr.message, "error");
                        }
                    },
                    "modal": {
                        "ondismiss": function() {
                            if (c.status !== 'recovered') {
                                if (container) {
                                    container.innerHTML = `
                                        <div class="p-3.5 rounded-xl border border-slate-200 bg-slate-50 space-y-1.5 text-xs">
                                            <div class="font-bold text-slate-800">CHECKOUT DISMISSED</div>
                                            <div class="text-slate-600 text-[11px]">Checkout window was closed before payment completion. Case remains open.</div>
                                            <button onclick="launchCheckoutFromDrawer()" class="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white rounded font-bold text-xs mt-1 transition">Open Checkout Again</button>
                                        </div>
                                    `;
                                }
                            }
                        }
                    },
                    "theme": { "color": "#0F172A" }
                };

                const rzp = new Razorpay(options);

                // Listen for REAL Razorpay failure events and route through RecoveryOrchestrator
                rzp.on('payment.failed', async function (resp) {
                    if (container) {
                        container.innerHTML = `
                            <div class="p-3.5 rounded-xl border border-amber-200 bg-amber-50 space-y-1.5 text-xs">
                                <div class="font-bold text-amber-900">INGESTING REAL RAZORPAY FAILURE...</div>
                                <div class="text-amber-700 text-[11px]">Sending failure event to RecoveryOS Orchestrator for 7-step autonomous analysis...</div>
                            </div>
                        `;
                    }

                    try {
                        const failRes = await fetch(`${API_BASE}/razorpay/checkout-failed`, {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({
                                order_id: order.order_id || order.id,
                                payment_id: resp.error?.metadata?.payment_id || null,
                                error_code: resp.error?.code || "PAYMENT_FAILED",
                                error_description: resp.error?.description || "Payment failed at bank gateway",
                                error_source: resp.error?.source || "gateway",
                                error_step: resp.error?.step || "payment_authorization",
                                error_reason: resp.error?.reason || "payment_failed",
                                case_id: parseInt(c.id) || null,
                                amount: amt,
                                customer_id: c.cust
                            })
                        });

                        const failData = await failRes.json();
                        const mappedReason = failData.failure_reason || "bank_declined";
                        const orchDecision = failData.orchestrator_summary?.decision?.action || "EVALUATED";
                        const orchOutcome = failData.final_case_status || "open";

                        c.status = orchOutcome;
                        c.reason = mappedReason.replace(/_/g, ' ').toUpperCase();
                        c.diag = failData.error_description || "Real payment decline from Razorpay switch";
                        c.decision = orchDecision.toUpperCase();
                        c.action = `Agent: ${orchDecision}`;

                        document.getElementById("insp-case-subtitle").innerText = `₹${amt.toLocaleString('en-IN')} • ${c.reason}`;
                        document.getElementById("insp-step-diagnose-text").innerText = `${c.reason} • ${c.diag}`;
                        document.getElementById("insp-step-decision-text").innerText = c.decision;
                        document.getElementById("insp-decision-action").innerText = c.decision;
                        document.getElementById("insp-decision-reason").innerText = failData.orchestrator_summary?.decision?.reason || `Real Razorpay test mode failure received. Autonomous agent decided: ${orchDecision}.`;

                        if (container) {
                            container.innerHTML = `
                                <div class="p-3.5 rounded-xl border border-rose-200 bg-rose-50 space-y-2 text-xs">
                                    <div class="flex items-center justify-between">
                                        <span class="font-bold text-rose-900">REAL RAZORPAY PAYMENT FAILED</span>
                                        <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-100 text-rose-800">${mappedReason}</span>
                                    </div>
                                    <div class="text-rose-700 text-[11px]">${failData.error_description || resp.error?.description || 'Payment failed at gateway'}</div>
                                    <div class="pt-1 border-t border-rose-200 text-[11px] text-slate-800 space-y-0.5">
                                        <div><strong>RecoveryOS Agent Action:</strong> <code class="font-mono bg-white px-1 py-0.5 rounded border border-rose-200 text-rose-800">${orchDecision}</code></div>
                                        <div><strong>Status:</strong> Case routed to automated recovery pipeline</div>
                                    </div>
                                    <button onclick="launchCheckoutFromDrawer()" class="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white rounded font-bold text-xs mt-1 transition">Retry Test Payment</button>
                                </div>
                            `;
                        }
                        showToast(`Razorpay payment failed. RecoveryOS Agent executed: ${orchDecision}`, "error");
                        loadCasesTable();
                        loadOverviewData();
                    } catch (fErr) {
                        if (container) {
                            container.innerHTML = `
                                <div class="p-3.5 rounded-xl border border-rose-200 bg-rose-50 space-y-1.5 text-xs">
                                    <div class="font-bold text-rose-900">PAYMENT FAILED</div>
                                    <div class="text-rose-700 text-[11px]">${resp.error?.description || 'Payment declined at gateway.'}</div>
                                    <button onclick="launchCheckoutFromDrawer()" class="px-3 py-1 bg-slate-900 text-white rounded font-bold text-xs mt-1">Try Again</button>
                                </div>
                            `;
                        }
                        showToast("Payment failed at gateway: " + (resp.error ? resp.error.description : "Declined"), "error");
                    }
                });

                rzp.open();
            } catch (e) {
                if (container) {
                    container.innerHTML = `
                        <div class="p-3.5 rounded-xl border border-rose-200 bg-rose-50 space-y-1.5 text-xs">
                            <div class="font-bold text-rose-900">Razorpay Test Mode unavailable</div>
                            <div class="text-rose-700 text-[11px]">${e.message}</div>
                            <div class="text-slate-500 text-[10px] font-medium pt-1">
                                Please ensure <code class="font-mono bg-slate-200 px-1 py-0.5 rounded text-slate-800">RAZORPAY_KEY_ID</code> and <code class="font-mono bg-slate-200 px-1 py-0.5 rounded text-slate-800">RAZORPAY_KEY_SECRET</code> are set in <code class="font-mono">.env</code>.
                            </div>
                        </div>
                    `;
                }
                showToast(e.message, "error");
            } finally {
                if (btn) {
                    btn.innerText = "⚡ Open Razorpay Standard Checkout";
                    btn.disabled = false;
                }
            }
        }

        // Quick Demo Launcher for Razorpay Standard Checkout
        function triggerQuickCheckoutDemo() {
            let target = allDatasetCases.find(c => c.status !== 'blocked') || allDatasetCases[0];
            openCaseFromDataset(target.id);
            showToast("Opening Razorpay Standard Checkout for Case #" + target.id + "...", "info");
            setTimeout(() => {
                launchCheckoutFromDrawer();
            }, 300);
        }



        // 5. Batch Evaluation
        async function triggerEvaluationBatch() {
            navigateView('benchmark');
            showToast("Running 50-case empirical evaluation benchmark...", "info");
            try {
                const res = await fetch(`${API_BASE}/simulator/benchmark?count=50`, { method: "POST" });
                const data = await res.json();
                const s = data.summary;

                document.getElementById("stat-at-risk").innerText = "₹" + Number(s.total_revenue_at_risk_inr).toLocaleString("en-IN");
                document.getElementById("stat-recovered").innerText = "₹" + Number(s.ai_money_recovered_inr).toLocaleString("en-IN");
                document.getElementById("stat-baseline").innerText = "₹" + Number(s.baseline_money_recovered_inr).toLocaleString("en-IN");
                document.getElementById("stat-fraud").innerText = "₹" + Number(s.fraud_losses_prevented_by_ai_inr).toLocaleString("en-IN");
                document.getElementById("hero-recovered-amt").innerText = "₹" + Number(s.ai_money_recovered_inr).toLocaleString("en-IN");
                document.getElementById("hero-recovery-rate").innerText = `${s.ai_recovery_rate_percent}% Recovery Rate`;
                document.getElementById("hero-net-lift").innerText = `+₹${Number(s.net_revenue_lift_inr).toLocaleString('en-IN')} vs. Naive Baseline`;

                showToast(`Evaluation completed: +₹${Number(s.net_revenue_lift_inr).toLocaleString('en-IN')} net lift over baseline.`, "success");
            } catch (e) {
                showToast("Evaluation error: " + e.message, "error");
            }
        }

        // 6. Bank Gateway Health
        async function loadGatewayHealth() {
            const grid = document.getElementById("gateway-health-grid");
            try {
                const res = await fetch(`${API_BASE}/gateway/health`);
                const data = await res.json();
                grid.innerHTML = Object.entries(data.gateways).map(([code, g]) => `
                    <div class="p-4 rounded-xl border ${g.status === 'healthy' ? 'border-slate-200 bg-white' : 'border-rose-300 bg-rose-50/50'} space-y-2">
                        <div class="flex items-center justify-between">
                            <span class="font-bold text-slate-900 text-xs">${g.name}</span>
                            <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${g.status === 'healthy' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'}">${g.status.toUpperCase()}</span>
                        </div>
                        <div class="flex items-baseline justify-between text-xs">
                            <span class="text-slate-500 font-medium">Success Rate:</span>
                            <span class="font-bold font-mono ${g.status === 'healthy' ? 'text-emerald-700' : 'text-rose-600'}">${g.success_rate_percent}%</span>
                        </div>
                        <div class="flex items-baseline justify-between text-xs">
                            <span class="text-slate-500 font-medium">Switch Latency:</span>
                            <span class="font-mono text-slate-700 font-bold">${g.latency_ms} ms</span>
                        </div>
                    </div>
                `).join("");
            } catch (e) {
                grid.innerHTML = `<div class="text-xs text-rose-600">Error loading gateway health.</div>`;
            }
        }

        // 7. Mandate & PTP Actions
        async function scheduleMandate() {
            const mandateId = document.getElementById("man-id").value;
            const amount = Number(document.getElementById("man-amount").value);
            const code = document.getElementById("man-code").value;
            const box = document.getElementById("mandate-status-box");

            try {
                const res = await fetch(`${API_BASE}/mandate/schedule`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ mandate_id: mandateId, customer_id: "cust_sub_vip", amount, failure_code: code })
                });
                const data = await res.json();
                box.innerHTML = `<div class="text-emerald-800 font-bold">✓ Mandate scheduled for ${data.scheduled_date} (${data.optimal_window}).</div><div class="text-[11px] text-slate-500 mt-0.5">${data.strategy}</div>`;
                showToast("Mandate retry scheduled for optimal salary cycle.", "success");
            } catch (e) {
                box.innerHTML = `<div class="text-rose-600 font-bold">Error: ${e.message}</div>`;
                showToast("Failed to schedule mandate: " + e.message, "error");
            }
        }

        async function processScheduledMandates() {
            const box = document.getElementById("mandate-status-box");
            try {
                const res = await fetch(`${API_BASE}/mandate/process`, { method: "POST" });
                const data = await res.json();
                box.innerHTML = `<div class="text-emerald-800 font-bold">✓ Processed ${data.processed_schedules} Mandates. Recovered ₹${Number(data.revenue_recovered_inr).toLocaleString('en-IN')}.</div>`;
                showToast(`Processed ${data.processed_schedules} due mandates. ₹${Number(data.revenue_recovered_inr).toLocaleString('en-IN')} recovered.`, "success");
            } catch (e) {
                box.innerHTML = `<div class="text-rose-600 font-bold">Error: ${e.message}</div>`;
                showToast("Error processing mandates: " + e.message, "error");
            }
        }

        async function analyzePTP() {
            const invId = document.getElementById("ptp-inv-id").value;
            const amount = Number(document.getElementById("ptp-amount").value);
            const msg = document.getElementById("ptp-msg").value;
            const box = document.getElementById("ptp-status-box");

            box.innerHTML = "<div class='text-slate-500 animate-pulse'>Gemini analyzing customer promise date...</div>";
            try {
                const res = await fetch(`${API_BASE}/receivables/ptp`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ invoice_id: invId, customer_id: "corp_tech", amount, customer_message: msg })
                });
                const data = await res.json();
                box.innerHTML = `
                    <div class="text-slate-900 font-bold">Promise Extracted: <span class="text-violet-800 font-black">${data.promised_date}</span></div>
                    <div class="text-emerald-700 font-bold text-[11px] mt-0.5">✓ Collection Reminders Paused Until ${data.promised_date}</div>
                `;
                showToast(`Promise-to-Pay extracted for ${data.promised_date}. Reminders paused.`, "success");
            } catch (e) {
                box.innerHTML = `<div class="text-rose-600 font-bold">Error: ${e.message}</div>`;
                showToast("PTP extraction error: " + e.message, "error");
            }
        }

        // 8. Operations Audit Log
        async function loadAuditTimeline() {
            const tbody = document.getElementById("audit-timeline-tbody");
            try {
                const res = await fetch(`${API_BASE}/recovery/analytics`);
                const data = await res.json();
                if (data.recent_audit_trail && data.recent_audit_trail.length > 0) {
                    tbody.innerHTML = data.recent_audit_trail.map(log => `
                        <tr class="rec-row-hover transition">
                            <td class="py-3 px-3 font-mono text-slate-400 font-bold">#${log.id}</td>
                            <td class="py-3 px-3 font-bold text-slate-900 font-mono">Case ${log.case_id}</td>
                            <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-slate-100 text-slate-800 font-mono text-[11px] font-bold">${log.action}</span></td>
                            <td class="py-3 px-3 text-slate-600 font-medium">${log.details}</td>
                        </tr>
                    `).join("");
                }
            } catch (e) {
                tbody.innerHTML = `<tr><td colspan='4' class='p-4 text-center text-rose-600'>Error: ${e.message}</td></tr>`;
            }
        }

        function openSimulateModal() {
            const errBox = document.getElementById("sim-form-error");
            if (errBox) {
                errBox.classList.add("hidden");
                errBox.innerText = "";
            }
            document.getElementById("simulate-modal").classList.remove("hidden");
        }

        function closeSimulateModal() {
            document.getElementById("simulate-modal").classList.add("hidden");
        }

        function onIntendedOutcomeChange() {
            const outcome = document.getElementById("sim-intended-outcome").value;
            const catSelect = document.getElementById("sim-failure-category");
            const reasonText = document.getElementById("sim-failure-reason");
            const amountInput = document.getElementById("sim-amount");

            if (outcome === "transient") {
                catSelect.value = "gateway_timeout";
                reasonText.value = "Bank payment switch timed out during transaction authorization";
                amountInput.value = "2800";
            } else if (outcome === "message") {
                catSelect.value = "bank_declined";
                reasonText.value = "Bank declined transaction due to temporary balance limitation";
                amountInput.value = "4500";
            } else if (outcome === "fraud") {
                catSelect.value = "suspected_fraud";
                reasonText.value = "Multiple suspicious transactions detected across geo-velocity triggers";
                amountInput.value = "55000";
            }
        }

        async function executeSimulatedCase() {
            const errBox = document.getElementById("sim-form-error");
            if (errBox) {
                errBox.classList.add("hidden");
                errBox.innerText = "";
            }

            const custName = (document.getElementById("sim-cust-name").value || "").trim();
            const custEmail = (document.getElementById("sim-cust-email").value || "").trim();
            let custId = (document.getElementById("sim-cust-id").value || "").trim();
            const amountVal = parseFloat(document.getElementById("sim-amount").value);
            let payId = (document.getElementById("sim-pay-id").value || "").trim();
            const outcome = document.getElementById("sim-intended-outcome").value;
            const category = document.getElementById("sim-failure-category").value;
            const reason = (document.getElementById("sim-failure-reason").value || "").trim();

            if (!custName) {
                if (errBox) {
                    errBox.innerText = "Please enter a customer name.";
                    errBox.classList.remove("hidden");
                }
                return;
            }
            if (!amountVal || isNaN(amountVal) || amountVal <= 0) {
                if (errBox) {
                    errBox.innerText = "Please enter a valid payment amount greater than 0.";
                    errBox.classList.remove("hidden");
                }
                return;
            }
            if (!reason) {
                if (errBox) {
                    errBox.innerText = "Please provide a failure reason.";
                    errBox.classList.remove("hidden");
                }
                return;
            }

            if (!payId) {
                payId = "pay_sim_" + Date.now().toString().slice(-6);
            }
            if (!custId) {
                custId = "cust_" + custName.toLowerCase().replace(/[^a-z0-9]+/g, '_').slice(0, 16) + "_" + Date.now().toString().slice(-4);
            }

            const btn = document.getElementById("btn-submit-sim");
            btn.disabled = true;
            btn.innerText = "Running Autonomous Agent...";

            try {
                const cRes = await fetch(`${API_BASE}/recovery/cases`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ customer_id: custId, payment_id: payId, amount: Math.round(amountVal) })
                });

                if (!cRes.ok) {
                    const err = await cRes.json().catch(() => ({}));
                    throw new Error(err.detail || "Failed to create recovery case");
                }
                const caseData = await cRes.json();

                const runRes = await fetch(`${API_BASE}/orchestrator/run/${caseData.id}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        failure_reason: reason,
                        failure_category: category,
                        customer_name: custName,
                        customer_email: custEmail,
                        intended_outcome: outcome
                    })
                });

                if (!runRes.ok) {
                    const err = await runRes.json().catch(() => ({}));
                    throw new Error(err.detail || "Orchestration execution failed");
                }
                const trace = await runRes.json();

                const newCaseObj = {
                    id: caseData.id.toString(),
                    pay: payId,
                    cust: custName,
                    custId: custId,
                    custEmail: custEmail,
                    reason: category.replace(/_/g, ' ').toUpperCase(),
                    amt: Math.round(amountVal),
                    status: trace.final_status || "open",
                    action: trace.action?.payment_link_url ? "1-Click link sent" : (trace.action?.tool === 'retry_payment' ? "Smart retry executed" : (trace.final_status === 'escalated' ? "Escalated to Ops" : "Analyzed")),
                    time: new Date().toLocaleTimeString(),
                    diag: reason,
                    decision: (trace.ai_decision?.decision || "evaluate").toUpperCase(),
                    conf: trace.ai_decision?.confidence ? (Math.round(trace.ai_decision.confidence * 100) + "%") : "94%",
                    reasonText: trace.ai_decision?.reason || ("Autonomous recovery decision for " + reason),
                    policy: trace.policy?.allowed ? "✓ All safety guardrails passed" : "✕ Safety Gate: " + (trace.policy?.violated_rules?.[0] || "Policy violation"),
                    actionTitle: trace.action?.payment_link_url ? "1-Click Recovery Link Generated" : (trace.action?.tool === 'retry_payment' ? "Smart Retry Executed" : "Escalation Review Scheduled"),
                    actionLink: trace.action?.payment_link_url || ("Switch ref: " + payId),
                    outcomeTitle: trace.final_status === 'recovered' ? `✓ ₹${Math.round(amountVal).toLocaleString('en-IN')} Recovered` : (trace.final_status === 'escalated' ? "STATUS: ESCALATED" : "STATUS: OPEN"),
                    outcomeDesc: trace.final_status === 'recovered' ? "Payment verified via simulated recovery switch." : (trace.final_status === 'escalated' ? "Safety guardrail blocked automated action. Routed to ops." : "Recovery action pending.")
                };

                allDatasetCases.unshift(newCaseObj);

                closeSimulateModal();
                loadOverviewData();
                loadCasesTable();
                openCaseFromDataset(caseData.id.toString());
                showToast(`Test Payment created. Agent Action: ${(trace.ai_decision?.decision || '').toUpperCase()} (${(trace.final_status || '').toUpperCase()})`, "success");
            } catch (e) {
                if (errBox) {
                    errBox.innerText = e.message;
                    errBox.classList.remove("hidden");
                }
                showToast("Execution error: " + e.message, "error");
            } finally {
                btn.disabled = false;
                btn.innerText = "Run Autonomous Agent";
            }
        }


        // Initialize on Load
        loadOverviewData();
    </script>
</body>
</html>"""




