import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import Dict

# Initialize FastAPI App
app = FastAPI(title="Nova-Shield Telemetry Core")

# Global in-memory storage simulating your metrics/state
telemetry_data: Dict[str, dict] = {}

# Define the expected telemetry payload validation layout
class TelemetryPayload(BaseModel):
    cluster_id: str
    tenant_id: str
    status: str
    cpu_utilization: float
    memory_utilization: float
    network_throughput_mbps: float

# ==========================================
# 0. Root Redirect (Fixes empty landing page)
# ==========================================
@app.get("/")
async def root_redirect():
    """Redirects the base URL straight to the telemetry dashboard."""
    return RedirectResponse(url="/dashboard")

# ==========================================
# 1. API Endpoint for Simulator Sidecar
# ==========================================
@app.post("/api/v1/telemetry")
async def receive_telemetry(payload: TelemetryPayload):
    """
    Receives live performance data from the sidecar simulator
    running on localhost within the same Fargate task network namespace.
    """
    telemetry_data[payload.cluster_id] = {
        "tenant_id": payload.tenant_id,
        "status": payload.status,
        "cpu": f"{payload.cpu_utilization}%",
        "memory": f"{payload.memory_utilization}%",
        "network": f"{payload.network_throughput_mbps} Mbps"
    }
    return {"status": "success", "processed_clusters": len(telemetry_data)}

# ==========================================
# 2. Frontend View Routing Layout
# ==========================================
@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """
    Renders the live monitoring dashboard layout populated with real-time telemetry data.
    """
    cluster_count = len(telemetry_data)
    
    profiles_html = ""
    if not telemetry_data:
        profiles_html = '<div style="color: #a0aec0; font-style: italic; text-align: center; padding: 20px;">Awaiting data streams from network server simulator...</div>'
    else:
        for cid, info in telemetry_data.items():
            profiles_html += f"""
            <div style="background: #2d3748; padding: 15px; border-radius: 6px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: #63b3ed;">Cluster: {cid}</strong> <span style="font-size: 12px; color: #cbd5e0; margin-left: 10px;">Tenant: {info['tenant_id']}</span>
                </div>
                <div style="display: flex; gap: 20px;">
                    <span>CPU: <strong style="color: #48bb78;">{info['cpu']}</strong></span>
                    <span>Mem: <strong style="color: #48bb78;">{info['memory']}</strong></span>
                    <span>Net: <strong style="color: #48bb78;">{info['network']}</strong></span>
                    <span style="background: #2f855a; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{info['status']}</span>
                </div>
            </div>
            """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Nova-Shield Telemetry Dashboard</title>
        <meta http-equiv="refresh" content="3"> 
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #1a202c; color: #fff; margin: 0; padding: 40px; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            .card {{ background: #2d3748; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            h1 {{ color: #3182ce; margin-bottom: 5px; }}
            .subtitle {{ color: #a0aec0; margin-bottom: 30px; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Nova-Shield Telemetry Core</h1>
            <div class="subtitle">Multi-Tenant Infrastructure Analytics Engine</div>
            
            <div class="grid">
                <div class="card">
                    <div style="font-size: 12px; text-transform: uppercase; color: #a0aec0; font-weight: bold; margin-bottom: 5px;">Monitored Infrastructure Clusters</div>
                    <div style="font-size: 36px; font-weight: bold; color: #63b3ed;">{cluster_count}</div>
                </div>
                <div class="card">
                    <div style="font-size: 12px; text-transform: uppercase; color: #a0aec0; font-weight: bold; margin-bottom: 5px;">Data Pipeline Protocol</div>
                    <div style="font-size: 20px; font-weight: bold; color: #cbd5e0; margin-top: 10px;">REST HTTP/JSON + AWS S3</div>
                </div>
            </div>

            <div class="card">
                <h3 style="margin-top: 0; border-bottom: 1px solid #4a5568; padding-bottom: 10px; color: #edf2f7;">Live Target Profiles</h3>
                <div style="margin-top: 15px;">
                    {profiles_html}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

# ==========================================
# 3. Application Runner Entrypoint
# ==========================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)