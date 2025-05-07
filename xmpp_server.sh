#!/bin/bash

CONTAINER_NAME="ejabberd_xmpp"
IMAGE_NAME="ejabberd/ecs:25.03"
DEFAULT_PORT=5222  # Default client-to-server (c2s) port

ADMIN_USER="admin"
ADMIN_PASSWORD="admin_password"
HOSTNAME="localhost"

start_container() {
    PORT=${1:-$DEFAULT_PORT}

    echo "Starting ejabberd XMPP server on port $PORT..."
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        echo "Container '$CONTAINER_NAME' is already running."
    else
        docker run -d --rm --name $CONTAINER_NAME \
            -p $PORT:5222 -p 5269:5269 -p 5280:5280 -p 5443:5443 \
            -v /home/henrique/Desktop/chat_service/ejabberd.yml:/home/ejabberd/conf/ejabberd.yml \
            $IMAGE_NAME

        echo "Container '$CONTAINER_NAME' started on port $PORT."

        echo "⏳ Waiting for ejabberd to boot up..."
        sleep 5  # optional, give ejabberd time to fully boot

        echo "🔐 Registering admin user using ejabberdctl..."
        docker exec $CONTAINER_NAME bin/ejabberdctl register "$ADMIN_USER" "$HOSTNAME" "$ADMIN_PASSWORD"
    fi
}

stop_container() {
    echo "Stopping ejabberd XMPP server..."
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        docker stop $CONTAINER_NAME
        echo "Container '$CONTAINER_NAME' stopped."
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

enter_shell() {
    if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
        echo "Entering shell of container '$CONTAINER_NAME'..."
        docker exec -it $CONTAINER_NAME /bin/sh
    else
        echo "Container '$CONTAINER_NAME' is not running. Start it first using: $0 start"
        exit 1
    fi
}

case "$1" in
    start)
        start_container "$2"  # Pass custom port as argument
        ;;
    stop)
        stop_container
        ;;
    status)
        status_container
        ;;
    shell)
        enter_shell
        ;;
    *)
        echo "Usage: $0 {build|start [port]|stop|status|restart [port]|shell}"
        exit 1
        ;;
esac
