FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

ARG TIMEZONE=America/Sao_Paulo

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    TZ=${TIMEZONE}

RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY pyproject.toml uv.lock ./
COPY src ./src
COPY .setup/docker/streamlit/config.toml ./.streamlit/config.toml

RUN uv sync --frozen --no-dev

ENV PATH="/code/.venv/bin:$PATH" \
    PYTHONPATH=/code

EXPOSE 8501

HEALTHCHECK CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8501/_stcore/health')"

CMD ["streamlit", "run", "src/main.py", "--server.address=0.0.0.0", "--server.port=8501"]
