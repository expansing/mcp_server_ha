ARG BUILD_FROM=ghcr.io/hassio-addons/base:18.0.0

FROM ${BUILD_FROM}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml
COPY src /app/src
COPY tests /app/tests

RUN python3 -m venv /app/venv \
    && /app/venv/bin/pip install --no-cache-dir -e ".[dev]"

COPY run /app/run
RUN chmod +x /app/run

WORKDIR /app

CMD ["/app/run"]
