# =============================================================================
#  Neos Autonomous Dev Squad - Single Image, Dual Service
#
#  This single image is used for BOTH the backend (FastAPI/uvicorn) and
#  the frontend (Streamlit). The CMD is overridden per-service in
#  docker-compose.yml. No multi-stage needed – shared deps = shared image.
# =============================================================================

FROM python:3.11-slim

# --- System dependencies ---
# Install Docker CLI so that the QA Agent (running inside this container)
# can issue docker run commands against the HOST daemon via the mounted socket.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg \
        -o /etc/apt/keyrings/docker.asc \
    && chmod a+r /etc/apt/keyrings/docker.asc \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
        https://download.docker.com/linux/debian \
        $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
        | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# --- Python dependencies ---
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# --- Application code ---
COPY . .

# Create outputs directory for the Saver agent
RUN mkdir -p /app/outputs

# Expose both service ports (docker-compose maps only what's needed per service)
EXPOSE 8000 8501

# Default CMD – overridden by docker-compose per service
CMD ["uvicorn", "worker:app", "--host", "0.0.0.0", "--port", "8000"]
