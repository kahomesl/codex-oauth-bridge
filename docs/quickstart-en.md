# Quick start: ChatGPT/Codex OAuth → Claude Desktop / Qoder (macOS)

[Home](../README.md) · [中文首页](../README.zh-CN.md) · [FAQ](faq-en.md)

This is an **unofficial** compatibility guide. Confirm your account and client are authorized to use the selected service; this setup does not create permissions or guarantee access to any model.

## Prerequisites

- macOS, Node.js/npm, Git, Python 3, and a network path to the authorized service.
- A checkout of [claude-codex-proxy](https://github.com/brianconnoly/claude-codex-proxy) **separate** from this repository.
- No other process already listening on `127.0.0.1:8787`; if one exists, read [maintenance](08-maintenance.md) rather than installing again.

## 1. Install the upstream proxy

```bash
git clone https://github.com/brianconnoly/claude-codex-proxy.git "$HOME/claude-codex-proxy"
cd "$HOME/claude-codex-proxy"
npm install
cp -n .env.example .env
chmod 600 .env
```

Review `.env`: use `HOST=127.0.0.1`, `PORT=8787`, `UPSTREAM=codex`, and the selected fallback models. If the upstream version has changed, **do not force incompatible patch scripts onto it**.

## 2. Sign in locally

Use the upstream `npm run auth` interaction. If outbound HTTP(S) needs a *local* macOS proxy, inspect `scutil --proxy` and configure the real HTTP proxy port for this process. Example (replace port as needed):

```bash
HTTP_PROXY=http://127.0.0.1:10808 \
HTTPS_PROXY=http://127.0.0.1:10808 \
NO_PROXY=127.0.0.1,localhost NODE_USE_ENV_PROXY=1 npm run auth
```

Never copy `.auth/codex.json` or any refresh token into Claude Desktop, Qoder, CC Switch, chat, or GitHub. Do not share the OAuth callback URL containing a one-time authorization code.

## 3. Apply per-alias model routing

From **this toolkit repository** (the path containing `scripts/`):

```bash
python3 scripts/install_legacy_8.py --check
python3 scripts/install_legacy_8.py --apply
python3 scripts/set_final_models.py --check
python3 scripts/set_final_models.py --apply
```

Each application requires a compatible source checkout and writes local backups. Inspect dry-run results and allow only intended changes. The first script adds exact per-ID effort/display mapping to the upstream proxy; the second selects [eight current presets](03-model-presets.md). The upstream project does not necessarily ship these extra keys.

## 4. Start and validate

Start the proxy with the necessary HTTP(S)_PROXY environment if required, then in a second Terminal:

```bash
curl --noproxy '*' -fsS http://127.0.0.1:8787/health
curl --noproxy '*' -fsS http://127.0.0.1:8787/v1/models | python3 -m json.tool
```

Then use the [real request in the README](../README.md#minimal-checks) to validate actual upstream access. Sending a real request consumes quota.

## 5. Point clients to localhost

| Client | Provider type | Base URL | Client key |
|---|---|---|---|
| Claude Desktop | Third-party inference / Gateway | `http://127.0.0.1:8787` | Example `local` |
| CC Switch (Claude Desktop) | Direct | `http://127.0.0.1:8787` | Same local gateway key |
| Qoder | Anthropic Compatible | `http://127.0.0.1:8787` | Same local gateway key |

Keep the `model` value equal to an alias in [the model table](../README.md#model-alias-presets). Do **not** send bare upstream model names if you want the custom per-alias effort configuration.

For automatic start, follow [LaunchAgent guidance](04-launchagent.md) only after stopping the foreground process and verifying no existing service. See [troubleshooting](07-troubleshooting.md) for port changes or expired OAuth tokens.
