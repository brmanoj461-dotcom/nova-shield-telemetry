import os
import time
import random
import requests

# Read the target URL from the environment variables configured via Terraform
# Defaults to localhost if not explicitly provided
API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1/telemetry")

# Mock cluster metadata to simulate multi-tenant traffic
CLUSTERS = [
    {"cluster_id": "nova-cluster-alpha", "tenant_id": "tenant-9921"},
    {"cluster_id": "nova-cluster-beta", "tenant_id": "tenant-4402"},
    {"cluster_id": "nova-cluster-gamma", "tenant_id": "tenant-1185"},
]

print(f"Simulator initialized. Target API Endpoint: {API_URL}")

def generate_mock_telemetry(cluster_id: str, tenant_id: str) -> dict:
    """Generates random infrastructure telemetry data metrics."""
    return {
        "cluster_id": cluster_id,
        "tenant_id": tenant_id,
        "status": random.choice(["HEALTHY", "HEALTHY", "HEALTHY", "DEGRADED"]),
        "cpu_utilization": round(random.uniform(15.0, 85.0), 2),
        "memory_utilization": round(random.uniform(30.0, 90.0), 2),
        "network_throughput_mbps": round(random.uniform(100.0, 950.0), 2)
    }

def run_simulation_loop():
    """Continuously streams data to the FastAPI server on localhost."""
    while True:
        for cluster in CLUSTERS:
            payload = generate_mock_telemetry(cluster["cluster_id"], cluster["tenant_id"])
            
            try:
                # Post the telemetry payload down the internal localhost channel
                response = requests.post(API_URL, json=payload, timeout=5)
                
                if response.status_code == 200:
                    print(f"Successfully streamed telemetry for {payload['cluster_id']} -> Server Response: {response.json()}")
                else:
                    print(f"Server rejected telemetry payload with status code: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print(f"Connection to server at {API_URL} refused. Server may still be booting. Retrying...")
            except Exception as e:
                print(f"Unexpected error encountered during streaming pipeline: {e}")
                
        # Pause for 3 seconds before sending the next telemetry interval match
        time.sleep(3)

if __name__ == "__main__":
    # Small grace period delay to allow uvicorn server to start binding to port 8000
    print("Waiting 5 seconds for application server initialization sequence...")
    time.sleep(5)
    run_simulation_loop()