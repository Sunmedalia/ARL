# Trusted TLS certificate mount

Place `arl.crt` and `arl.key` in this directory to have the gateway copy them
into its writable certificate volume at startup. Keep private keys out of Git.
When these files are absent, the gateway creates a local self-signed certificate.

The gateway runs as UID/GID `10001:10001`. On Linux, make the mounted files
readable by that identity while keeping the private key restricted, for example:

```bash
sudo chown 10001:10001 docker/certs/arl.crt docker/certs/arl.key
sudo chmod 644 docker/certs/arl.crt
sudo chmod 600 docker/certs/arl.key
```
