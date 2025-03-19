FROM fedora:latest

# Install necessary packages including Prosody, netstat, ps, lsof, and expect
RUN dnf -y update && \
    dnf -y install prosody net-tools procps-ng lsof && \
    dnf clean all

# Create a non-privileged user and group for Prosody, if not already present
RUN id -u prosody &>/dev/null || useradd -r -m prosody

# Ensure required directories exist and set correct permissions
RUN mkdir -p /etc/prosody/conf.d /var/lib/prosody && \
    chown -R prosody:prosody /etc/prosody /var/lib/prosody

# Switch back to non-privileged prosody user
USER prosody

# Define volumes for persistent configuration and data
VOLUME ["/etc/prosody", "/var/lib/prosody"]

# Start Prosody when the container runs
CMD ["prosody", "--config", "/etc/prosody/prosody.cfg.lua"]