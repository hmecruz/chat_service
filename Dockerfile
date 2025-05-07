# Dockerfile (for ejabberd)

FROM ejabberd/ecs:latest

# bring in your custom config
COPY ejabberd.yml /home/ejabberd/conf/ejabberd.yml

# bring in the admin-registration script
COPY scripts/ejabberd-entrypoint.sh /usr/local/bin/ejabberd-entrypoint.sh
RUN chmod +x /usr/local/bin/ejabberd-entrypoint.sh

# inject env defaults (will be overridden by docker-compose .env)
ENV ADMIN_USER=${ADMIN_USER}
ENV ADMIN_PASSWORD=${ADMIN_PASSWORD}
ENV HOSTNAME=${HOSTNAME}
ENV ERLANG_NODE=${ERLANG_NODE}

EXPOSE 5222 5269 5280 5443

ENTRYPOINT ["/usr/local/bin/ejabberd-entrypoint.sh"]
