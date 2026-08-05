FROM node:22-bookworm-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim-bookworm

ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential curl fontconfig fonts-wqy-microhei nginx nmap unzip wget \
    && rm -rf /var/lib/apt/lists/*

COPY app/ app/
COPY test/ test/
COPY requirements.txt requirements.txt
COPY docker/frontend/ frontend/
COPY --from=frontend-builder /frontend/dist/ frontend-next/
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/worker/gen_crt.sh /usr/bin/gen_crt.sh
COPY docker/worker/wait-for-it.sh /usr/bin/wait-for-it.sh

COPY tools/ncrack /usr/local/bin/ncrack
COPY tools/ncrack-services /usr/local/share/ncrack/ncrack-services
COPY tools/ARL-NPoC/ /opt/ARL-NPoC/
COPY tools/GeoLite2-ASN.mmdb /data/GeoLite2/GeoLite2-ASN.mmdb
COPY tools/GeoLite2-City.mmdb /data/GeoLite2/GeoLite2-City.mmdb
COPY tools/nuclei.zip /tmp/nuclei.zip
COPY tools/wih/wih_linux_amd64 /usr/bin/wih

RUN chmod +x /usr/local/bin/ncrack /usr/bin/wih app/tools/* \
    && ln -s /code/app/tools/phantomjs /usr/bin/phantomjs \
    && unzip /tmp/nuclei.zip nuclei -d /usr/bin \
    && chmod +x /usr/bin/nuclei \
    && rm /tmp/nuclei.zip \
    && python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip install --no-cache-dir -r /opt/ARL-NPoC/requirements.txt \
    && python -m pip install --no-cache-dir -e /opt/ARL-NPoC

RUN curl https://ssl-config.mozilla.org/ffdhe2048.txt -o /etc/ssl/certs/dhparam.pem

# Import the application during the image build to catch dependency and route
# registration failures. Runtime configuration is mounted separately.
RUN cp app/config.yaml.example app/config.yaml \
    && FLASK_APP=app.main:arl_app python -m flask routes \
    && rm app/config.yaml
