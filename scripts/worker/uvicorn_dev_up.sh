#!/bin/bash

set -euo pipefail

PORT=10001

cd ./worker_lambda

# ソースの変更を検知できるようにリロードを有効にしている
uv run uvicorn main:app --host "0.0.0.0" --port $PORT --reload