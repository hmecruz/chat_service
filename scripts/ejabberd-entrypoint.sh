#!/bin/bash
set -e

echo "⏳ Waiting for ejabberd to boot up..."
sleep 5

echo "🔐 Registering admin user: $ADMIN_USER@$HOSTNAME"
ejabberdctl register "$ADMIN_USER" "$HOSTNAME" "$ADMIN_PASSWORD" || true

# Finally, start Ejabberd in foreground
exec ejabberdctl foreground