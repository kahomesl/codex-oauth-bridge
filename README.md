# Codex OAuth Bridge for Claude Desktop & Qoder

**[简体中文](README.zh-CN.md) | English**

A practical, **unofficial**, reproducible macOS guide and configuration toolkit for connecting an authorized **ChatGPT/Codex OAuth session** to **Claude Desktop**, **CC Switch**, and **Qoder** through a local **Anthropic Messages-compatible API gateway**.

> **This is not an official OpenAI, Anthropic, Claude, Qoder, or CC Switch product.** It is a third-party interoperability playbook built around [brianconnoly/claude-codex-proxy](https://github.com/brianconnoly/claude-codex-proxy); it does not bundle that upstream project's source code. Access, models, and supported authentication methods may change. Use only in accordance with your service agreements and regional availability. A ChatGPT subscription does not automatically grant access to every model or unrestricted API usage.

### Who is this for?

You have a locally authorized Codex session on your Mac, want a single localhost gateway for multiple AI desktop or IDE clients, and prefer repeatable setup, validation, safety checks, and troubleshooting over copying live credentials between apps.

## At a glance

| Component | Connection | Role |
|---|---|---|
| Local Node.js gateway | `http://127.0.0.1:8787` | Anthropic-compatible `/v1/messages` and `/v1/models` |
| Claude Desktop | Third-party inference Gateway | Uses Claude-shaped model aliases |
| CC Switch | Claude Desktop **Direct** provider | Switches providers; avoid double-mapping model IDs |
| Qoder | **Anthropic Compatible** custom provider | Uses the same local URL and aliases |
| Codex OAuth | Authorized locally, in the upstream gateway | **Never** copied into client API Key fields |

```text
Claude Desktop ─┐
CC Switch       ├──> 127.0.0.1:8787 (Anthropic Messages gateway)
Qoder           ┘             └──> HTTPS → authorized Codex service
```

The default example gateway key `local` is **not your OAuth access token**. Keep the server bound to `127.0.0.1`; never publish this gateway on the internet with a demo key.

## Quick start (macOS)

1. Read [prerequisites and safety](docs/01-preflight.md) and [English quick start](docs/quickstart-en.md). Install Node.js, Git, and Python 3, and ensure you can authorize the required service.
2. Clone the **upstream** `claude-codex-proxy` separately and follow [OAuth setup](docs/02-setup-macos.md). Keep OAuth token files and real `.env` values local.
3. Run `python3 scripts/install_legacy_8.py --check` and, if compatible, `--apply`, then `python3 scripts/set_final_models.py --check` and `--apply` from this toolkit directory. **Only apply to a compatible, backed-up upstream checkout**. The first script enables per-alias routing; the second selects the final presets.
4. Test `/health`, `/v1/models`, and an actual `/v1/messages` request. The health endpoint alone does not prove upstream auth works.
5. Follow the [Claude Desktop / CC Switch](docs/05-claude-desktop.md) or [Qoder](docs/06-qoder.md) configuration instructions.

For a machine with a working proxy, **do not reinstall or create another LaunchAgent**. Use [maintenance](docs/08-maintenance.md) and [troubleshooting](docs/07-troubleshooting.md).

## Model alias presets

These are **local aliases, not official Claude model IDs**. Your upstream permissions determine what actually works.

| Alias (send as `model`) | Upstream model target | Reasoning effort | Suggested menu label |
|---|---|---|---|
| `claude-haiku-luna-low` | `gpt-6-luna` | low | GPT-6 Luna · Low |
| `claude-haiku-luna-medium` | `gpt-6-luna` | medium | GPT-6 Luna · Medium |
| `claude-haiku-luna-high` | `gpt-6-luna` | high | GPT-6 Luna · High |
| `claude-opus-sol61-low` | `gpt-6.1-sol` | low | GPT-6.1 Sol · Low |
| `claude-opus-sol61-medium` | `gpt-6.1-sol` | medium | GPT-6.1 Sol · Medium |
| `claude-opus-sol61-high` | `gpt-6.1-sol` | high | GPT-6.1 Sol · High |
| `claude-opus-astra-low` | `gpt-6-astra` | low | GPT-6 Astra · Low |
| `claude-opus-astra-medium` | `gpt-6-astra` | medium | GPT-6 Astra · Medium |

**Important:** model discovery and UI labels do **not** establish upstream access. Test a small real request for each model before relying on it. Context-window controls in the clients (200K/400K/1M) are **not** proof of an equally large upstream input budget. [Read the limits](docs/03-model-presets.md).

## Minimal checks

```bash
# Local listener only; does not validate OAuth
curl --noproxy '*' -fsS http://127.0.0.1:8787/health

# Gateway-discovered model aliases
curl --noproxy '*' -fsS http://127.0.0.1:8787/v1/models | python3 -m json.tool

# Optional real upstream test; uses subscription quota
curl --noproxy '*' -sS --max-time 120 -w '\nHTTP %{http_code}\n' \
  http://127.0.0.1:8787/v1/messages \
  -H 'content-type: application/json' -H 'x-api-key: local' \
  -d '{"model":"claude-haiku-luna-medium","max_tokens":64,"messages":[{"role":"user","content":"Reply OK"}]}'

# Local diagnostic (never share credential files)
bash scripts/doctor.sh
```

## Common problems

| Symptom | First check | Guide |
|---|---|---|
| `HTTP 500`, `fetch failed` | System HTTP proxy port and LaunchAgent environment | [Troubleshooting](docs/07-troubleshooting.md) |
| `HTTP 401`, token expired | Local OAuth renewal / reauthorization | [OAuth setup](docs/02-setup-macos.md) |
| Model visible but requests fail | Account eligibility and exact alias-to-model routing | [Presets](docs/03-model-presets.md) |
| Claude Desktop context shows 200K, compaction slow | Client-native compaction vs gateway compaction; enabled MCP tools | [Context notes](docs/03-model-presets.md) |
| Qoder validation failed | Anthropic-compatible protocol, correct root URL, and real request response | [Qoder](docs/06-qoder.md) |

## Documentation

**English:** [Quick start](docs/quickstart-en.md) · [FAQ / troubleshooting](docs/faq-en.md) · [Security](SECURITY.md) · [Contributing](CONTRIBUTING.md)

**中文：** [完整中文首页](README.zh-CN.md) · [macOS 安装](docs/02-setup-macos.md) · [八档模型](docs/03-model-presets.md) · [Claude Desktop](docs/05-claude-desktop.md) · [Qoder](docs/06-qoder.md) · [排错](docs/07-troubleshooting.md) · [维护](docs/08-maintenance.md)

**For maintainers and AI-assisted debugging:** [AI handoff](docs/09-ai-handoff.md) · [Validation scope](docs/11-validation-status.md) · [Search visibility](docs/discoverability.md) · [Public release safety check](docs/public-release-checklist.md)

## Security and provenance

This repository contains only docs, example environment values, and generic setup scripts. It must never include `.auth/codex.json`, real `.env`, personal database files, terminal transcripts with credentials, provider API keys, or OAuth refresh tokens. The release audit script is a **best-effort heuristic**, not a substitute for manual review. See [SECURITY.md](SECURITY.md).

Original dependencies and references: [claude-codex-proxy](https://github.com/brianconnoly/claude-codex-proxy), [CC Switch](https://github.com/farion1231/cc-switch). Their trademarks, licenses, and service requirements remain with their owners.

**License:** MIT, for this repository's original content only. This license does not override upstream licenses or third-party terms.
