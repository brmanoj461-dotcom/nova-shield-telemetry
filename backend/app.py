from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os

app = FastAPI()

DB_PATH = "backend/telemetry.db"

# Secure database of registered tenants and their secret API keys
TENANT_DATABASE = {
    "tenant_a": "key_alpha_123",
    "tenant_b": "key_beta_456",
    "tenant_ninja": "key_secret_ninja"
}

class LogSubmission(BaseModel):
    tenant: str
    level: str  # INFO, WARNING, CRITICAL
    message: str

# Initialize the SQLite Database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def home():
    return {"status": "Online", "message": "Secure SQL Multi-Tenant Telemetry Engine Active!"}

# Ingestion API endpoint (Writes securely to SQLite database via HTTP Header verification)
@app.post("/submit-log")
def submit_log(log: LogSubmission, x_api_key: str = Header(None)):
    # 1. Check if the API key header was even provided
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Security check failed: Missing 'X-API-Key' header.")
    
    # 2. Check if the tenant exists in our secure database
    tenant_key = log.tenant.strip().lower()
    if tenant_key not in TENANT_DATABASE:
        raise HTTPException(status_code=403, detail=f"Registration error: '{log.tenant}' is not a registered tenant.")
    
    # 3. Verify that the provided key matches the tenant's registered key
    expected_key = TENANT_DATABASE[tenant_key]
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Access Denied: Invalid API key for this tenant.")

    # Validation passed! Save the log to SQL
    if not log.message.strip():
        raise HTTPException(status_code=400, detail="Log message cannot be empty.")
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (tenant, timestamp, level, message) VALUES (?, ?, ?, ?)",
        (log.tenant.strip(), timestamp, log.level.upper(), log.message.strip())
    )
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": f"Log securely saved to DB for {log.tenant}!"}

# Query API endpoint that feeds our Dynamic UI
@app.get("/logs")
def get_logs(tenant: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch logs based on filter
    if tenant:
        cursor.execute("SELECT tenant, timestamp, level, message FROM logs WHERE LOWER(tenant) = ? ORDER BY id DESC", (tenant.lower(),))
    else:
        cursor.execute("SELECT tenant, timestamp, level, message FROM logs ORDER BY id DESC")
    
    rows = cursor.fetchall()
    
    # Fetch distinct active tenants for the top filter buttons
    cursor.execute("SELECT DISTINCT tenant FROM logs")
    tenants = [row[0] for row in cursor.fetchall()]
    
    # Calculate System Stats
    cursor.execute("SELECT COUNT(*) FROM logs")
    total_logs = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM logs WHERE level = 'CRITICAL'")
    critical_alerts_count = cursor.fetchone()[0]
    
    # Fetch raw alerts to populate the critical alerts feed
    if tenant:
        cursor.execute("SELECT tenant, message FROM logs WHERE level = 'CRITICAL' AND LOWER(tenant) = ? ORDER BY id DESC", (tenant.lower(),))
    else:
        cursor.execute("SELECT tenant, message FROM logs WHERE level = 'CRITICAL' ORDER BY id DESC")
    alerts_data = [{"tenant": row[0], "message": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    
    logs_data = [{"tenant": r[0], "timestamp": r[1], "level": r[2], "message": r[3]} for r in rows]
    
    return {
        "total_logs": total_logs,
        "critical_alerts_count": critical_alerts_count,
        "critical_alerts": alerts_data,
        "data": logs_data,
        "tenants": sorted(tenants)
    }

# Main Premium UI Route (High-End Dark Command Center)
@app.get("/dashboard", response_class=HTMLResponse)
def read_dashboard(tenant: str = None):
    # Fetch current list of tenants to build filtering navbar dynamically
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT tenant FROM logs")
    tenant_list = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # Generate interactive filter badges
    nav_html = f'<a href="/dashboard" class="px-4 py-2 rounded-lg font-semibold text-sm transition-all {"bg-blue-600 text-white shadow-lg shadow-blue-500/20" if not tenant else "bg-slate-800 text-slate-400 hover:bg-slate-700"}">All Channels</a>'
    
    for t_name in sorted(tenant_list):
        is_selected = tenant and tenant.lower() == t_name.lower()
        badge_class = "bg-blue-600 text-white shadow-lg shadow-blue-500/20" if is_selected else "bg-slate-800 text-slate-400 hover:bg-slate-700"
        nav_html += f"""
        <a href="/dashboard?tenant={t_name}" class="px-4 py-2 rounded-lg font-semibold text-sm transition-all {badge_class}">
            {t_name}
        </a>
        """

    active_tenant_js = f"'{tenant}'" if tenant else "null"

    return f"""
    <!DOCTYPE html>
    <html lang="en" class="h-full bg-slate-950">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Nova-Shield Telemetry Hub</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="min-h-full text-slate-100 p-6 md:p-12 font-sans">
        
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center bg-slate-900/60 border border-slate-800/80 backdrop-blur-xl p-6 rounded-2xl gap-4 shadow-2xl">
            <div>
                <div class="flex items-center gap-3">
                    <span class="flex h-3 w-3 relative">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                    </span>
                    <h1 class="text-2xl font-bold tracking-tight bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">Nova-Shield Hub</h1>
                </div>
                <p class="text-slate-400 text-xs mt-1">SaaS Logging System &bull; Active Filters: <span class="text-blue-400 font-semibold">{tenant if tenant else "All Streams"}</span></p>
            </div>
            <div class="flex flex-wrap gap-2">
                {nav_html}
            </div>
        </div>

        <div class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div class="bg-slate-900/40 border border-slate-800/80 p-6 rounded-2xl flex items-center justify-between">
                <div>
                    <p class="text-sm text-slate-400 font-medium">Total Raw Log Streams</p>
                    <p id="stat-total-logs" class="text-3xl font-bold text-white mt-1">0</p>
                </div>
                <div class="p-3 bg-blue-500/10 text-blue-400 rounded-xl">📊</div>
            </div>
            <div class="bg-slate-900/40 border border-slate-800/80 p-6 rounded-2xl flex items-center justify-between">
                <div>
                    <p class="text-sm text-slate-400 font-medium">Active Connected Tenants</p>
                    <p id="stat-active-tenants" class="text-3xl font-bold text-white mt-1">0</p>
                </div>
                <div class="p-3 bg-indigo-500/10 text-indigo-400 rounded-xl">🔑</div>
            </div>
            <div class="bg-slate-900/40 border border-slate-800/80 p-6 rounded-2xl flex items-center justify-between">
                <div>
                    <p class="text-sm text-slate-400 font-medium">Threat Alerts</p>
                    <p id="stat-alerts" class="text-3xl font-bold text-rose-500 mt-1">0</p>
                </div>
                <div class="p-3 bg-rose-500/10 text-rose-400 rounded-xl">⚠️</div>
            </div>
        </div>

        <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
            
            <div class="lg:col-span-1">
                <h3 class="text-lg font-bold text-slate-300 mb-4 flex items-center gap-2">
                    <span>🚨</span> Critical System Incidents
                </h3>
                <div id="alert-container" class="space-y-4">
                    </div>
            </div>

            <div class="lg:col-span-2">
                <h3 class="text-lg font-bold text-slate-300 mb-4 flex items-center gap-2">
                    <span>📡</span> Continuous Ingestion Stream
                </h3>
                <div id="log-container" class="space-y-3">
                    </div>
            </div>
        </div>

        <script>
            const activeTenant = {active_tenant_js};

            async function fetchUpdates() {{
                try {{
                    const url = activeTenant ? `/logs?tenant=${{activeTenant}}` : '/logs';
                    const response = await fetch(url);
                    const result = await response.json();
                    
                    // Update Stat Badges
                    document.getElementById('stat-total-logs').innerText = result.total_logs;
                    document.getElementById('stat-active-tenants').innerText = result.tenants.length;
                    document.getElementById('stat-alerts').innerText = result.critical_alerts_count;

                    // 1. Render Alerts Panel
                    const alertContainer = document.getElementById('alert-container');
                    if (result.critical_alerts.length === 0) {{
                        alertContainer.innerHTML = `
                            <div class="bg-emerald-500/5 border border-emerald-500/20 text-emerald-400 p-5 rounded-2xl text-sm flex items-center gap-3">
                                <span>🛡️</span> All active nodes report nominal parameters.
                            </div>`;
                    }} else {{
                        alertContainer.innerHTML = result.critical_alerts.map(alert => `
                            <div class="bg-rose-500/5 border border-rose-500/20 p-5 rounded-2xl shadow-xl transition-all hover:scale-[1.01]">
                                <div class="text-rose-400 font-bold text-xs uppercase tracking-wider flex items-center gap-2">
                                    <span class="h-2 w-2 rounded-full bg-rose-500 animate-pulse"></span>
                                    CRITICAL WARNING: ${{alert.tenant}}
                                </div>
                                <p class="text-slate-300 text-sm mt-2 font-medium">${{alert.message}}</p>
                            </div>
                        `).join('');
                    }}

                    // 2. Render Logs Feed
                    const logContainer = document.getElementById('log-container');
                    if (result.data.length === 0) {{
                        logContainer.innerHTML = `
                            <div class="text-center py-12 text-slate-500 italic text-sm border border-dashed border-slate-800 rounded-2xl">
                                No network telemetry ingested on this interface yet.
                            </div>`;
                    }} else {{
                        logContainer.innerHTML = result.data.map(log => {{
                            const isCrit = log.level === "CRITICAL";
                            const borderColor = isCrit ? "border-rose-500/30 bg-rose-500/5" : "border-slate-800/80 bg-slate-900/30";
                            const badgeStyle = isCrit ? "bg-rose-500/10 text-rose-400 border border-rose-500/20" : "bg-blue-500/10 text-blue-400 border border-blue-500/20";
                            
                            return `
                                <div class="border p-5 rounded-2xl flex flex-col sm:flex-row justify-between items-start gap-4 shadow-sm transition-all hover:border-slate-700/60 ${{borderColor}}">
                                    <div class="flex-1">
                                        <div class="flex flex-wrap items-center gap-2">
                                            <span class="text-xs px-2.5 py-1 rounded-full font-bold uppercase tracking-wider ${{badgeStyle}}">${{log.tenant}}</span>
                                            <span class="text-[10px] text-slate-500 font-semibold tracking-wider uppercase">${{log.level}}</span>
                                        </div>
                                        <p class="text-slate-300 text-sm mt-3 font-mono">${{log.message}}</p>
                                    </div>
                                    <span class="text-xs text-slate-500 font-medium sm:self-start">${{log.timestamp}}</span>
                                </div>`;
                        }}).join('');
                    }}
                }} catch (error) {{
                    console.error("Dashboard Sync Error:", error);
                }}
            }}

            fetchUpdates();
            setInterval(fetchUpdates, 2000);
        </script>
    </body>
    </html>
    """