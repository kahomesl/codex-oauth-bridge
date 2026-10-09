# Security policy / 安全说明

## Scope

This repository contains documentation, templates, and local setup tools. **It does not provide an official authentication product or a hosted gateway.** Keep the upstream gateway bound to `127.0.0.1`; do not expose port 8787 publicly with the example key `local`. A local compatible API key is **not** your OAuth credential.

## Never publish / 禁止公开

- OAuth access/refresh tokens, `.auth/codex.json`, callback URLs with one-time codes, API keys, browser cookies or browser profiles.
- A real `.env`, provider database (including `cc-switch.db`), app preference exports, entire Claude/Qoder configuration, logs with credentials, or private client messages.
- Git commit identities, screenshots, file metadata or terminal transcripts that expose information you do not want public.

The included `python3 scripts/public_release_audit.py --strict` catches common patterns; it cannot guarantee the absence of all secrets or personal information. Perform a manual review **including Git history and commit metadata** before making any repository public.

## Vulnerability reports

If this repository is made public, use GitHub's **Report a vulnerability / private vulnerability reporting** (if enabled) for sensitive reports. Do not publish working credentials, exploit tokens, or private conversation data in a public issue. For ordinary documentation bugs, open an issue without sensitive data.

## Dependencies and terms

`claude-codex-proxy`, the clients and the remote service have independent licenses, terms, access controls and potential vulnerabilities. Do not claim that this toolkit bypasses regional availability or grants access to any subscription entitlement. Reconfirm supported upstream models before relying on them.

## Local installation / 本地安装

Back up files, run `--check` first, review modifications, test, then `--apply`. Start or restart services only when idle. Never run remote setup scripts blindly or copy secrets to outside services.
