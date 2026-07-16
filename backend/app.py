import sqlite3
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI(title="Nova-Shield Telemetry Hub")

# Enable CORS so the frontend dashboard can securely make API requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "telemetry.db"

# --- Database Initialization ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create tenants table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tenants (
        tenant_id TEXT PRIMARY KEY,
        api_key TEXT NOT NULL
    )
    """)
    
    # Create logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tenant_id TEXT,
        level TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(tenant_id) REFERENCES tenants(tenant_id)
    )
    """)
    
    # Seed default dummy tenants if table is empty
    cursor.execute("SELECT COUNT(*) FROM tenants")
    if cursor.fetchone()[0] == 0:
        default_tenants = [
            ("tenant_alpha", "alpha_secret_key_2026"),
            ("tenant_beta", "beta_secure_token_abc"),
            ("tenant_ninja", "your_secure_tenant_key")
        ]
        cursor.executemany("INSERT INTO tenants (tenant_id, api_key) VALUES (?, ?)", default_tenants)
        
    conn.commit()
    conn.close()

init_db()

# --- Pydantic Schemas ---
class LogPayload(BaseModel):
    tenant: str
    level: str
    message: str

# --- Authentication Dependency ---
async def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")
    
    # Read the body to check if tenant matches key
    try:
        body = await request.json()
        tenant_id = body.get("tenant")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT api_key FROM tenants WHERE tenant_id = ?", (tenant_id,))
    result = cursor.fetchone()
    conn.close()

    if not result or result[0] != api_key:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid Tenant ID or API Key mapping")
    
    return tenant_id

# --- API Endpoints ---

@app.post("/submit-log")
def submit_log(payload: LogPayload, authorized_tenant: str = Depends(verify_api_key)):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (tenant_id, level, message) VALUES (?, ?, ?)",
        (payload.tenant, payload.level.upper(), payload.message)
    )
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Log ingested securely for {authorized_tenant}"}

@app.get("/api/metrics")
def get_metrics():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Total streams/logs
    cursor.execute("SELECT COUNT(*) FROM logs")
    total_logs = cursor.fetchone()[0]
    
    # 2. Total active tenants logged
    cursor.execute("SELECT COUNT(DISTINCT tenant_id) FROM logs")
    active_tenants = cursor.fetchone()[0]
    
    # 3. Critical incidents count
    cursor.execute("SELECT COUNT(*) FROM logs WHERE level = 'CRITICAL'")
    critical_incidents = cursor.fetchone()[0]
    
    # 4. Recent logs feed
    cursor.execute("SELECT tenant_id, level, message, timestamp FROM logs ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    recent_logs = []
    for row in rows:
        recent_logs.append({
            "tenant": row[0],
            "level": row[1],
            "message": row[2],
            "timestamp": row[3]
        })
        
    conn.close()
    
    return {
        "total_logs": total_logs,
        "active_tenants": active_tenants,
        "critical_incidents": critical_incidents,
        "recent_logs": recent_logs
    }

@app.get("/dashboard", response_class=HTMLResponse)
def read_dashboard():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nova-Shield Command Center</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 font-sans min-h-screen">
        <div class="max-w-7xl mx-auto px-4 py-8">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-6 mb-8 gap-4">
                <div>
                    <h1 class="text-3xl font-bold tracking-tight bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
                        🛡️ Nova-Shield Hub
                    </h1>
                    <p class="text-slate-400 mt-1 text-sm">Real-time Multi-Tenant Security Telemetry Monitor</p>
                </div>
                <div class="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-lg">
                    <span class="relative flex h-2.5 w-2.5">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                    </span>
                    <span class="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Engine Live</span>
                </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
                <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md">
                    <p class="text-sm font-medium text-slate-400 uppercase tracking-wider">Total Streams Ingested</p>
                    <p id="total-logs" class="text-4xl font-extrabold mt-2 text-blue-400">0</p>
                </div>
                <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md">
                    <p class="text-sm font-medium text-slate-400 uppercase tracking-wider">Active Secure Nodes</p>
                    <p id="active-tenants" class="text-4xl font-extrabold mt-2 text-indigo-400">0</p>
                </div>
                <div class="bg-slate-900 border border-slate-800 p-6 rounded-xl shadow-md border-l-4 border-l-red-500">
                    <p class="text-sm font-medium text-slate-400 uppercase tracking-wider">Critical Anomalies</p>
                    <p id="critical-incidents" class="text-4xl font-extrabold mt-2 text-red-400">0</p>
                </div>
            </div>

            <div class="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-md">
                <div class="px-6 py-4 border-b border-slate-800 bg-slate-900/50 flex justify-between items-center">
                    <h2 class="font-semibold text-slate-200">Live Telemetry Stream Feed</h2>
                    <span class="text-xs text-slate-500">Refreshes automatically every 2s</span>
                </div>
                <div id="log-container" class="divide-y divide-slate-800 px-6 max-h-[400px] overflow-y-auto">
                    <p class="text-slate-500 text-sm py-8 text-center">Awaiting streaming nodes authorization initialization...</p>
                </div>
            </div>
        </div>

        <script>
            async function fetchUpdates() {
                try {
                    const response = await fetch('/api/metrics');
                    if (!response.ok) throw new Error("Network metrics polling failed");
                    const data = await response.json();
                    
                    // Update main cards
                    document.getElementById('total-logs').innerText = data.total_logs;
                    document.getElementById('active-tenants').innerText = data.active_tenants;
                    document.getElementById('critical-incidents').innerText = data.critical_incidents;
                    
                    // Update Feed container
                    const container = document.getElementById('log-container');
                    if(data.recent_logs.length === 0) {
                        container.innerHTML = `<p class="text-slate-500 text-sm py-8 text-center">No logs ingested yet. Send a POST request to track logs!</p>`;
                        return;
                    }
                    
                    container.innerHTML = data.recent_logs.map(log => {
                        let badgeColor = "bg-slate-800 text-slate-300 border-slate-700";
                        if (log.level === 'CRITICAL') badgeColor = "bg-red-950/40 text-red-400 border-red-900/50";
                        if (log.level === 'WARNING') badgeColor = "bg-amber-950/40 text-amber-400 border-amber-900/50";
                        if (log.level === 'INFO') badgeColor = "bg-blue-950/40 text-blue-400 border-blue-900/50";
                        
                        return `
                            <div class="py-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                                <div class="flex items-start gap-3">
                                    <span class="px-2 py-0.5 rounded text-xs font-mono font-bold uppercase tracking-wide border ${badgeColor} mt-0.5">
                                        \${log.level}
                                    </span>
                                    <div>
                                        <span class="text-xs font-semibold font-mono text-indigo-400">\${log.tenant}</span>
                                        <p class="text-slate-300 text-sm mt-0.5 font-mono">\${log.message}</p>
                                    </div>
                                </div>
                                <span class="text-xs text-slate-500 font-mono sm:self-start mt-1">\${log.timestamp}</span>
                            </div>
                        `;
                    }).join('');
                } catch (error) {
                    console.error("Dashboard Sync Error:", error);
                }
            }

            fetchUpdates();
            setInterval(fetchUpdates, 2000);
        </script>
    </body>
    </html>
    """

# --- Server Lifecycle Ingress Engine ---
if __name__ == "__main__":
    import uvicorn
    import os
    # Render provides a PORT environment variable dynamically on runtime
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.app:app", host="0.0.0.0", port=port)