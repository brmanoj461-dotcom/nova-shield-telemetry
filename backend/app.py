import time
from typing import Dict
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="Nova Shield Telemetry Core")

# Live telemetry storage
telemetry_db: Dict[str, dict] = {
    "tenant-alpha": {"tenant_id": "tenant-alpha", "name": "Tenant_A", "status": "INFO", "cpu": 40.33, "memory": 49.20, "device_id": "dev-001"},
    "tenant-beta": {"tenant_id": "tenant-beta", "name": "Tenant_B", "status": "WARNING", "cpu": 51.14, "memory": 51.92, "device_id": "dev-002"},
    "tenant-gamma": {"tenant_id": "tenant-gamma", "name": "Tenant_C", "status": "INFO", "cpu": 71.14, "memory": 61.00, "device_id": "dev-003"},
    "tenant-delta": {"tenant_id": "tenant-delta", "name": "Tenant_D", "status": "INFO", "cpu": 50.37, "memory": 61.50, "device_id": "dev-004"}
}

class TelemetryData(BaseModel):
    tenant_id: str
    device_id: str
    metric_name: str
    metric_value: float
    status: str
    timestamp: float

@app.post("/api/v1/telemetry")
async def ingest_telemetry(data: TelemetryData):
    tenant_key = data.tenant_id.lower()
    
    if tenant_key not in telemetry_db:
        telemetry_db[tenant_key] = {
            "tenant_id": data.tenant_id,
            "name": data.tenant_id.replace("tenant-", "Tenant_").replace("_", " ").title(),
            "status": "INFO",
            "cpu": 0.0,
            "memory": 0.0,
            "device_id": data.device_id
        }
    
    if "cpu" in data.metric_name.lower():
        telemetry_db[tenant_key]["cpu"] = round(data.metric_value, 2)
    elif "mem" in data.metric_name.lower():
        telemetry_db[tenant_key]["memory"] = round(data.metric_value, 2)
        
    telemetry_db[tenant_key]["status"] = data.status.upper()
    return {"status": "success"}

@app.get("/api/v1/telemetry/feed")
async def get_feed():
    return list(telemetry_db.values())

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Telemetry Core Analytics</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                background-color: #0b1120;
                color: #f8fafc;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                padding: 24px 16px;
                max-width: 500px;
                margin: 0 auto;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 24px;
            }
            .header-title h1 { font-size: 28px; font-weight: 800; color: #38bdf8; line-height: 1.1; }
            .header-title p { font-size: 13px; color: #64748b; margin-top: 6px; font-weight: 500; }
            .cluster-badge {
                background-color: #111c35;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                display: flex;
                flex-direction: column;
                gap: 2px;
            }
            .cluster-status { display: flex; align-items: center; gap: 6px; color: #22c55e; font-weight: 700; }
            .pulse-dot {
                width: 8px; height: 8px; background-color: #22c55e; border-radius: 50%;
                box-shadow: 0 0 8px #22c55e; animation: blink 1.5s infinite;
            }
            @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
            
            .stat-card {
                background-color: #131c31;
                border: 1px solid #1e2d4a;
                border-radius: 10px;
                padding: 16px;
                margin-bottom: 16px;
            }
            .stat-card .label { font-size: 11px; font-weight: 700; letter-spacing: 0.5px; color: #64748b; text-transform: uppercase; margin-bottom: 8px; }
            .stat-card .value-num { font-size: 32px; font-weight: 800; color: #ffffff; }
            .stat-card .value-purple { font-size: 22px; font-weight: 800; color: #c084fc; }

            .section-title { font-size: 22px; font-weight: 700; color: #ffffff; margin: 28px 0 16px 0; }

            .tenant-card {
                background-color: #131c31;
                border: 1px solid #1e2d4a;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 16px;
                position: relative;
                overflow: hidden;
            }
            .tenant-card.border-warning::before {
                content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 5px; background-color: #f43f5e;
            }
            .tenant-card.border-info::before {
                content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 5px; background-color: #38bdf8;
            }
            .tenant-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
            .tenant-name { font-size: 18px; font-weight: 700; color: #ffffff; }
            .badge-tag { font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 4px; letter-spacing: 0.5px; }
            .badge-warning { background-color: #9f1239; color: #fecdd3; }
            .badge-info { background-color: #0369a1; color: #bae6fd; }
            .tenant-id { font-size: 12px; color: #64748b; margin-bottom: 16px; }

            .metric-row { margin-bottom: 12px; }
            .metric-labels { display: flex; justify-content: space-between; font-size: 13px; color: #94a3b8; margin-bottom: 6px; }
            .metric-val { font-weight: 700; color: #ffffff; }
            .progress-bg { width: 100%; height: 8px; background-color: #1e293b; border-radius: 4px; overflow: hidden; }
            
            /* Animated Smooth Bars */
            .progress-fill-blue {
                height: 100%; background-color: #38bdf8; border-radius: 4px;
                transition: width 0.8s ease-in-out;
            }
            .progress-fill-purple {
                height: 100%; background-color: #c084fc; border-radius: 4px;
                transition: width 0.8s ease-in-out;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-title">
                <h1>Telemetry<br>Core</h1>
                <p>Multi-Tenant Infrastructure<br>Analytics Engine</p>
            </div>
            <div class="cluster-badge">
                <div class="cluster-status">
                    <div class="pulse-dot"></div> Cluster
                </div>
                <div style="color: #64748b;">State:</div>
                <div style="color: #22c55e; font-weight: 700;">Operational</div>
            </div>
        </div>

        <div class="stat-card">
            <div class="label">MONITORED INFRASTRUCTURE CLUSTERS</div>
            <div class="value-num" id="cluster-count">4</div>
        </div>

        <div class="stat-card">
            <div class="label">DATA PIPELINE PROTOCOL</div>
            <div class="value-purple">REST HTTP/JSON + AWS S3</div>
        </div>

        <div class="section-title">Live Target Profiles</div>
        <div id="profiles-container"></div>

        <script>
            async function updateFeed() {
                try {
                    const res = await fetch('/api/v1/telemetry/feed');
                    const data = await res.json();
                    
                    document.getElementById('cluster-count').innerText = data.length;
                    const container = document.getElementById('profiles-container');
                    container.innerHTML = '';

                    data.forEach(item => {
                        const isWarning = item.status === 'WARNING';
                        const badgeClass = isWarning ? 'badge-warning' : 'badge-info';
                        const borderClass = isWarning ? 'border-warning' : 'border-info';
                        
                        const cardHTML = `
                            <div class="tenant-card ${borderClass}">
                                <div class="tenant-header">
                                    <div class="tenant-name">${item.name}</div>
                                    <span class="badge-tag ${badgeClass}">${item.status}</span>
                                </div>
                                <div class="tenant-id">ID: ${item.tenant_id}</div>
                                
                                <div class="metric-row">
                                    <div class="metric-labels">
                                        <span>CPU Consumption</span>
                                        <span class="metric-val">${item.cpu}%</span>
                                    </div>
                                    <div class="progress-bg">
                                        <div class="progress-fill-blue" style="width: ${Math.min(item.cpu, 100)}%;"></div>
                                    </div>
                                </div>

                                <div class="metric-row">
                                    <div class="metric-labels">
                                        <span>Memory Allocation</span>
                                        <span class="metric-val">${item.memory}%</span>
                                    </div>
                                    <div class="progress-bg">
                                        <div class="progress-fill-purple" style="width: ${Math.min(item.memory, 100)}%;"></div>
                                    </div>
                                </div>
                            </div>
                        `;
                        container.innerHTML += cardHTML;
                    });
                } catch (e) {
                    console.error("Error fetching telemetry feed:", e);
                }
            }

            // Poll for updates every 1.5 seconds for active streaming
            setInterval(updateFeed, 1500);
            updateFeed();
        </script>
    </body>
    </html>
    """
    return html_content