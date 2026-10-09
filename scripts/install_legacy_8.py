#!/usr/bin/env python3
"""Patch a local claude-codex-proxy with eight GPT/Codex model presets.

This script never restarts the daemon or changes Claude Desktop/CC Switch.
Run on the Mac containing ~/claude-codex-proxy, not on the model's container.

Usage:
  python3 install_claude_plus_presets.py --check
  python3 install_claude_plus_presets.py --probe  # consumes two small Codex requests
  python3 install_claude_plus_presets.py --apply
  python3 install_claude_plus_presets.py --rollback ~/.claude-codex-proxy-preset-backups/<backup>
"""
from __future__ import annotations

import argparse
import datetime
import difflib
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import urllib.error

PRESETS = [
    ("claude-haiku-luna-none", "gpt-6-luna", "none", "GPT-6 Luna | None"),
    ("claude-haiku-luna-low", "gpt-6-luna", "low", "GPT-6 Luna | Low"),
    ("claude-haiku-luna-medium", "gpt-6-luna", "medium", "GPT-6 Luna | Medium"),
    ("claude-haiku-luna-high", "gpt-6-luna", "high", "GPT-6 Luna | High"),
    ("claude-sonnet-sol-low", "gpt-6-sol", "low", "GPT-6 Sol | Low"),
    ("claude-sonnet-sol-medium", "gpt-6-sol", "medium", "GPT-6 Sol | Medium"),
    ("claude-opus-sol61-low", "gpt-6.1-sol", "low", "GPT-6.1 Sol | Low"),
    ("claude-opus-sol61-medium", "gpt-6.1-sol", "medium", "GPT-6.1 Sol | Medium"),
]

SAFE_LEGACY = ["claude-opus-4-8", "claude-sonnet-4-6", "claude-haiku-4-5"]
ENV_SIMPLE = {
    "UPSTREAM": "codex",
    "DEFAULT_MODEL": "gpt-6-luna",
    "CLAUDE_OPUS_MODEL": "gpt-6.1-sol",
    "CLAUDE_OPUS_REASONING_EFFORT": "low",
    "CLAUDE_SONNET_MODEL": "gpt-6-luna",
    "CLAUDE_SONNET_REASONING_EFFORT": "medium",
    "CLAUDE_HAIKU_MODEL": "gpt-6-luna",
    "CLAUDE_HAIKU_REASONING_EFFORT": "low",
    "CONTEXT_COMPACT_MODEL": "gpt-6-luna",
    "CONTEXT_COMPACT_REASONING_EFFORT": "low",
    "CONTEXT_COMPACT_TEXT_VERBOSITY": "low",
}
ENV_MAP_KEYS = ("MODEL_MAP", "MODEL_EFFORT_MAP", "MODEL_DISPLAY_MAP")
CODE_PATHS = ["src/config.js", "src/anthropic.js", "src/server.js"]
TEST_PATH = "test/plus-model-presets.test.js"

TEST_CONTENT = '''import test from "node:test";
import assert from "node:assert/strict";
import { loadConfig } from "../src/config.js";
import { resolveModelProfile, anthropicToResponses } from "../src/anthropic.js";

const config = loadConfig();
const expected = [
  ["claude-haiku-luna-none", "gpt-6-luna", "none"],
  ["claude-haiku-luna-low", "gpt-6-luna", "low"],
  ["claude-haiku-luna-medium", "gpt-6-luna", "medium"],
  ["claude-haiku-luna-high", "gpt-6-luna", "high"],
  ["claude-sonnet-sol-low", "gpt-6-sol", "low"],
  ["claude-sonnet-sol-medium", "gpt-6-sol", "medium"],
  ["claude-opus-sol61-low", "gpt-6.1-sol", "low"],
  ["claude-opus-sol61-medium", "gpt-6.1-sol", "medium"],
];

for (const [alias, model, effort] of expected) {
  test(`${alias} routes to ${model}/${effort}`, () => {
    const route = resolveModelProfile(alias, config);
    assert.equal(route.model, model);
    assert.equal(route.reasoningEffort, effort);
    assert.ok(config.discoveryModels.includes(alias));
    assert.ok(config.modelDisplayMap.get(alias));
    const request = anthropicToResponses({
      model: alias,
      max_tokens: 64,
      messages: [{ role: "user", content: "ping" }],
    }, config);
    assert.equal(request.model, model);
    assert.equal(request.reasoning.effort, effort);
  });
}

test("legacy aliases still work", () => {
  assert.equal(resolveModelProfile("claude-opus-4-8", config).model, "gpt-6.1-sol");
  assert.equal(resolveModelProfile("claude-sonnet-4-6", config).model, "gpt-6-luna");
  assert.equal(resolveModelProfile("claude-haiku-4-5", config).model, "gpt-6-luna");
});
'''


def replace_once(src: str, needle: str, replacement: str, filename: str) -> str:
    if replacement in src:
        return src
    if src.count(needle) != 1:
        raise RuntimeError(f"{filename}: expected exactly one source anchor; found {src.count(needle)}")
    return src.replace(needle, replacement, 1)


def patch_code(original: dict[str, str]) -> dict[str, str]:
    result = dict(original)
    key = "src/config.js"
    result[key] = replace_once(
        result[key],
        '    modelMap: parseModelMap(env("MODEL_MAP")),',
        '    modelMap: parseModelMap(env("MODEL_MAP")),\n'
        '    modelEffortMap: parseModelMap(env("MODEL_EFFORT_MAP")),\n'
        '    modelDisplayMap: parseModelMap(env("MODEL_DISPLAY_MAP")),',
        key,
    )
    key = "src/anthropic.js"
    result[key] = replace_once(
        result[key],
        '    reasoningEffort: profile?.reasoningEffort ?? config.request.reasoningEffort,',
        '    reasoningEffort: config.modelEffortMap?.get(model) ?? profile?.reasoningEffort ?? config.request.reasoningEffort,',
        key,
    )
    key = "src/server.js"
    result[key] = replace_once(
        result[key],
        '    display_name: displayNameForModel(id),',
        '    display_name: config.modelDisplayMap?.get(id) ?? displayNameForModel(id),',
        key,
    )
    return result


def parse_csv_map(value: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for pair in value.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            raise RuntimeError(f"Invalid map entry, expected key=value: {pair!r}")
        key, entry = pair.split("=", 1)
        result[key.strip()] = entry.strip()
    return result


def patch_env(raw: str) -> str:
    # Preserve unrelated user settings and comments; replace only controlled keys.
    lines = raw.splitlines(keepends=False)
    found: dict[str, list[int]] = {}
    matcher = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=")
    for index, line in enumerate(lines):
        if not line.strip().startswith("#"):
            hit = matcher.match(line)
            if hit:
                found.setdefault(hit.group(1), []).append(index)
    for key, positions in found.items():
        if len(positions) > 1 and key in set(ENV_SIMPLE) | set(ENV_MAP_KEYS) | {"ANTHROPIC_DISCOVERY_MODELS"}:
            raise RuntimeError(f".env: {key} is defined {len(positions)} times; resolve duplicates first")

    def current(key: str) -> str:
        if key not in found:
            return ""
        return lines[found[key][0]].split("=", 1)[1].strip().strip('"').strip("'")

    model_map = parse_csv_map(current("MODEL_MAP"))
    effort_map = parse_csv_map(current("MODEL_EFFORT_MAP"))
    display_map = parse_csv_map(current("MODEL_DISPLAY_MAP"))
    for alias, model, effort, display in PRESETS:
        model_map[alias] = model
        effort_map[alias] = effort
        display_map[alias] = display
    custom_ids = [p[0] for p in PRESETS]
    discovery = [x.strip() for x in current("ANTHROPIC_DISCOVERY_MODELS").split(",") if x.strip()]
    # Keep older aliases plus eight discoverable presets. This preserves existing desktop profiles.
    discovery = list(dict.fromkeys(discovery + SAFE_LEGACY + custom_ids))
    updates = dict(ENV_SIMPLE)
    updates.update({
        "MODEL_MAP": ",".join(f"{key}={value}" for key, value in model_map.items()),
        "MODEL_EFFORT_MAP": ",".join(f"{key}={value}" for key, value in effort_map.items()),
        "MODEL_DISPLAY_MAP": ",".join(f"{key}={value}" for key, value in display_map.items()),
        "ANTHROPIC_DISCOVERY_MODELS": ",".join(discovery),
    })
    pending = []
    for key, val in updates.items():
        if key in found:
            lines[found[key][0]] = f"{key}={val}"
        else:
            pending.append(f"{key}={val}")
    if pending:
        lines.extend(["", "# Plus GPT/Codex model presets (installed locally)"] + pending)
    return "\n".join(lines) + "\n"


def write_atomic(dest: pathlib.Path, data: bytes, mode: int = 0o644):
    fd, filename = tempfile.mkstemp(prefix=".plus-presets-", dir=dest.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.chmod(filename, mode)
        os.replace(filename, dest)
    finally:
        if os.path.exists(filename):
            os.unlink(filename)


def run_cmd(cmd: list[str], cwd: pathlib.Path):
    res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, timeout=90, errors="replace")
    print(f"$ {' '.join(cmd)}  => {'PASS' if res.returncode == 0 else 'FAIL'}")
    if res.returncode:
        print("\n".join(res.stdout.splitlines()[-45:]))
        raise RuntimeError(f"Failed command: {' '.join(cmd)}")
    summary = [line for line in res.stdout.splitlines() if re.search(r"(?:# pass|# fail|tests?|passing|failing)", line, re.I)]
    if summary:
        print("  " + " / ".join(summary[-4:])[:500])


def stage(root: pathlib.Path) -> tuple[dict[str, bytes], dict[str, bytes]]:
    originals = {}
    for name in CODE_PATHS + [".env"]:
        target = root / name
        if not target.is_file():
            raise RuntimeError(f"Missing required file: {target}")
        originals[name] = target.read_bytes()
    if not (root / "package.json").is_file() or not (root / "src/auth-cli.js").is_file():
        raise RuntimeError("Not a recognized claude-codex-proxy checkout")
    code = patch_code({key: originals[key].decode("utf-8") for key in CODE_PATHS})
    modifications = {key: val.encode("utf-8") for key, val in code.items()}
    modifications[".env"] = patch_env(originals[".env"].decode("utf-8")).encode("utf-8")
    test_path = root / TEST_PATH
    if test_path.exists():
        originals[TEST_PATH] = test_path.read_bytes()
        if originals[TEST_PATH] != TEST_CONTENT.encode("utf-8"):
            raise RuntimeError(f"Found existing test at {TEST_PATH} with different contents; will not overwrite")
    modifications[TEST_PATH] = TEST_CONTENT.encode("utf-8")
    return originals, modifications


def create_backup(root: pathlib.Path, originals: dict[str, bytes], modifications: dict[str, bytes]) -> pathlib.Path:
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    base = pathlib.Path.home() / ".claude-codex-proxy-preset-backups" / stamp
    base.mkdir(parents=True, mode=0o700)
    backup_meta = {"created": stamp, "project": str(root), "files": {}}
    for key in modifications:
        orig = originals.get(key)
        backup_meta["files"][key] = {"existed": orig is not None}
        if orig is not None:
            backup_path = base / key
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            write_atomic(backup_path, orig, 0o600)
    write_atomic(base / "manifest.json", json.dumps(backup_meta, indent=2).encode(), 0o600)
    return base


def rollback(root: pathlib.Path, backup: pathlib.Path):
    manifest = json.loads((backup / "manifest.json").read_text())
    if manifest.get("project") != str(root):
        raise RuntimeError("Backup was created for another project directory")
    for rel, desc in manifest["files"].items():
        dest = root / rel
        if desc["existed"]:
            prev = backup / rel
            if not prev.is_file():
                raise RuntimeError(f"Incomplete backup: {prev}")
            write_atomic(dest, prev.read_bytes(), 0o600 if rel == ".env" else 0o644)
        elif dest.exists():
            dest.unlink()
    print("Restored original files. Running daemon was not changed.")


def probe_upstream():
    # Does not depend on altered config; direct gpt-* IDs are accepted by the original proxy.
    # Makes two small real requests, consuming a small amount of Codex quota.
    for model in ("gpt-6-luna", "gpt-6-sol"):
        payload = json.dumps({
            "model": model,
            "max_tokens": 32,
            "messages": [{"role": "user", "content": "Reply OK"}],
        }).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:8787/v1/messages",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json", "x-api-key": "local"},
        )
        try:
            with urllib.request.urlopen(req, timeout=100) as response:
                body = json.loads(response.read())
                if response.status != 200 or body.get("type") != "message":
                    raise RuntimeError(f"Upstream returned an unexpected response for {model}")
                print(f"{model}: PASS HTTP {response.status}")
        except urllib.error.HTTPError as error:
            message = error.read().decode("utf-8", "replace")[:1000]
            raise RuntimeError(f"{model}: HTTP {error.code} {message}") from error
    print("Both Luna and Sol are reachable via the existing Codex subscription proxy.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Check patch compatibility without writing files")
    group.add_argument("--apply", action="store_true", help="Back up, patch, test; do NOT restart the daemon")
    group.add_argument("--probe", action="store_true", help="Test Luna and Sol via live local Codex proxy, uses small quota")
    group.add_argument("--rollback", metavar="BACKUP_DIR", help="Restore from the given backup directory")
    ap.add_argument("--project", default=str(pathlib.Path.home() / "claude-codex-proxy"))
    args = ap.parse_args()
    root = pathlib.Path(args.project).expanduser().resolve()
    try:
        if args.probe:
            probe_upstream()
            return 0
        if args.rollback:
            backup = pathlib.Path(args.rollback).expanduser().resolve()
            private_backups = pathlib.Path.home() / ".claude-codex-proxy-preset-backups"
            if not backup.is_relative_to(private_backups):
                raise RuntimeError(f"Rollback directory must be under {private_backups}")
            rollback(root, backup)
            return 0
        originals, modifications = stage(root)
        changed = [name for name, new in modifications.items() if originals.get(name) != new]
        print(f"Project: {root}")
        print(f"Changes: {', '.join(changed) if changed else 'none'}")
        print("Eight profiles: " + ", ".join(x[0] for x in PRESETS))
        if args.check:
            print("CHECK PASS. No local files modified; daemon and CC Switch left untouched.")
            return 0
        backup = create_backup(root, originals, modifications)
        print(f"Backup: {backup}")
        try:
            for name in changed:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                prev_mode = (path.stat().st_mode & 0o777) if path.exists() else 0o644
                write_atomic(path, modifications[name], 0o600 if name == ".env" else prev_mode)
            for name in CODE_PATHS + [TEST_PATH]:
                run_cmd(["node", "--check", name], root)
            run_cmd(["npm", "test"], root)
        except Exception:
            print("Validation failed. Rolling back all modified files ...")
            rollback(root, backup)
            raise
        print("INSTALL PASS. Files updated. Running LaunchAgent has NOT been restarted.")
        print("Wait for Claude tasks to finish before launchctl kickstart -k ...")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
