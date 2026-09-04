# main.py
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from agent import run_reconciliation

app = FastAPI(title="RightsLedger Agent")
logger = logging.getLogger("RightsLedgerWeb")

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RightsLedger | Autonomous Royalty & Rights Reconciliation Agent</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-primary: #0a0f1d;
                --bg-card: rgba(18, 26, 47, 0.75);
                --bg-card-hover: rgba(24, 34, 61, 0.9);
                --border-color: rgba(255, 255, 255, 0.08);
                --accent-blue: #38bdf8;
                --accent-purple: #a855f7;
                --accent-orange: #f97316;
                --accent-green: #10b981;
                --accent-red: #ef4444;
                --text-primary: #f8fafc;
                --text-muted: #94a3b8;
                --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                --font-mono: 'JetBrains Mono', monospace;
            }

            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                font-family: var(--font-sans);
                background-color: var(--bg-primary);
                background-image: 
                    radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.12) 0px, transparent 50%),
                    radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.1) 0px, transparent 50%);
                color: var(--text-primary);
                min-height: 100vh;
                padding: 32px 24px;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
            }

            /* Header Section */
            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 32px;
                padding-bottom: 24px;
                border-bottom: 1px solid var(--border-color);
            }

            .brand-group {
                display: flex;
                align-items: center;
                gap: 16px;
            }

            .logo-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, #38bdf8, #818cf8);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                box-shadow: 0 8px 24px rgba(56, 189, 248, 0.25);
            }

            .brand-text h1 {
                font-size: 24px;
                font-weight: 800;
                letter-spacing: -0.5px;
                background: linear-gradient(to right, #ffffff, #94a3b8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .brand-text p {
                font-size: 13px;
                color: var(--text-muted);
                margin-top: 2px;
            }

            .track-badges {
                display: flex;
                gap: 10px;
            }

            .badge {
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                border: 1px solid transparent;
            }

            .badge-clickhouse {
                background: rgba(249, 115, 22, 0.15);
                color: #fb923c;
                border-color: rgba(249, 115, 22, 0.3);
            }

            .badge-gemini {
                background: rgba(168, 85, 247, 0.15);
                color: #c084fc;
                border-color: rgba(168, 85, 247, 0.3);
            }

            .badge-mcp {
                background: rgba(56, 189, 248, 0.15);
                color: #38bdf8;
                border-color: rgba(56, 189, 248, 0.3);
            }

            /* Main Action Bar */
            .action-bar {
                background: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 32px;
                backdrop-filter: blur(12px);
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
            }

            .action-info h2 {
                font-size: 18px;
                font-weight: 700;
                margin-bottom: 4px;
            }

            .action-info p {
                font-size: 14px;
                color: var(--text-muted);
            }

            .btn-audit {
                padding: 14px 28px;
                background: linear-gradient(135deg, #38bdf8, #2563eb);
                border: none;
                border-radius: 10px;
                font-weight: 700;
                font-size: 15px;
                color: #ffffff;
                cursor: pointer;
                transition: all 0.2s ease;
                box-shadow: 0 8px 20px rgba(56, 189, 248, 0.3);
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .btn-audit:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 12px 24px rgba(56, 189, 248, 0.45);
            }

            .btn-audit:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }

            /* Metrics Row */
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
                gap: 20px;
                margin-bottom: 32px;
            }

            .metric-card {
                background: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 14px;
                padding: 20px;
                backdrop-filter: blur(8px);
            }

            .metric-label {
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: var(--text-muted);
                font-weight: 600;
                margin-bottom: 8px;
            }

            .metric-value {
                font-size: 28px;
                font-weight: 800;
                color: var(--text-primary);
            }

            .metric-sub {
                font-size: 12px;
                color: var(--accent-green);
                margin-top: 4px;
                display: flex;
                align-items: center;
                gap: 4px;
            }

            /* Status & Pipeline Stepper */
            .status-container {
                background: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 14px;
                padding: 20px;
                margin-bottom: 32px;
                display: none;
            }

            .status-header {
                display: flex;
                align-items: center;
                gap: 12px;
                font-weight: 600;
                font-size: 14px;
                margin-bottom: 16px;
            }

            .spinner {
                width: 18px;
                height: 18px;
                border: 2px solid rgba(56, 189, 248, 0.2);
                border-top-color: var(--accent-blue);
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
            }

            @keyframes spin { to { transform: rotate(360deg); } }

            .stepper {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 12px;
            }

            .step {
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid var(--border-color);
                padding: 12px;
                border-radius: 8px;
                font-size: 12px;
            }

            .step.active {
                border-color: var(--accent-blue);
                background: rgba(56, 189, 248, 0.08);
            }

            .step.done {
                border-color: var(--accent-green);
                color: var(--accent-green);
            }

            /* Discrepancy Cards List */
            .section-title {
                font-size: 20px;
                font-weight: 700;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }

            .cards-list {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }

            .discrepancy-card {
                background: var(--bg-card);
                border: 1px solid var(--border-color);
                border-radius: 16px;
                padding: 24px;
                transition: all 0.2s ease;
                backdrop-filter: blur(10px);
            }

            .discrepancy-card:hover {
                background: var(--bg-card-hover);
                border-color: rgba(255, 255, 255, 0.15);
            }

            .card-top {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 16px;
            }

            .title-meta h3 {
                font-size: 18px;
                font-weight: 700;
                color: #ffffff;
            }

            .title-meta .meta-tags {
                display: flex;
                gap: 8px;
                margin-top: 6px;
            }

            .tag {
                font-size: 11px;
                padding: 3px 8px;
                border-radius: 4px;
                background: rgba(255, 255, 255, 0.06);
                color: var(--text-muted);
            }

            .badge-type {
                font-size: 12px;
                font-weight: 700;
                padding: 4px 10px;
                border-radius: 6px;
            }

            .badge-underpayment {
                background: rgba(239, 68, 68, 0.15);
                color: #f87171;
                border: 1px solid rgba(239, 68, 68, 0.3);
            }

            .badge-overpayment {
                background: rgba(245, 158, 11, 0.15);
                color: #fbbf24;
                border: 1px solid rgba(245, 158, 11, 0.3);
            }

            /* Financial Numbers Grid */
            .financial-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                background: rgba(0, 0, 0, 0.25);
                border-radius: 10px;
                padding: 14px 18px;
                margin-bottom: 16px;
                border: 1px solid rgba(255, 255, 255, 0.04);
            }

            .fin-col .label {
                font-size: 11px;
                color: var(--text-muted);
                text-transform: uppercase;
                margin-bottom: 4px;
            }

            .fin-col .num {
                font-size: 16px;
                font-family: var(--font-mono);
                font-weight: 700;
            }

            .fin-col .num.negative {
                color: #f87171;
            }

            /* Explanation Box */
            .explanation-box {
                background: rgba(56, 189, 248, 0.04);
                border-left: 3px solid var(--accent-blue);
                padding: 12px 16px;
                border-radius: 0 8px 8px 0;
                font-size: 13px;
                line-height: 1.5;
                color: #cbd5e1;
                margin-bottom: 16px;
            }

            /* Resolution Email Drawer */
            .email-section {
                border-top: 1px solid var(--border-color);
                padding-top: 16px;
            }

            .email-toggle {
                background: none;
                border: none;
                color: var(--accent-blue);
                font-size: 13px;
                font-weight: 600;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 6px;
                padding: 0;
            }

            .email-toggle:hover {
                text-decoration: underline;
            }

            .email-content {
                display: none;
                margin-top: 12px;
                background: #0f172a;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                padding: 16px;
                font-family: var(--font-mono);
                font-size: 12px;
                line-height: 1.6;
                color: #e2e8f0;
                white-space: pre-wrap;
                position: relative;
            }

            .btn-copy {
                position: absolute;
                top: 12px;
                right: 12px;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid var(--border-color);
                color: #ffffff;
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 11px;
                cursor: pointer;
            }

            .btn-copy:hover {
                background: rgba(255, 255, 255, 0.2);
            }

            /* Raw JSON Toggle */
            .json-toggle-wrap {
                margin-top: 32px;
                text-align: center;
            }

            .btn-raw {
                background: none;
                border: 1px dashed var(--border-color);
                color: var(--text-muted);
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
                cursor: pointer;
            }

            .raw-output-pre {
                display: none;
                margin-top: 16px;
                background: #0f172a;
                padding: 16px;
                border-radius: 8px;
                font-family: var(--font-mono);
                font-size: 12px;
                color: #94a3b8;
                text-align: left;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="brand-group">
                    <div class="logo-icon">🎬</div>
                    <div class="brand-text">
                        <h1>RightsLedger Agent</h1>
                        <p>Autonomous Royalty & Rights Reconciliation Engine</p>
                    </div>
                </div>
                <div class="track-badges">
                    <span class="badge badge-clickhouse">⚡ ClickHouse Cloud</span>
                    <span class="badge badge-mcp">🔌 MCP stdio</span>
                    <span class="badge badge-gemini">✨ Gemini 3.6 Flash</span>
                </div>
            </header>

            <section class="action-bar">
                <div class="action-info">
                    <h2>Auditing: <code>rightsledger-dev</code> Cluster</h2>
                    <p>Cross-references streaming play telemetry against contracted licensing rate cards.</p>
                </div>
                <button class="btn-audit" id="btn-run" onclick="triggerAudit()">
                    <span>⚡ Run Autonomous Reconciliation</span>
                </button>
            </section>

            <!-- Metrics -->
            <div class="metrics-grid" id="metrics-section" style="display: none;">
                <div class="metric-card">
                    <div class="metric-label">Discrepancies Flagged</div>
                    <div class="metric-value" id="m-flagged">0</div>
                    <div class="metric-sub">Threshold > 2% variance</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Net Unrecovered Revenue</div>
                    <div class="metric-value" id="m-leakage" style="color: #f87171;">$0.00</div>
                    <div class="metric-sub">Distributor Underpayments</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Security Gate Defense</div>
                    <div class="metric-value" id="m-security" style="color: #10b981;">ACTIVE</div>
                    <div class="metric-sub" id="m-security-sub">0 Injections Blocked</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Audit Trail Writeback</div>
                    <div class="metric-value" id="m-audit" style="color: #38bdf8;">100%</div>
                    <div class="metric-sub">Persisted via MCP to ClickHouse</div>
                </div>
            </div>

            <!-- Pipeline Status Stepper -->
            <div class="status-container" id="status-box">
                <div class="status-header">
                    <div class="spinner" id="status-spinner"></div>
                    <span id="status-text">Initializing mcp-clickhouse stdio session...</span>
                </div>
                <div class="stepper" style="grid-template-columns: repeat(5, 1fr);">
                    <div class="step" id="step-1">1. Spawn MCP</div>
                    <div class="step" id="step-2">2. Fetch & Validate Data</div>
                    <div class="step" id="step-3">3. Gemini Flash Reasoning</div>
                    <div class="step" id="step-4">4. Policy & Security Gate</div>
                    <div class="step" id="step-5">5. Commit Audit Trails</div>
                </div>
            </div>

            <!-- Security Defense Banner -->
            <div id="security-alerts-area" style="display: none; margin-bottom: 32px;"></div>

            <!-- Discrepancy Results -->
            <div id="results-area" style="display: none;">
                <div class="section-title">
                    <span>Audit Findings & Dispute Communications</span>
                </div>
                <div class="cards-list" id="cards-container"></div>
            </div>

            <!-- Raw JSON Drawer -->
            <div class="json-toggle-wrap">
                <button class="btn-raw" onclick="toggleRaw()">View Raw MCP Tool Payload & Audit Telemetry</button>
                <pre class="raw-output-pre" id="raw-json"></pre>
            </div>
        </div>

        <script>
            function toggleRaw() {
                const pre = document.getElementById('raw-json');
                pre.style.display = pre.style.display === 'block' ? 'none' : 'block';
            }

            function toggleEmail(id) {
                const el = document.getElementById('email-' + id);
                el.style.display = el.style.display === 'block' ? 'none' : 'block';
            }

            function copyEmail(id) {
                const text = document.getElementById('email-text-' + id).innerText;
                navigator.clipboard.writeText(text).then(() => {
                    alert('Draft dispute communication copied to clipboard!');
                });
            }

            function formatCurrency(val) {
                return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
            }

            async function triggerAudit() {
                const btn = document.getElementById('btn-run');
                const statusBox = document.getElementById('status-box');
                const statusText = document.getElementById('status-text');
                const resultsArea = document.getElementById('results-area');
                const metricsSection = document.getElementById('metrics-section');
                const securityAlertsArea = document.getElementById('security-alerts-area');
                const cardsContainer = document.getElementById('cards-container');
                const rawPre = document.getElementById('raw-json');

                btn.disabled = true;
                btn.innerHTML = '<span>⏳ Processing Audit...</span>';
                statusBox.style.display = 'block';
                resultsArea.style.display = 'none';
                securityAlertsArea.style.display = 'none';
                securityAlertsArea.innerHTML = '';

                // Stepper animation
                document.getElementById('step-1').className = 'step active';
                document.getElementById('step-2').className = 'step';
                document.getElementById('step-3').className = 'step';
                document.getElementById('step-4').className = 'step';
                document.getElementById('step-5').className = 'step';
                statusText.innerText = 'Connecting to mcp-clickhouse via stdio...';

                setTimeout(() => {
                    document.getElementById('step-1').className = 'step done';
                    document.getElementById('step-2').className = 'step active';
                    statusText.innerText = 'Querying ClickHouse Cloud (JOIN reported_plays & expected_rates)...';
                }, 600);

                setTimeout(() => {
                    document.getElementById('step-2').className = 'step done';
                    document.getElementById('step-3').className = 'step active';
                    statusText.innerText = 'Gemini 3.6 Flash reasoning over isolated untrusted data payload...';
                }, 1200);

                setTimeout(() => {
                    document.getElementById('step-3').className = 'step done';
                    document.getElementById('step-4').className = 'step active';
                    statusText.innerText = 'Executing Deterministic Policy Gate & checking math integrity...';
                }, 2000);

                try {
                    const res = await fetch('/api/reconcile', { method: 'POST' });
                    const data = await res.json();
                    
                    if (!res.ok) {
                        throw new Error(data.detail || 'Server encountered an error during reconciliation');
                    }

                    document.getElementById('step-4').className = 'step done';
                    document.getElementById('step-5').className = 'step done';
                    statusText.innerText = 'Reconciliation complete! Audit trails and security events committed to ClickHouse.';
                    document.getElementById('status-spinner').style.display = 'none';

                    const payload = typeof data.agent_output === 'string' ? JSON.parse(data.agent_output) : data.agent_output;
                    const items = payload.discrepancies || (Array.isArray(payload) ? payload : []);
                    const securityEvents = payload.security_events || [];
                    
                    // Render Metrics
                    let netLeakage = 0;
                    items.forEach(item => {
                        if (item.delta < 0) netLeakage += Math.abs(item.delta);
                    });

                    document.getElementById('m-flagged').innerText = items.length;
                    document.getElementById('m-leakage').innerText = formatCurrency(netLeakage);
                    
                    if (securityEvents.length > 0) {
                        document.getElementById('m-security').innerText = `${securityEvents.length} BLOCKED`;
                        document.getElementById('m-security').style.color = '#ef4444';
                        document.getElementById('m-security-sub').innerText = 'Prompt Injection Neutralized';
                    } else {
                        document.getElementById('m-security').innerText = 'SECURE';
                        document.getElementById('m-security').style.color = '#10b981';
                        document.getElementById('m-security-sub').innerText = 'All Untrusted Data Validated';
                    }

                    metricsSection.style.display = 'grid';

                    // Render Security Event Banner
                    if (securityEvents.length > 0) {
                        securityAlertsArea.innerHTML = '';
                        securityEvents.forEach(sec => {
                            const secCard = `
                            <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-left: 5px solid #ef4444; border-radius: 12px; padding: 20px; backdrop-filter: blur(8px);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                    <div style="display: flex; align-items: center; gap: 8px;">
                                        <span style="font-size: 18px;">🛡️</span>
                                        <strong style="color: #f87171; font-size: 15px;">Prompt Injection Attempt Blocked by Policy Gate</strong>
                                    </div>
                                    <span style="font-size: 11px; font-weight: 700; background: rgba(239, 68, 68, 0.2); color: #fca5a5; padding: 3px 8px; border-radius: 4px;">TARGET ID: ${sec.id}</span>
                                </div>
                                <p style="font-size: 13px; color: #cbd5e1; margin-bottom: 8px;">
                                    <strong>Untrusted Source:</strong> <code>${sec.distributor}</code> | <strong>Title Metadata:</strong> <code>${sec.title}</code>
                                </p>
                                <div style="background: rgba(0, 0, 0, 0.3); padding: 10px 14px; border-radius: 6px; font-size: 12px; color: #fca5a5; font-family: var(--font-mono); margin-bottom: 8px;">
                                    🚨 ${sec.flags.join('<br>🚨 ')}
                                </div>
                                <div style="font-size: 12px; color: #86efac; display: flex; align-items: center; gap: 6px;">
                                    <span>✅</span> <strong>Defense Enforcement:</strong> ${sec.action_taken}
                                </div>
                            </div>
                            `;
                            securityAlertsArea.insertAdjacentHTML('beforeend', secCard);
                        });
                        securityAlertsArea.style.display = 'block';
                    }

                    // Render Discrepancy Cards
                    cardsContainer.innerHTML = '';
                    items.forEach((item, idx) => {
                        const isUnder = item.discrepancy_type === 'UNDERPAYMENT';
                        const badgeClass = isUnder ? 'badge-underpayment' : 'badge-overpayment';
                        const deltaSign = item.delta > 0 ? '+' : '';
                        const isAttackItem = item.id.includes('ATTACK') || (item.security_flags && item.security_flags.length > 0);

                        const cardHtml = `
                        <div class="discrepancy-card" style="${isAttackItem ? 'border-color: rgba(239, 68, 68, 0.35);' : ''}">
                            <div class="card-top">
                                <div class="title-meta">
                                    <h3>${item.title}</h3>
                                    <div class="meta-tags">
                                        <span class="tag">ID: <strong>${item.id}</strong></span>
                                        <span class="tag">Distributor: <strong>${item.distributor}</strong></span>
                                        <span class="tag">Period: ${item.period_start} → ${item.period_end}</span>
                                        ${item.confidence ? `<span class="tag" style="color: #38bdf8;">Confidence: ${(item.confidence * 100).toFixed(0)}%</span>` : ''}
                                        ${isAttackItem ? `<span class="tag" style="background: rgba(239, 68, 68, 0.2); color: #fca5a5; font-weight: 600;">🛡️ Defense Verified</span>` : ''}
                                    </div>
                                </div>
                                <span class="badge-type ${badgeClass}">${item.discrepancy_type}</span>
                            </div>

                            <div class="financial-grid">
                                <div class="fin-col">
                                    <div class="label">Reported Payout</div>
                                    <div class="num">${formatCurrency(item.reported_payout)}</div>
                                </div>
                                <div class="fin-col">
                                    <div class="label">Expected Payout</div>
                                    <div class="num">${formatCurrency(item.expected_payout)}</div>
                                </div>
                                <div class="fin-col">
                                    <div class="label">Discrepancy (Delta)</div>
                                    <div class="num ${item.delta < 0 ? 'negative' : ''}">${deltaSign}${formatCurrency(item.delta)}</div>
                                </div>
                            </div>

                            <div class="explanation-box">
                                <strong>Root Cause Analysis:</strong> ${item.explanation}
                            </div>

                            <div class="email-section">
                                <button class="email-toggle" onclick="toggleEmail('${item.id}')">
                                    <span>✉️ View Auto-Drafted Dispute Letter</span>
                                </button>
                                <div class="email-content" id="email-${item.id}">
                                    <button class="btn-copy" onclick="copyEmail('${item.id}')">📋 Copy Notice</button>
                                    <div id="email-text-${item.id}">${item.resolution_draft}</div>
                                </div>
                            </div>
                        </div>
                        `;
                        cardsContainer.insertAdjacentHTML('beforeend', cardHtml);
                    });

                    rawPre.innerText = JSON.stringify(payload, null, 2);
                    resultsArea.style.display = 'block';

                } catch (err) {
                    statusText.innerText = 'Error: ' + err.message;
                    document.getElementById('status-spinner').style.display = 'none';
                } finally {
                    btn.disabled = false;
                    btn.innerHTML = '<span>⚡ Re-Run Autonomous Reconciliation</span>';
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/reconcile")
async def trigger_reconcile():
    """
    Catches exceptions raised from the agent pipeline 
    and returns an HTTP 500 status with error details.
    """
    try:
        result = await run_reconciliation()
        return {"status": "success", "agent_output": result}
    except Exception as e:
        logger.error(f"API reconciliation route failure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)