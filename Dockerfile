FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock README.md /app/
COPY src /app/src
COPY scripts/docker/start.sh /app/scripts/docker/start.sh

RUN pip install --no-cache-dir uv \
    && uv pip install --system -e .

EXPOSE 8000

CMD ["/bin/sh", "/app/scripts/docker/start.sh"]
