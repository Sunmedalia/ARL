ARG NODE_IMAGE=node:22.18.0-bookworm-slim
ARG NGINX_IMAGE=nginx:1.28.0-alpine
FROM ${NODE_IMAGE} AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM ${NGINX_IMAGE}
RUN apk add --no-cache curl openssl \
    && addgroup -g 10001 -S arl \
    && adduser -u 10001 -S -D -H -s /sbin/nologin -G arl arl \
    && mkdir -p /etc/nginx/arl-certs /etc/nginx/trusted-certs \
        /var/cache/nginx /usr/share/nginx/html/next \
    && chown -R arl:arl /etc/nginx/arl-certs /var/cache/nginx /usr/share/nginx/html
COPY docker/frontend/ /usr/share/nginx/html/
COPY --from=frontend-builder /frontend/dist/ /usr/share/nginx/html/next/
COPY docker/compose/nginx.conf /etc/nginx/nginx.conf
COPY docker/compose/docker-gateway.sh /usr/local/bin/docker-gateway.sh
RUN chmod +x /usr/local/bin/docker-gateway.sh
USER 10001:10001
ENTRYPOINT ["/usr/local/bin/docker-gateway.sh"]
