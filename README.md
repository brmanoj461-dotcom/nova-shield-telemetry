# Nova Shield Cloud Telemetry Dashboard

A high-performance, containerized telemetry monitoring system built with Python and FastAPI. It uses a multi-container sidecar architecture deployed on AWS Fargate to collect and display live multi-tenant infrastructure metrics.

## 🚀 Architecture Overview

*   **Application Server (`app.py`)**: A FastAPI backend serving as the central telemetry ingestion API (`/api/v1/telemetry`) and a real-time tracking dashboard (`/dashboard`).
*   **Simulator Sidecar (`simulator.py`)**: A background agent that runs alongside the server in the same Fargate task network namespace, streaming simulated infrastructure logs down the internal `localhost` loop.

## 🛠️ Tech Stack

*   **Backend & Simulation**: Python 3.11, FastAPI, Uvicorn, Requests
*   **Infrastructure**: AWS Fargate (ECS, `awsvpc` mode), Amazon ECR, CloudWatch Logging
*   **IaC & Automation**: Terraform, GitHub Actions (CI/CD)

## 📦 Deployment Workflow

This project is fully automated via GitHub Actions (`deploy.yml`). On every push to `main`:
1. Both the Server and Simulator Docker images are built.
2. Images are pushed to individual Amazon ECR repositories.
3. An ECS Task definition update is triggered to force a rolling deployment on AWS Fargate.
