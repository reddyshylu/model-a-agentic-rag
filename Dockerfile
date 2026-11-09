# Model A: Streamlit app in a container. Runs offline (template answers) unless keys are passed at run time.
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so Docker can reuse this layer when only code changes
COPY requirements-core.txt .
RUN pip install --no-cache-dir -r requirements-core.txt

# Copy the project (secrets are excluded by .dockerignore)
COPY . .

ENV PYTHONPATH=/app/src \
    LLM_BACKEND=none \
    PYTHONUNBUFFERED=1

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
