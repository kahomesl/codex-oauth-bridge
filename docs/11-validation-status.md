# Validation scope / 验证范围

## Known reproducible checks (snapshot prepared October 2026)

- Python scripts provide `--check`/`--apply` and backup/error handling; unit tests exercise documented transformations.
- Localhost `/health`, model discovery, and the Anthropic-compatible Messages request can be tested individually.
- Claude Desktop and Qoder can show custom model aliases when the client version accepts them; Qoder may offer 200K/400K choices.

## Explicitly **not** guaranteed

- No guarantee of access to GPT-6 Astra, 6.1 Sol, Luna or any other named model for a different account, date, subscription or region.
- Client UI model selection or a model-discovery entry is not proof of upstream entitlement.
- `200K`, `400K`, and `1M` client UI labels are not proof of equivalent upstream input capacity.
- `/health` success does not prove OAuth/network health; unit tests do not prove a live request succeeds.
- Different versions of upstream `claude-codex-proxy`, CC Switch, Qoder or Claude Desktop may require source changes; patch scripts must reject incompatible versions rather than silently corrupt them.

The public package is deliberately separate from any private source repository, machine configuration, or Git commit history. Revalidate the local environment on each installation. Do not paste real credentials into reports or issues.
