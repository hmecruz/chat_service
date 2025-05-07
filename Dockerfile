# Dockerfile (for ejabberd)
FROM ejabberd/ecs:25.03

# Copy custom config
COPY ejabberd.yml /home/ejabberd/conf/ejabberd.yml

# Copy entrypoint script (ensure it's executable locally)
COPY scripts/ejabberd-entrypoint.sh /usr/local/bin/ejabberd-entrypoint.sh

# Expose standard ejabberd ports
EXPOSE 5222 5269 5280 5443

# Entry point to register admin and start server
ENTRYPOINT ["/sbin/tini", "--", "/home/ejabberd/bin/ejabberdctl", "foreground"]

