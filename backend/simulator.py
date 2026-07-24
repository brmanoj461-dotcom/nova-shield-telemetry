import os
import time
import requests
from datetime import datetime, timezone

TARGET_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1/telemetry")

def run_simulator():
    print(f"Starting telemetry simulator targeting: {TARGET_URL}")
    
    while True:
        try:
            payload = {
                "tenant_id": "tenant-alpha",
                "device_id": "dev-001",
                "metric_name": "cpu_usage",
                "metric_value": 45.2,
                "status": "ok",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            response = requests.post(TARGET_URL, json=payload, timeout=5)
            print(f"[SENT] Status Code: {response.status_code} | Response: {response.text}")
        except Exception as e:
            print(f"Error sending telemetry: {e}")
            
        time.sleep(2)

if __name__ == "__main__":
    run_simulator()