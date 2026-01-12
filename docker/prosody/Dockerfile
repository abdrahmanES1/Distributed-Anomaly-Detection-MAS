FROM prosody/prosody:latest

COPY prosody.cfg.lua /etc/prosody/prosody.cfg.lua

# Generate self-signed certificate for monitor.local
USER root
RUN openssl req -new -x509 -days 365 -nodes \
    -out /etc/prosody/certs/prosody.crt \
    -keyout /etc/prosody/certs/prosody.key \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=prosody" && \
    chown prosody:prosody /etc/prosody/certs/prosody.key /etc/prosody/certs/prosody.crt


CMD ["prosody"]
