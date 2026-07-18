# Use an official, lightweight Python runtime base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the dependency file first to leverage Docker's caching layer
COPY requirements.txt .

# Install the application dependencies cleanly
RUN pip install --no-cache-dir -r requirements.txt

# Copy the complete application server file into the container
COPY app.py .

# Inform Docker that the container listens on port 8000 at runtime
EXPOSE 8000

# Execute the FastAPI server backend on container startup
CMD ["python", "app.py"]