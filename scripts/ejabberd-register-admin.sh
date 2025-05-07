#!/bin/sh
set -e

echo "⏳ Waiting for ejabberd to boot up..."
sleep 5

echo "🔐 Registering admin user: $ADMIN_USERNAME@$VHOST"
ejabberdctl register "$ADMIN_USERNAME" "$VHOST" "$ADMIN_PASSWORD"