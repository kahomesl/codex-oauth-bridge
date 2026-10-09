# Contributing / 贡献指南

Contributions to documentation, tests and safer local diagnostics are welcome **after publication**.

- Do not paste a real `.env`, `codex.json`, HTTP Authorization header, one-time OAuth code, cookies, terminal username/hostname, or identifiable project content in issues or pull requests.
- Document reproducible non-sensitive examples. Distinguish locally observed behavior from guarantees made by any upstream provider.
- Preserve both [English](README.md) and [Chinese](README.zh-CN.md) entry points when editing shared workflows.
- Run `python3 scripts/public_release_audit.py --strict` and `python3 -m unittest discover -s tests -v` before submitting.
- Do not turn model access assumptions, backend endpoints, or unsupported authentication methods into promises. Service terms and permissions control what is available.

This repository is unaffiliated with OpenAI, Anthropic, Qoder, CC Switch, or the upstream proxy authors.
