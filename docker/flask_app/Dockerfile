# docker/flask_app/Dockerfile

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
      build-essential \
      libffi-dev \
      libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 1) Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copy your application code
COPY app/ ./app
COPY config/ ./config
# (copy any other dirs your app.main needs)

ENV PYTHONUNBUFFERED=1

EXPOSE ${FLASK_PORT}

# run your Flask-SocketIO entrypoint
CMD ["python", "-m", "app.main"]
