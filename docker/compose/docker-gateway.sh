#!/bin/sh
set -eu

CERT_DIR=/etc/nginx/arl-certs
TRUSTED_DIR=/etc/nginx/trusted-certs
CERT_FILE="$CERT_DIR/arl.crt"
KEY_FILE="$CERT_DIR/arl.key"

mkdir -p "$CERT_DIR"
if [ -s "$TRUSTED_DIR/arl.crt" ] && [ -s "$TRUSTED_DIR/arl.key" ]; then
    if [ ! -r "$TRUSTED_DIR/arl.crt" ] || [ ! -r "$TRUSTED_DIR/arl.key" ]; then
        echo "Mounted TLS files must be readable by gateway UID 10001" >&2
        exit 1
    fi
    echo "Installing mounted TLS certificate"
    cp "$TRUSTED_DIR/arl.crt" "$CERT_FILE"
    cp "$TRUSTED_DIR/arl.key" "$KEY_FILE"
fi

if [ ! -s "$CERT_FILE" ] || [ ! -s "$KEY_FILE" ]; then
    echo "Generating a local self-signed TLS certificate"
    openssl req -x509 -newkey rsa:2048 -sha256 -nodes -days 3650 \
        -keyout "$KEY_FILE" -out "$CERT_FILE" \
        -subj "/C=CN/O=ARL/CN=localhost" \
        -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
fi
chmod 600 "$KEY_FILE"

exec nginx -g "daemon off;"
