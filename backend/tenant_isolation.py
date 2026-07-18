# 1. We group logs under their specific customer (Tenant) labels using a Dictionary
tenant_logs = {
    "Tenant_A": "2026-07-14 [CRITICAL] Database went offline!",
    "Tenant_B": "2026-07-14 [INFO] User login successful",
    "Tenant_C": "2026-07-14 [CRITICAL] Payment gateway timeout!"
}

# 2. We loop through each tenant and its logs to isolate issues
for tenant, log in tenant_logs.items():
    if "[CRITICAL]" in log:
        print(f"🚨 ALERT: Customer {tenant} is experiencing a CRITICAL failure!")
        print(f"   Log Detail: {log}\n")