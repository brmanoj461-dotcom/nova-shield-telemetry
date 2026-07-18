import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Nova Shield Telemetry Engine")

# In-memory storage for demonstration metrics
telemetry_db = []

class TelemetryData(BaseModel):
    device_id: str
    timestamp: float
    status: str
    metric_value: float

@app.get("/", include_in_schema=False)
async def root_redirect():
    return HTMLResponse(content="<script>window.location.href='/dashboard';</script>", status_code=200)

@app.post("/api/v1/telemetry", status_code=201)
async def ingest_telemetry(data: TelemetryData):
    telemetry_db.append(data.dict())
    # Keep database bound to the last 50 entries for memory efficiency
    if len(telemetry_db) > 50:
        telemetry_db.pop(0)
    return {"status": "success", "received": data.device_id}

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    # Build a simple real-time visualization layer
    profiles_html = ""
    for entry in reversed(telemetry_db):
        profiles_html += f"""
        <div style='padding: 10px; margin: 5px 0; background: #eef2f3; border-left: 4px solid #007bff;'>
            <strong>Device:</strong> {entry['device_id']} | 
            <strong>Status:</strong> {entry['status']} | 
            <strong>Value:</strong> {entry['metric_value']}
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nova Shield Telemetry Dashboard</title>
        <meta http-equiv="refresh" content="3">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #fafafa; color: #333; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #007bff; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Nova Shield Live Telemetry Monitor</h1>
            <p>Status: <span style="color: green; font-weight: bold;">Connected Engine Active</span></p>
            <hr/>
            <h3>Recent Metrics Profiles:</h3>
            <div>
                {profiles_html if profiles_html else "<p style='color: #777;'>Waiting for simulation stream updates...</p>"}
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)