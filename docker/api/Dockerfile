ARG PYTHON_IMAGE=python:3.11.12-slim-bookworm

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
    PYTHONUNBUFFERED=1 \
    PATH=/home/arl/.local/bin:$PATH
WORKDIR /code
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 arl \
    && useradd --uid 10001 --gid arl --create-home --shell /usr/sbin/nologin arl
COPY --from=python-builder /usr/local /usr/local
COPY app/ app/
COPY arl_tool/ arl_tool/
RUN cp app/config.yaml.example app/config.yaml \
    && rm -f app/tools/phantomjs app/tools/massdns \
    && mkdir -p app/tmp app/tmp_screenshot \
    && chown -R arl:arl /code /home/arl \
    && chmod 0770 app/tmp app/tmp_screenshot
USER 10001:10001
RUN FLASK_APP=app.main:arl_app python -m flask routes >/dev/null
