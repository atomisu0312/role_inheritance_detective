#!/bin/bash
set -euo pipefail

# 環境変数の設定
OPENAI_API_KEY="${OPENAI_API_KEY:-your-api-key-here}"

# サンプル値
SYSTEM_PROMPT="あなたは経験豊富なコードレビュアーです。"
USER_PROMPT="## 差分

\`\`\`diff
+ def hello():
+     print(\"Hello, World!\")
- print(\"Hello\")
\`\`\`"

# jqでJSONを生成してcurlに渡す
jq -n \
  --arg model "gpt-5-nano" \
  --arg system "$SYSTEM_PROMPT" \
  --arg user "$USER_PROMPT" \
  '{
    model: $model,
    messages: [
      {role: "system", content: $system},
      {role: "user", content: $user}
    ],
    max_completion_tokens: 15000
  }' | curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${OPENAI_API_KEY}" \
  -d @- | jq '.'

