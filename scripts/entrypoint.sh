#!/usr/bin/env sh
set -e

echo "🚀 Launching ejabberd in foreground (backgrounded)…"
/home/ejabberd/bin/ejabberdctl foreground &
EJABBERD_PID=$!

echo "⏳ Waiting for ejabberd to become healthy…"
until /home/ejabberd/bin/ejabberdctl status >/dev/null 2>&1; do
  sleep 1
done

echo "🔐 Registering admin user: $ADMIN_USERNAME@$VHOST"
/usr/local/bin/ejabberd-register-admin.sh

echo "🎯 Admin registration done; handing off to ejabberd foreground…"
wait $EJABBERD_PID
