# Public release review — STOP before any remote change

**Status:** proposal only. This package is not a GitHub repository yet and must not automatically create, push, or change the visibility of any remote repository.

## Proposed GitHub metadata (copy manually after approval)

**Repository name:** `codex-oauth-bridge`

**Repository title:** Codex OAuth Bridge for Claude Desktop & Qoder

**Description:** `Unofficial ChatGPT/Codex OAuth localhost bridge for Claude Desktop, Qoder and CC Switch on macOS. Anthropic-compatible gateway, model routing, setup and troubleshooting.`

**Topics:** `codex`, `codex-oauth`, `chatgpt`, `claude-desktop`, `qoder`, `cc-switch`, `anthropic-api`, `local-proxy`, `macos`, `model-routing`

**Website:** leave blank until a real documentation website exists. Do not link a nonexistent GitHub Pages site.

**License:** MIT for the repository's own work only.

## Privacy approval gates

- [ ] Inspect every file with `find . -type f -not -path './.git/*'` and `git diff --cached --name-only` (if staging in Git).
- [ ] Run `python3 scripts/public_release_audit.py --strict` and review every finding; scanner is heuristic.
- [ ] Check `git log --format=fuller` and `git cat-file -p HEAD` after committing: no personal full name, machine hostname, private email or non-public source repository references.
- [ ] Configure Git author/committer identity **before first commit** using a permitted display name (e.g. `Open Source Contributor`) and your own GitHub `noreply` address. Do not invent a specific `noreply` address; get it from GitHub settings.
- [ ] Never copy `.git` from the private source. Start from this sanitized snapshot as a NEW root commit.
- [ ] Confirm no OAuth files, API keys, real `.env`, databases, private documents, screenshots, backups, private Git URLs or private issue/Actions content.
- [ ] Confirm all external links point only to intended public sources and no links disclose private repositories.
- [ ] Verify shell and Python tests pass; test a new machine before claiming a one-command installation.
- [ ] Review the compatibility and service-terms disclaimers in the English and Chinese README.
- [ ] Make an explicit human decision to publish; **do not create a public GitHub repo without approval**.

## Future release procedure (after approval, not executed here)

1. Create an empty, separate public repository using the chosen name. No fork/transfer from a private repository.
2. Initialize the reviewed folder with **fresh** `.git` history after setting the intended Git author and email; do not import old commits, tags or workflows.
3. Inspect the first staged commit and re-run the audit; publish only the newly reviewed files.
4. Configure Description and Topics in **About** after publication and keep README titles/links current.
5. Optionally add a reviewed 1280×640 social-preview image via GitHub Settings → General → Social preview. Do not assume GitHub automatically derives one.
6. Add a link on your GitHub profile and cross-reference the relevant public upstream project only when appropriate and allowed.
7. Verify repository privacy state, Actions log visibility and any code scanning alerts. Search engines and AI answers are **not guaranteed** to index or cite the project.

## Discoverability / SEO

Search queries this repository should answer naturally: “ChatGPT Codex OAuth Claude Desktop”, “Qoder Anthropic compatible localhost proxy”, “CC Switch Claude Desktop local gateway”, “Codex OAuth HTTP 401 token expired”, “Codex proxy HTTP 500 fetch failed”, “Claude context 200K 400K compaction”.

Keep answers accurate and link specific related pages from both README files. Do **not** keyword-stuff, fabricate usage stats or testimonials, or add `llms.txt` claiming guaranteed AI indexing. Search engines and AI systems discover useful **public, crawlable, text-based** content on their own schedules.
