# Scanner image. ARL's bundled scanner executables are x86_64-only, so this
# image deliberately targets amd64. API, AI and gateway use separate images.
ARG PYTHON_IMAGE=python:3.11.12-slim-bookworm
FROM --platform=linux/amd64 ${PYTHON_IMAGE} AS python-builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build
COPY requirements.txt ./requirements.txt
COPY tools/ARL-NPoC/ ./ARL-NPoC/
RUN python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip install --no-cache-dir -r ARL-NPoC/requirements.txt \
    && python -m pip install --no-cache-dir ./ARL-NPoC

FROM --platform=linux/amd64 ${PYTHON_IMAGE} AS scanner-assets
COPY tools/nuclei.zip /tmp/nuclei.zip
RUN mkdir -p /out \
    && python -c "import zipfile; zipfile.ZipFile('/tmp/nuclei.zip').extract('nuclei', '/out')" \
    && chmod +x /out/nuclei

FROM --platform=linux/amd64 ${PYTHON_IMAGE}
ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /code
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        fontconfig fonts-wqy-microhei nmap \
    && rm -rf /var/lib/apt/lists/*
COPY --from=python-builder /usr/local /usr/local
COPY app/ app/
COPY arl_tool/ arl_tool/
COPY tools/ncrack /usr/local/bin/ncrack
COPY tools/ncrack-services /usr/local/share/ncrack/ncrack-services
COPY tools/GeoLite2-ASN.mmdb /data/GeoLite2/GeoLite2-ASN.mmdb
COPY tools/GeoLite2-City.mmdb /data/GeoLite2/GeoLite2-City.mmdb
COPY --from=scanner-assets /out/nuclei /usr/bin/nuclei
COPY tools/wih/wih_linux_amd64 /usr/bin/wih
RUN chmod +x /usr/local/bin/ncrack /usr/bin/nuclei /usr/bin/wih app/tools/* \
    && ln -s /code/app/tools/phantomjs /usr/bin/phantomjs \
    && cp app/config.yaml.example app/config.yaml \
    && mkdir -p app/tmp app/tmp_screenshot /root/nuclei-templates \
    && chown root:10001 app/tmp app/tmp_screenshot \
    && chmod 0770 app/tmp app/tmp_screenshot
RUN FLASK_APP=app.main:arl_app python -m flask routes >/dev/null
