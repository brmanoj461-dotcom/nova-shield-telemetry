FROM python:3.11-slim

# Force stdout and stderr to be unbuffered so logs stream instantly to CloudWatch
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files (or make sure all relevant code files are included)
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]