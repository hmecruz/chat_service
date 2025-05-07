# Dockerfile (for ejabberd with custom entrypoint)
FROM ejabberd/ecs:25.03

USER root

# Copy custom config
COPY ejabberd.yml /home/ejabberd/conf/ejabberd.yml

# Copy register-admin script
COPY scripts/ejabberd-register-admin.sh /usr/local/bin/ejabberd-register-admin.sh
RUN chmod +x /usr/local/bin/ejabberd-register-admin.sh

# Copy our new entrypoint wrapper
COPY scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER ejabberd

# Expose standard ejabberd ports
EXPOSE 5222 5269 5280 5443

ENV TINI_SUBREAPER=1

# Use our wrapper as entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
