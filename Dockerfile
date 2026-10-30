FROM python:3.14.8-slim
COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy PATH="/app/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml uv.lock ./
# Optional corporate CA bundle, mounted only while installing dependencies.
RUN --mount=type=cache,target=/root/.cache/uv --mount=type=secret,id=ca_bundle \
    if [ -f /run/secrets/ca_bundle ]; then \
      SSL_CERT_FILE=/run/secrets/ca_bundle uv sync --frozen --no-dev; \
    else uv sync --frozen --no-dev; fi
COPY . .
RUN useradd --create-home --uid 10001 api && mkdir -p /data && chown -R api:api /app /data
USER api
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=30s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/espacios', timeout=2)"
CMD ["sh", "scripts/start.sh"]
