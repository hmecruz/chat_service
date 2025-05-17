# docker/flask_app/Dockerfile

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
      build-essential \
      libffi-dev \
      libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 1) Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copy backend code
COPY app/ ./app
COPY config/ ./config


ENV PYTHONUNBUFFERED=1

EXPOSE ${FLASK_PORT}

CMD ["python", "-m", "app.main"]
