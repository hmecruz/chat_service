# Dockerfile for ejabberd with custom entrypoint
FROM ejabberd/ecs:25.03

USER root

# Copy the register-admin script
COPY scripts/ejabberd-register-admin.sh /usr/local/bin/ejabberd-register-admin.sh
RUN chmod +x /usr/local/bin/ejabberd-register-admin.sh

# Copy our custom entrypoint wrapper
COPY scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER ejabberd

# Expose the necessary ejabberd ports
EXPOSE 5222 5269 5280 5443

ENV TINI_SUBREAPER=1

# Set the entrypoint to our custom wrapper
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
