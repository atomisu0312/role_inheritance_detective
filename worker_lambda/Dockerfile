# Base image
FROM python:3.13-slim-bookworm AS base
WORKDIR /app

# Install uv
RUN pip install uv

# Build stage
FROM base AS builder

COPY pyproject.toml uv.lock ./
# パッケージ構造をコピー（setuptoolsがパッケージを認識するために必要）
COPY __init__.py ./
COPY . .
RUN uv sync --frozen --no-dev

# Production stage
FROM base AS prod

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy Python packages from virtual environment
COPY --from=builder /app/.venv/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

# AWS Lambdaにデプロイしても動くように修正
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1 /lambda-adapter /opt/extensions/lambda-adapter
COPY . .

ENTRYPOINT ["python3", "-m", "uvicorn"]
CMD ["main:app", "--host", "0.0.0.0", "--port", "8080"]