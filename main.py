import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from agent import run_reconciliation

app = FastAPI(title="RightsLedger Agent")

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>RightsLedger</title>
        <style>
            body { font-family: sans-serif; margin: 40px; background: #0f172a; color: white; }
            button { padding: 12px 24px; font-size: 16px; cursor: pointer; }
            pre { background: #1e293b; padding: 16px; border-radius: 8px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <h1>RightsLedger Agent</h1>
        <button onclick="triggerAudit()">Run Autonomous Reconciliation</button>
        <pre id="output">Waiting to run...</pre>
        <script>
            async function triggerAudit() {
                const out = document.getElementById('output');
                out.innerText = 'Agent running...';
                try {
                    const res = await fetch('/api/reconcile', { method: 'POST' });
                    const data = await res.json();
                    out.innerText = data.agent_output;
                } catch (err) {
                    out.innerText = 'Error: ' + err.message;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/reconcile")
def trigger_reconcile():
    try:
        result = run_reconciliation()
        return {"status": "success", "agent_output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
