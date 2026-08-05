#!/bin/sh
set -eu

CERT_DIR=/etc/nginx/arl-certs
CERT_FILE="$CERT_DIR/arl.crt"
KEY_FILE="$CERT_DIR/arl.key"

mkdir -p "$CERT_DIR"
if [ ! -s "$CERT_FILE" ] || [ ! -s "$KEY_FILE" ]; then
    echo "Generating a local self-signed TLS certificate"
    openssl req -x509 -newkey rsa:2048 -sha256 -nodes -days 3650 \
        -keyout "$KEY_FILE" -out "$CERT_FILE" \
        -subj "/C=CN/O=ARL/CN=localhost" \
        -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
    chmod 600 "$KEY_FILE"
fi

exec nginx -g "daemon off;"
