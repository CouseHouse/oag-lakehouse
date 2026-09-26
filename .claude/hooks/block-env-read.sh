#!/usr/bin/env bash
# PreToolUse hook: refuse any Bash command or file read that touches a live .env file.
# Allowed: .env.example (a template with no values). Blocked: .env, .env.local, .env.<anything else>.
set -euo pipefail
input="$(cat)"
tool="$(printf '%s' "$input" | jq -r '.tool_name // empty')"
case "$tool" in
  Bash) text="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')" ;;
  Read|Grep|Glob) text="$(printf '%s' "$input" | jq -r '[.tool_input.file_path?, .tool_input.path?, .tool_input.pattern?] | map(select(. != null)) | join(" ")')" ;;
  *) exit 0 ;;
esac
# Strip the allowed template name, then look for any remaining .env reference.
stripped="$(printf '%s' "$text" | sed -E 's/\.env\.example//g')"
if printf '%s' "$stripped" | grep -Eq '(^|[^A-Za-z0-9_])\.env([./][A-Za-z0-9_.-]*)?($|[^A-Za-z0-9_])'; then
  jq -n '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:"Hard rule: the live .env file is never read by Claude. Use .env.example for variable names; values stay local."}}'
  exit 0
fi
exit 0
