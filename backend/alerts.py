# 1. We define a reusable "Alert Machine" (Function)
# It expects two inputs: which tenant is broken, and what the error is
def send_slack_alert(tenant_name, error_message):
    print("--- 📡 CONNECTING TO SLACK API ---")
    print(f"📣 CHANNEL: #alerts-{tenant_name.lower()}")
    print(f"⚠️ MESSAGE: Warning! [Tenant: {tenant_name}] encountered a system crash!")
    print(f"   Details: {error_message}")
    print("---------------------------------\n")


# 2. Let's open our physical server log file and read it
with open("backend/server.log", "r") as file:
    for line in file:
        clean_line = line.strip()
        
        # 3. If we find a critical log, we trigger our Alert Machine!
        if "[CRITICAL]" in clean_line:
            # Let's split the line to find who the tenant is
            # (e.g., "Tenant_B | 2026-07-14... " -> we grab "Tenant_B")
            parts = clean_line.split(" | ")
            tenant = parts[0]
            error_details = parts[2]
            
            # Here we "call" our function and pass the tenant and error details into it!
            send_slack_alert(tenant, error_details)