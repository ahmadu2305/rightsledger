# RightsLedger: Autonomous Royalty & Rights Reconciliation Agent

RightsLedger is an autonomous financial intelligence agent built for the Google Cloud **"Agentic Cinema: The Blockbuster Hackathon"** (ClickHouse Partner Track). It automates the reconciliation of media licensing and streaming telemetry statements against contracted rate cards, flags discrepancies, reasons over root causes, drafts distributor dispute communications, and writes persistent audit records back to ClickHouse Cloud via Model Context Protocol (MCP).

---

## 🎬 Problem Statement & Industry Impact

In the media, entertainment, and streaming distribution ecosystem, rights holders and independent studios receive monthly and quarterly royalty statements across dozens of platforms (e.g., Netflix, Prime Video, Hulu, Disney+).

* **Revenue Leakage:** Industry studies show 8% to 15% of digital royalty statements contain underreporting, tier mismatches, or missing play periods.
* **Audit Latency:** Manually cross-referencing millions of play event logs against dynamic, territory-specific rate cards in spreadsheets takes accounting teams weeks—often blowing past 60-day contractual dispute windows.
* **The Solution:** RightsLedger runs continuous, high-speed joins on streaming telemetry in ClickHouse Cloud, invokes Gemini to analyze discrepancies > 2%, drafts dispute notices, and commits audit trails autonomously.

---

## 🏗️ Architecture

```mermaid
graph TD
    User["Catalog Manager / Accountant UI"] -->|"Trigger Audit"| FastAPI["FastAPI Backend (/api/reconcile)"]
    FastAPI -->|"Async Task"| Agent["RightsLedger Agent (agent.py)"]
    subgraph "Google Cloud / GenAI Runtime"
        Agent -->|"1. Prompt + Telemetry Delta"| Gemini["Gemini 3.6 Flash (google-genai)"]
        Gemini -->|"2. Structured Reasoning + Dispute Drafts"| Agent
    end

    subgraph "Model Context Protocol Boundary"
        Agent -->|"Spawn Subprocess (stdio)"| MCP["mcp-clickhouse (Official MCP Server)"]
    end

    subgraph "ClickHouse Cloud Cluster (rightsledger-dev)"
        MCP -->|"Tool Call: run_query (Read JOIN)"| CH["ClickHouse Cloud"]
        CH -->|"Return Mismatched Rows"| MCP
        MCP -->|"Tool Call: run_query (Writeback Audit)"| CH
    end

    style MCP fill:#38bdf8,stroke:#0f172a,stroke-width:2px,color:#0f172a
    style CH fill:#f97316,stroke:#0f172a,stroke-width:2px,color:#fff
    style Gemini fill:#a855f7,stroke:#0f172a,stroke-width:2px,color:#fff
```

---

## ⚡ How This Satisfies the ClickHouse Track Requirement

To satisfy the hackathon's ClickHouse partner track guidelines:

1. **Official MCP Server:** RightsLedger interacts with ClickHouse Cloud **exclusively** through the official [`mcp-clickhouse`](https://github.com/ClickHouse/mcp-clickhouse) Model Context Protocol server rather than direct or proprietary database drivers.
2. **`stdio` Subprocess Transport:** The agent spawns the `mcp-clickhouse` executable in an isolated environment with secure environment parameters (`CLICKHOUSE_HOST`, `CLICKHOUSE_PORT=8443`, `CLICKHOUSE_SECURE=true`).
3. **Bi-Directional Tool Orchestration:**
   * **Read Phase:** Invokes `run_query` tool to execute high-performance analytical joins between `reported_plays` and `expected_rates`.
   * **Write Phase:** Invokes `run_query` tool to persist structured discrepancy findings, calculated deltas, and generated email drafts directly into the `discrepancies` audit table.

---

## 🛠️ Tech Stack

* **AI / Agentic Framework:** `google-genai` SDK powered by **Gemini 3.6 Flash**
* **Protocol Layer:** Model Context Protocol (`mcp` + `mcp-clickhouse`)
* **Database / Data Warehouse:** ClickHouse Cloud
* **Backend Framework:** Python 3.11, FastAPI & Uvicorn
* **Deployment Target:** Google Cloud Run

---

## 🚀 Setup & Local Run Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/ahmadu2305/rightsledger.git
cd rightsledger
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
CLICKHOUSE_HOST=your_cluster_hostname_only.clickhouse.cloud
CLICKHOUSE_PORT=8443
CLICKHOUSE_SECURE=true
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=your_cluster_password
CLICKHOUSE_ALLOW_WRITE_ACCESS=true
GOOGLE_GENAI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.6-flash
```

### 5. Run the Application
```bash
python main.py
```
Open **`http://localhost:8080`** in your browser to run the reconciliation agent.

---

## 🛡️ Security Architecture: Prompt Injection Defense by Design

Media rights statements and distributor play counts frequently ingest untrusted external strings (e.g., metadata, movie titles, report notes). RightsLedger incorporates a multi-tiered **Defense-by-Design** security architecture to prevent prompt injection and unauthorized financial ledger mutation:
