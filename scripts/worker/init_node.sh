#!/bin/bash

set -eCu

PORT=10001
curl -X POST http://localhost:$PORT/init > /dev/null 2>&1