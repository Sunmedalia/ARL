# ARM64 scanner compatibility image. API/AI and gateway use their dedicated
# lightweight images; this image contains only worker runtime and scanners.
ARG PYTHON_IMAGE=python:3.11.12-slim-bookworm

FROM ubuntu:20.04 AS scanner-builder
ARG DEBIAN_FRONTEND=noninteractive
ARG NUCLEI_VERSION=3.2.4
ARG NUCLEI_SHA256=11392e74a90f994c643a5b007b5ee7edfb14d60acbc40c7ec6e99e585381ea7a
ARG MASSDNS_COMMIT=6bfa47197d78e68b79041d494e280174cb2d6ae1
WORKDIR /opt
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates g++ git libssl-dev make wget zlib1g-dev unzip \
    && git init /opt/massdns \
    && git -C /opt/massdns remote add origin https://github.com/blechschmidt/massdns.git \
    && git -C /opt/massdns fetch --depth 1 origin "$MASSDNS_COMMIT" \
    && git -C /opt/massdns checkout --detach FETCH_HEAD \
    && make -C /opt/massdns \
    && wget -q "https://nmap.org/ncrack/dist/ncrack-0.7.tar.gz" \
    && echo "f3f971cd677c4a0c0668cb369002c581d305050b3b0411e18dd3cb9cc270d14a  ncrack-0.7.tar.gz" | sha256sum -c - \
    && tar -xzf "ncrack-0.7.tar.gz" \
    && cd "ncrack-0.7" \
    && ./configure \
    && make \
    && wget -q "https://github.com/projectdiscovery/nuclei/releases/download/v${NUCLEI_VERSION}/nuclei_${NUCLEI_VERSION}_linux_arm64.zip" -O /tmp/nuclei.zip \
    && echo "$NUCLEI_SHA256  /tmp/nuclei.zip" | sha256sum -c - \
    && unzip /tmp/nuclei.zip nuclei -d /opt \
    && chmod +x /opt/nuclei

FROM ${PYTHON_IMAGE} AS python-builder
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /build
COPY requirements.txt ./requirements.txt
COPY tools/ARL-NPoC/ ./ARL-NPoC/
RUN python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip install --no-cache-dir -r ARL-NPoC/requirements.txt \
    && python -m pip install --no-cache-dir ./ARL-NPoC

FROM ${PYTHON_IMAGE}
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
COPY --from=scanner-builder /opt/ncrack-0.7/ncrack /usr/local/bin/ncrack
COPY --from=scanner-builder /opt/ncrack-0.7/ncrack-services /usr/local/share/ncrack/ncrack-services
COPY --from=scanner-builder /opt/massdns/bin/massdns app/tools/massdns
COPY --from=scanner-builder /opt/nuclei /usr/bin/nuclei
COPY tools/wih/wih_linux_arm64 /usr/bin/wih
COPY tools/GeoLite2-ASN.mmdb /data/GeoLite2/GeoLite2-ASN.mmdb
COPY tools/GeoLite2-City.mmdb /data/GeoLite2/GeoLite2-City.mmdb
RUN echo "92b31cc60ee9223bead4b74dd4ecc2c7179c0ed9333689558c7cbc86325b540b  /usr/bin/wih" | sha256sum -c - \
    && chmod +x /usr/local/bin/ncrack /usr/bin/nuclei /usr/bin/wih app/tools/* \
    && ln -s /code/app/tools/phantomjs /usr/bin/phantomjs \
    && cp app/config.yaml.example app/config.yaml \
    && mkdir -p app/tmp app/tmp_screenshot /root/nuclei-templates \
    && chown root:10001 app/tmp app/tmp_screenshot \
    && chmod 0770 app/tmp app/tmp_screenshot
RUN FLASK_APP=app.main:arl_app python -m flask routes >/dev/null
