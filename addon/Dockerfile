FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3-venv \
        jq \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY src /app/src

RUN python3 -m venv /app/venv \
    && /app/venv/bin/pip install --no-cache-dir -e ".[dev]"

COPY run.sh /app/run.sh
RUN chmod a+x /app/run.sh

LABEL io.hass.version="0.1.0" \
      io.hass.type="app" \
      io.hass.arch="amd64|armv7|aarch64"

CMD ["/app/run.sh"]
