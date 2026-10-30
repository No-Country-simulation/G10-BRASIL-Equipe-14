FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /code

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY .setup/docker/streamlit/config.toml ./.streamlit/config.toml
COPY src ./src

ENV PATH="/code/.venv/bin:$PATH"

EXPOSE 8501

HEALTHCHECK CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8501/_stcore/health')"

CMD ["streamlit", "run", "src/main.py", "--server.address=0.0.0.0", "--server.port=8501"]
