#!/bin/bash

set -euo pipefail

PORT=10000
curl -X POST http://localhost:$PORT/init > /dev/null 2>&1