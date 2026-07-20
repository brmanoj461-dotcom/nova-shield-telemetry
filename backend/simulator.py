import time
import requests

# Set your target endpoint using IPv4 explicitly
TARGET_URL = "http://127.0.0.1:8000/dashboard"

def run_simulator():
    print(f"Starting telemetry simulator targeting: {TARGET_URL}")
    
    # Infinite loop so the container never exits
    while True:
        try:
            # Example payload - replace with your actual telemetry data logic
            payload = {"status": "ok", "telemetry": "sample_data"}
            
            response = requests.post(TARGET_URL, json=payload, timeout=5)
            print(f"[SENT] Status Code: {response.status_code}")
            
        except Exception as e:
            # Catch connection errors without crashing the process
            print(f"[WAITING] Could not reach server: {e}. Retrying...")

        # Pause for 5 seconds between runs (adjust interval as needed)
        time.sleep(5)

if __name__ == "__main__":
    run_simulator()