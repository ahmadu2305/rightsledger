import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
import clickhouse_connect

load_dotenv()

# Using the active model recommended by your API error log
MODEL_ID = "gemini-3.6-flash" 

def run_reconciliation() -> str:
    """Runs autonomous royalty reconciliation audit synchronously."""
    api_key = os.environ.get("GOOGLE_GENAI_API_KEY")
    client = genai.Client(api_key=api_key)

    # 1. Connect to ClickHouse
    host = os.environ.get("CLICKHOUSE_HOST", "").replace("https://", "").replace(":8443", "").strip()
    ch_client = clickhouse_connect.get_client(
        host=host,
        port=8443,
        username=os.environ.get("CLICKHOUSE_USER", "default").strip(),
        password=os.environ.get("CLICKHOUSE_PASSWORD", "").strip(),
        secure=True
    )

    # 2. Query with NULLIF to prevent Division by Zero
    query_sql = """
    SELECT 
        p.id, p.distributor, p.title, p.period_start, p.period_end, 
        p.play_count, p.reported_payout, r.rate_per_play,
        (p.play_count * r.rate_per_play) AS expected_payout,
        (p.reported_payout - (p.play_count * r.rate_per_play)) AS delta,
        abs(p.reported_payout - (p.play_count * r.rate_per_play)) / NULLIF((p.play_count * r.rate_per_play), 0) AS error_rate
    FROM reported_plays p
    JOIN expected_rates r ON p.title = r.title AND p.distributor = r.distributor
    WHERE abs(p.reported_payout - (p.play_count * r.rate_per_play)) / NULLIF((p.play_count * r.rate_per_play), 0) > 0.02
    """
    
    result = ch_client.query(query_sql)
    records = [dict(zip(result.column_names, row)) for row in result.result_rows]
    
    if not records:
        return "No discrepancies found exceeding the 2% threshold."

    # 3. Request structured JSON from Gemini using the Chats API
    prompt = f"""
    Analyze these royalty discrepancies: {json.dumps(records, default=str)}
    
    For each, determine the discrepancy_type ('UNDERPAYMENT', 'OVERPAYMENT', or 'MISSING_USAGE_DATA'), 
    write a 1-sentence explanation of the root cause, and draft a short resolution email.
    
    Return ONLY a raw JSON array of objects with these exact keys:
    id, title, distributor, period_start, period_end, reported_payout, expected_payout, delta, discrepancy_type, explanation, resolution_draft
    """

    chat = client.chats.create(model=MODEL_ID)
    response = chat.send_message(
        prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )
    )

    # 4. Parameterized Insert to prevent SQL Injection
    try:
        flagged_items = json.loads(response.text)
        
        columns = ["id", "title", "distributor", "period_start", "period_end", "reported_payout", "expected_payout", "delta", "discrepancy_type", "explanation", "resolution_draft"]
        
        data_rows = [
            [
                item["id"], item["title"], item["distributor"], 
                item["period_start"], item["period_end"], 
                item["reported_payout"], item["expected_payout"], item["delta"], 
                item["discrepancy_type"], item["explanation"], item["resolution_draft"]
            ] for item in flagged_items
        ]
        
        ch_client.insert('discrepancies', data_rows, column_names=columns)
    except Exception as e:
        return f"Audit completed but database write failed: {e}"

    return json.dumps(flagged_items, indent=2)
