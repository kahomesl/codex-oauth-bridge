# AI maintainer handoff / 给后续 AI 助手

Start by reading the [README](../README.md), [中文首页](../README.zh-CN.md), [model presets](03-model-presets.md), [security](../SECURITY.md) and [validation boundaries](11-validation-status.md).

**This repository is a portable reference, not evidence of the current machine state.** Do not claim local files or daemon status have been verified without checking the user's actual environment. Never request or reproduce OAuth access/refresh token files, provider databases, API keys or browser cookies.

Architecture: an authorized upstream `claude-codex-proxy` checkout normally runs a localhost Anthropic Messages gateway on `127.0.0.1:8787`. Claude Desktop / CC Switch Direct / Qoder Anthropic Compatible use the gateway. The gateway selects GPT model and effort from exact model aliases (see the current README); the client menu labels are separate.

Recommended read-only diagnostic sequence:

1. `curl --noproxy '*' http://127.0.0.1:8787/health` and inspect listener (does not prove upstream works).
2. `scutil --proxy` plus running service proxy environment: distinguish outbound network failure from local service failure.
3. Fetch `/v1/models`; use one authorized, short `/v1/messages` request to validate a specific model (consumes quota).
4. Inspect the installed proxy's `resolveModelProfile()` and `.env` **without printing credentials**.
5. Only then inspect client settings, `labelOverride`, 200K/400K window selections, or compaction.

Change policy: make a backup, run `--check`, test, apply with explicit user approval, and restart only after idle. Never automatically create GitHub repos or switch repository visibility. Respect regional access and service terms.

For public distribution, do not copy private Git history or identify the original user's machine, account, hostname or local paths. See [public release checklist](public-release-checklist.md).
