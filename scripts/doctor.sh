#!/bin/bash
# Safe diagnostics without reading credential values.
set -u
printf '%s\n' '== Codex bridge local health =='
curl --noproxy '*' -sS --max-time 3 http://127.0.0.1:8787/health || true
printf '\n%s\n' '== Listener =='
lsof -nP -iTCP:8787 -sTCP:LISTEN || true
printf '\n%s\n' '== macOS HTTP system proxy (non-secret) =='
if command -v scutil >/dev/null; then
  scutil --proxy | grep -E 'HTTPProxy|HTTPPort|HTTPEnable|HTTPSProxy|HTTPSPort|HTTPSEnable' || true
fi
printf '\n%s\n' '== Discovered Claude aliases =='
if command -v python3 >/dev/null; then
  curl --noproxy '*' -sS --max-time 4 http://127.0.0.1:8787/v1/models | python3 -c 'import json,sys; print("\n".join(item.get("id", "") for item in json.load(sys.stdin).get("data", []) if "luna" in item.get("id", "") or "astra" in item.get("id", "") or "sol61" in item.get("id", "")))' || true
fi
printf '\nNote: /health shows local server only; test real /v1/messages for upstream.\n'
