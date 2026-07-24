import os
import time
import random
import requests

TARGET_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1/telemetry")

TENANTS = [
    {"id": "tenant-alpha", "device": "dev-001"},
    {"id": "tenant-beta", "device": "dev-002"},
    {"id": "tenant-gamma", "device": "dev-003"},
    {"id": "tenant-delta", "device": "dev-004"}
]

def run_simulator():
    print(f"Starting dynamic multi-tenant telemetry simulator targeting: {TARGET_URL}")
    
    while True:
        for tenant in TENANTS:
            # Generate fluctuating real-time CPU & Memory values
            cpu_val = round(random.uniform(20.0, 95.0), 2)
            mem_val = round(random.uniform(35.0, 90.0), 2)
            status = "WARNING" if (cpu_val > 75.0 or mem_val > 75.0) else "INFO"
            
            # Send CPU Telemetry
            payload_cpu = {
                "tenant_id": tenant["id"],
                "device_id": tenant["device"],
                "metric_name": "cpu_usage",
                "metric_value": cpu_val,
                "status": status,
                "timestamp": time.time()
            }
            
            # Send Memory Telemetry
            payload_mem = {
                "tenant_id": tenant["id"],
                "device_id": tenant["device"],
                "metric_name": "memory_allocation",
                "metric_value": mem_val,
                "status": status,
                "timestamp": time.time()
            }
            
            try:
                requests.post(TARGET_URL, json=payload_cpu, timeout=5)
                requests.post(TARGET_URL, json=payload_mem, timeout=5)
                print(f"[STREAM] Pushed live telemetry for {tenant['id']} | CPU: {cpu_val}% | MEM: {mem_val}%")
            except Exception as e:
                print(f"Error sending telemetry stream: {e}")
                
        time.sleep(2)  # Frequency: Updates every 2 seconds

if __name__ == "__main__":
    run_simulator()