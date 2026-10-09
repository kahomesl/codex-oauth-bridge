#!/bin/bash
# Launch-time macOS system HTTP proxy autodiscovery for Node fetch.
# Does not log or read OAuth token contents.
set -euo pipefail

PROXY_DIR="${CODEX_BRIDGE_PROJECT:-$HOME/claude-codex-proxy}"
NODE_EXEC="${CODEX_BRIDGE_NODE:-}"
if [[ -z "$NODE_EXEC" ]]; then
  NODE_EXEC="$(command -v node || true)"
fi
if [[ ! -x "$NODE_EXEC" ]]; then
  echo "Node executable unavailable; set CODEX_BRIDGE_NODE to an absolute path" >&2
  exit 1
fi
if [[ ! -f "$PROXY_DIR/src/server.js" ]]; then
  echo "Expected proxy source missing: $PROXY_DIR/src/server.js" >&2
  exit 1
fi

PROXY_URL="${CODEX_BRIDGE_PROXY_URL:-}"
if [[ -z "$PROXY_URL" ]] && command -v scutil >/dev/null 2>&1; then
  system_proxy="$(scutil --proxy)"
  host="$(awk '$1=="HTTPSProxy" {print $3; exit}' <<< "$system_proxy")"
  port="$(awk '$1=="HTTPSPort" {print $3; exit}' <<< "$system_proxy")"
  enabled="$(awk '$1=="HTTPSEnable" {print $3; exit}' <<< "$system_proxy")"
  if [[ "$enabled" != "1" ]]; then
    host="$(awk '$1=="HTTPProxy" {print $3; exit}' <<< "$system_proxy")"
    port="$(awk '$1=="HTTPPort" {print $3; exit}' <<< "$system_proxy")"
    enabled="$(awk '$1=="HTTPEnable" {print $3; exit}' <<< "$system_proxy")"
  fi
  if [[ "$enabled" == "1" && -n "$host" && "$port" =~ ^[0-9]+$ ]]; then
    PROXY_URL="http://${host}:${port}"
  fi
fi

if [[ -n "$PROXY_URL" ]]; then
  if [[ "$PROXY_URL" != http://* ]]; then
    echo "Expected an HTTP(S) CONNECT proxy URL beginning http:// (SOCKS-only is unsupported)" >&2
    exit 1
  fi
  export HTTP_PROXY="$PROXY_URL" HTTPS_PROXY="$PROXY_URL"
  export http_proxy="$PROXY_URL" https_proxy="$PROXY_URL"
  echo "Codex bridge: outgoing HTTP proxy configured from Mac settings" >&2
else
  unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy || true
  echo "Codex bridge: no enabled macOS HTTP proxy; attempting direct network access" >&2
fi
export NO_PROXY="127.0.0.1,localhost,::1"
export no_proxy="$NO_PROXY"
export NODE_USE_ENV_PROXY=1
cd "$PROXY_DIR"
exec "$NODE_EXEC" "$PROXY_DIR/src/server.js"
