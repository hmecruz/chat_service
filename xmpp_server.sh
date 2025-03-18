#!/bin/bash

CONTAINER_NAME="prosody_xmpp"
IMAGE_NAME="prosody_fedora"
DEFAULT_PORT=5222  # Default client-to-server (c2s) port

start_container() {
    PORT=${1:-$DEFAULT_PORT}  # Use provided port or default

    echo "Starting Prosody XMPP server on port $PORT..."
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        echo "Container '$CONTAINER_NAME' is already running."
    else
        docker run -d --rm --name $CONTAINER_NAME \
            -p $PORT:5222 \
            -v /home/henrique/Desktop/chat_service/prosody.cfg.lua:/etc/prosody/prosody.cfg.lua \
            $IMAGE_NAME
        echo "Container '$CONTAINER_NAME' started on port $PORT."
    fi
}

stop_container() {
    echo "Stopping Prosody XMPP server..."
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        echo "Container '$CONTAINER_NAME' stopped and removed."
    else
        echo "Container '$CONTAINER_NAME' is not running."
    fi
}

status_container() {
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        echo "Container '$CONTAINER_NAME' is running."
    else
        echo "Container '$CONTAINER_NAME' is not running."
    fi
}

build_image() {
    echo "Building Prosody XMPP Docker image..."
    docker build -t $IMAGE_NAME .
    echo "Docker image '$IMAGE_NAME' built successfully."
}

restart_container() {
    stop_container
    start_container "$1"  # Restart with the same port argument
}

enter_shell() {
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        echo "Entering shell of container '$CONTAINER_NAME'..."
        docker exec -it $CONTAINER_NAME /bin/bash
    else
        echo "Container '$CONTAINER_NAME' is not running. Start it first using: $0 start"
        exit 1
    fi
}

case "$1" in
    build)
        build_image
        ;;
    start)
        start_container "$2"  # Pass custom port as argument
        ;;
    stop)
        stop_container
        ;;
    status)
        status_container
        ;;
    restart)
        restart_container "$2"  # Pass custom port to restart
        ;;
    shell)
        enter_shell
        ;;
    *)
        echo "Usage: $0 {build|start [port]|stop|status|restart [port]|shell}"
        exit 1
        ;;
esac
