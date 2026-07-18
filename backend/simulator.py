import os
import time
import random
import requests

BACKEND_URL = "http://localhost:8000/api/v1/telemetry"
HEALTH_CHECK_URL = "http://localhost:8000/dashboard"
MAX_RETRIES = 10
RETRY_DELAY_SECONDS = 3

def wait_for_backend():
    print("Initiating network attachment validation...")
    print(f"Target system: {HEALTH_CHECK_URL}")
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Send a fast test handshake request
            response = requests.get(HEALTH_CHECK_URL, timeout=3)
            if response.status_code == 200:
                print("\n[SUCCESS] Core FastAPI engine is ready and accepting requests. Starting simulation stream...")
                return True
        except requests.exceptions.ConnectionError:
            print(f"[WAITING] Connection refused on attempt {attempt}/{MAX_RETRIES}. Engine may still be booting. Retrying in {RETRY_DELAY_SECONDS}s...")
            time.sleep(RETRY_DELAY_SECONDS)
        except Exception as e:
            print(f"[WARNING] Encountered transient warning: {e}. Retrying...")
            time.sleep(RETRY_DELAY_SECONDS)
            
    print("\n[ERROR] Maximum validation attempts exhausted. Backend engine unreachable.")
    return False

def run_simulation():
    device_id = f"node-fargate-{random.randint(100, 999)}"
    print(f"Starting telemetry payload sequence for {device_id}...")
    
    while True:
        payload = {
            "device_id": device_id,
            "timestamp": time.time(),
            "status": random.choice(["HEALTHY", "PROCESSING", "STABLE"]),
            "metric_value": round(random.uniform(22.1, 89.5), 2)
        }
        
        try:
            res = requests.post(BACKEND_URL, json=payload, timeout=5)
            print(f"[STREAM] Sent payload -> HTTP {res.status_code}: {payload}")
        except Exception as e:
            print(f"[STREAM ERROR] Disruption in network stream delivery: {e}")
            
        # Broadcast interval rhythm
        time.sleep(5)

if __name__ == "__main__":
    # Block loop execution until local port 8000 is open and answering
    if wait_for_backend():
        run_simulation()
    else:
        print("Exiting simulator execution due to interface failure.")