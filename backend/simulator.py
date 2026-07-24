import os
import time
import requests

# Dynamically pull API_URL from environment variable (set in main.tf) or fall back to local IP
TARGET_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/v1/telemetry")

def run_simulator():
    print(f"Starting telemetry simulator targeting: {TARGET_URL}")
    
    # Infinite loop so the container keeps running in Fargate
    while True:
        try:
            # Telemetry payload matching the TelemetryData schema
            payload = {
                "tenant_id": "tenant-alpha",
                "metric_name": "cpu_usage",
                "metric_value": 45.2,
                "status": "ok"
            }
            
            response = requests.post(TARGET_URL, json=payload, timeout=5)
            print(f"[SENT] Status Code: {response.status_code} | Response: {response.text}")
            
        except Exception as e:
            # Catch network errors without crashing the process
            print(f"[WAITING] Could not reach server: {e}. Retrying...")

        # Pause for 5 seconds between telemetry transmissions
        time.sleep(5)

if __name__ == "__main__":
    run_simulator()