# Chat Service

A real-time chat service leveraging Flask, Flask-SocketIO, MongoDB, and ejabberd XMPP. Includes a static frontend served via Nginx.

## Table of Contents

1. [Features](#features)  
2. [Prerequisites](#prerequisites)  
3. [Local Development Setup](#local-development-setup)  
   - [.env for Local Testing](#env-for-local-testing)  
   - [Rendering ejabberd Config](#rendering-ejabberd-config)  
   - [Launch ejabberd Server](#launch-ejabberd-server)  
   - [Running the Application](#running-the-application)  
   - [Accessing the Frontend](#accessing-the-frontend)  
   - [Important Note on User Registration (Local)](#important-note-on-user-registration-local)  
4. [Dockerized Setup](#dockerized-setup)  
   - [.env for Containerized Testing](#env-for-containerized-testing)  
   - [Rendering ejabberd Config inside Containers](#rendering-ejabberd-config-inside-containers)  
   - [Launch Containers](#launch-containers)  
   - [Accessing the Frontend (Containers)](#accessing-the-frontend-containers)  
   - [Accessing Services](#accessing-services)  


## Features

- 🔄 **Real‑time messaging** with WebSockets  
- 💾 **Chat history** persisted in MongoDB  
- 📡 **XMPP group chat** powered by ejabberd  
- 🌐 **Static frontend** delivered via Nginx  
- 🐳 **Dockerized** for consistent environments  
- ☸️ **Kubernetes-ready deployment** using `deployment.yaml`  


## Prerequisites

- **Python 3.11+**  
- **MongoDB** (local instance or Atlas)  
- **Docker & Docker Compose**  
- **bash** (for helper scripts)  


## Local Development Setup

**Note for Local MongoDB Usage**  
If you're not using a cloud-hosted MongoDB cluster (e.g., Atlas), you must run a MongoDB container locally. We recommend using the official MongoDB **4.4** image for compatibility:
```bash
docker run -d --name local-mongo -p 27017:27017 mongo:4.4
```

### `.env` for Local Testing

Create a file named `.env` in the project root. You can use the .env-sample-local file.

### Rendering ejabberd Config

Before starting ejabberd locally, generate ejabberd.yml from the template:

```bash
./scripts/render_template.sh
```

### Launch ejabberd Server
After rendering the configuration, you can start the ejabberd server.

```bash
./xmpp_server start
```

### Running the Application

#### Start Flask (at root in a virtual environment):

1. Navigate to the Project Root: Open your terminal and navigate to the root directory of the project.
2. Create and Activate Virtual Environment: It's highly recommended to use a virtual environment to manage project dependencies.

```bash
python -m venv venv
source venv/bin/activate  # On Linux/macOS
# venv\Scripts\activate   # On Windows
```

3. Install Dependencies: Install the required Python packages.
```bash
pip install -r requirements.txt
```

4. Run the Flask App:
```bash
python -m app.main
```

### Accessing the Frontend

With the Flask backend running, you can access the static frontend in your web browser at the following address (FLASK_PORT=5000):

Open your browser and navigate to:

```bash
http://localhost:5000/
```

### Important Note on User Registration (Local)
By default, the frontend is configured to automatically attempt a connection as user1. To connect with different users during local testing, you will need to modify the client-side JavaScript code. Specifically, examine the chat_frontend/assets/js/socket.js file to understand how user identification and connection are handled.

## Dockerized Setup

### `.env` for Containerized Testing

Create a file named `.env` in the project root. You can use the .env-sample-container file.

### Rendering ejabberd Config inside Containers

Before launching the ejjaberd container generate ejabberd.yml from the template:

```bash
./scripts/render_template.sh
```

#### Note
1. The VHOST should match the name of the container.
2. The following ejjaberd variables in the .env require the same name as the VHOST:
-  EJABBERD_API_URL="https://${VHOST}:5443/api"
-  ADMIN_USER="admin@${VHOST}"
-  MUC_SERVICE="conference.${VHOST}"

### Launch Containers

```bash
docker-compose up --build -d
```

### Accessing the Frontend (Containers)

With the containers running, you can access the frontend in your web browser at the following address (FRONTEND_PORT=8080):

Open your browser and navigate to:

```bash
http://localhost:8080/
```

### Accessing Services

| Service      | URL                                  |
|--------------|--------------------------------------|
| Frontend     | `http://localhost:${FRONTEND_PORT}`  |
| Flask API    | `http://localhost:${FLASK_PORT}`     |
| ejabberd API | `https://localhost:${PORT_HTTP_TLS}/api` |
