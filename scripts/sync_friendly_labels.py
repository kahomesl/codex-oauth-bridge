#!/usr/bin/env python3
"""Persist friendly model labels in CC Switch direct provider and Claude 3P profile.

macOS only. Does not restart Claude, CC Switch, or the Codex proxy.
Use after quitting CC Switch and Claude Desktop (Command+Q).

python3 scripts/sync_friendly_labels.py --check
python3 scripts/sync_friendly_labels.py --apply
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile

LABELS = {
    "claude-haiku-luna-low": "GPT-6 Luna · Low",
    "claude-haiku-luna-medium": "GPT-6 Luna · Medium",
    "claude-haiku-luna-high": "GPT-6 Luna · High",
    "claude-opus-sol61-low": "GPT-6.1 Sol · Low",
    "claude-opus-sol61-medium": "GPT-6.1 Sol · Medium",
    "claude-opus-sol61-high": "GPT-6.1 Sol · High",
    "claude-opus-astra-low": "GPT-6 Astra · Low",
    "claude-opus-astra-medium": "GPT-6 Astra · Medium",
}
ENDPOINT = "http://127.0.0.1:8787"
CC_SWITCH_PROFILE_ID = "00000000-0000-4000-8000-000000157210"


def read_json_file(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def selected_provider(db: Path):
    if not db.is_file():
        raise RuntimeError(f"CC Switch database not found: {db}")
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        candidates = []
        query = "SELECT id, name, settings_config, meta FROM providers WHERE app_type = ?"
        for provider_id, name, settings_raw, meta_raw in con.execute(query, ("claude-desktop",)):
            try:
                settings = json.loads(settings_raw)
                meta = json.loads(meta_raw)
                endpoint = settings.get("env", {}).get("ANTHROPIC_BASE_URL", "").rstrip("/")
                routes = meta.get("claudeDesktopModelRoutes", {})
            except (ValueError, AttributeError, TypeError):
                continue
            if endpoint != ENDPOINT or not isinstance(routes, dict):
                continue
            if not set(LABELS).issubset(routes):
                continue
            if meta.get("claudeDesktopMode") != "direct":
                continue
            candidates.append((provider_id, name, meta, routes))
        if len(candidates) != 1:
            raise RuntimeError(
                f"Expected exactly one 8787 direct provider with all 8 presets; found {len(candidates)}. "
                "No changes made."
            )
        return candidates[0]
    finally:
        con.close()


def chosen_profile(config_library: Path):
    if not config_library.is_dir():
        raise RuntimeError(f"Claude 3P configLibrary not found: {config_library}")
    meta_path = config_library / "_meta.json"
    applied = None
    if meta_path.exists():
        try:
            applied = read_json_file(meta_path).get("appliedId")
        except (OSError, ValueError, TypeError):
            pass
    candidates = []
    for p in config_library.glob("*.json"):
        if p.name == "_meta.json":
            continue
        try:
            profile = read_json_file(p)
            if not isinstance(profile, dict):
                continue
            if profile.get("inferenceGatewayBaseUrl", "").rstrip("/") != ENDPOINT:
                continue
            models = profile.get("inferenceModels", [])
            if not isinstance(models, list):
                continue
            names = {v if isinstance(v, str) else v.get("name") for v in models if isinstance(v, (dict, str))}
            if set(LABELS).issubset(names):
                candidates.append((p, profile))
        except (OSError, ValueError, TypeError):
            continue
    preferred = [x for x in candidates if x[0].stem == applied]
    if len(preferred) == 1:
        return preferred[0]
    cc = [x for x in candidates if x[0].stem == CC_SWITCH_PROFILE_ID]
    if len(cc) == 1:
        return cc[0]
    if len(candidates) == 1:
        return candidates[0]
    raise RuntimeError(
        f"Expected one active Claude 8787 profile with 8 models, found {len(candidates)}. "
        "No changes made."
    )


def label_profile(profile: dict):
    result = dict(profile)
    output = []
    changed = 0
    for item in profile["inferenceModels"]:
        name = item if isinstance(item, str) else item.get("name")
        if name in LABELS:
            obj = {"name": name} if isinstance(item, str) else dict(item)
            if obj.get("labelOverride") != LABELS[name]:
                changed += 1
            obj["labelOverride"] = LABELS[name]
            output.append(obj)
        else:
            output.append(item)
    result["inferenceModels"] = output
    return result, changed


def label_provider(meta: dict):
    out = json.loads(json.dumps(meta, ensure_ascii=False))
    routes = out["claudeDesktopModelRoutes"]
    changed = 0
    for key, label in LABELS.items():
        if routes[key].get("labelOverride") != label:
            changed += 1
        routes[key]["labelOverride"] = label
    return out, changed


def atomic_json_write(dest: Path, doc: dict):
    contents = (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    file_mode = dest.stat().st_mode & 0o777
    fd, tmp = tempfile.mkstemp(prefix=".claude-labels-", dir=dest.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(contents)
        os.chmod(tmp, file_mode)
        os.replace(tmp, dest)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def backup_files(db: Path, profile_path: Path, backup_dir: Path):
    backup_dir.mkdir(parents=True, mode=0o700, exist_ok=False)
    os.chmod(backup_dir, 0o700)
    db_copy = backup_dir / "cc-switch.db.sqlite-backup"
    with sqlite3.connect(str(db)) as src, sqlite3.connect(str(db_copy)) as dst:
        src.backup(dst)
    os.chmod(db_copy, 0o600)
    shutil.copy2(profile_path, backup_dir / (profile_path.name + ".backup"))
    os.chmod(backup_dir / (profile_path.name + ".backup"), 0o600)
    return backup_dir


def apply(db: Path, provider_id: str, updated_meta: dict, profile_path: Path, updated_profile: dict):
    # Keep SQLite provider metadata and the active Claude profile in sync.
    con = sqlite3.connect(str(db), timeout=10)
    try:
        con.execute("BEGIN IMMEDIATE")
        existing = con.execute(
            "SELECT meta FROM providers WHERE app_type = ? AND id = ?",
            ("claude-desktop", provider_id),
        ).fetchone()
        if existing is None:
            raise RuntimeError("The CC Switch provider changed during verification")
        # Keep updates narrowly scoped to the intended eight metadata labels.
        latest = json.loads(existing[0])
        for key in LABELS:
            if key not in latest.get("claudeDesktopModelRoutes", {}):
                raise RuntimeError(f"Missing model in stored CC Switch provider: {key}")
            latest["claudeDesktopModelRoutes"][key]["labelOverride"] = LABELS[key]
        con.execute(
            "UPDATE providers SET meta = ? WHERE app_type = ? AND id = ?",
            (json.dumps(latest, ensure_ascii=False, separators=(",", ":")), "claude-desktop", provider_id),
        )
        atomic_json_write(profile_path, updated_profile)
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def main():
    parser = argparse.ArgumentParser(description="Friendly Claude Desktop GPT preset names (CC Switch)")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="Read-only compatibility check")
    mode.add_argument("--apply", action="store_true", help="Back up and set friendly labels")
    parser.add_argument("--home", type=Path, default=Path.home(), help=argparse.SUPPRESS)
    args = parser.parse_args()
    home = args.home.expanduser()
    db = home / ".cc-switch" / "cc-switch.db"
    config_library = home / "Library" / "Application Support" / "Claude-3p" / "configLibrary"
    try:
        provider_id, provider_name, meta, routes = selected_provider(db)
        profile_path, profile = chosen_profile(config_library)
        updated_meta, stored_count = label_provider(meta)
        updated_profile, profile_count = label_profile(profile)
        print("Found CC Switch provider:", provider_name)
        print("Claude profile:", profile_path)
        print("Eight preset IDs: verified")
        print(f"Labels requiring update: provider {stored_count}, profile {profile_count}")
        if args.check:
            print("CHECK PASS. Nothing changed. Quit CC Switch and Claude Desktop before --apply.")
            return 0
        backup_root = home / ".claude-model-label-backups"
        backup_root.mkdir(mode=0o700, exist_ok=True)
        os.chmod(backup_root, 0o700)
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup_dir = backup_root / stamp
        backup_files(db, profile_path, backup_dir)
        try:
            apply(db, provider_id, updated_meta, profile_path, updated_profile)
        except Exception:
            # Do not blindly overwrite the CC Switch DB if app state changed; backup is retained.
            # Active profile restoration is safe as long as this script was sole writer.
            shutil.copy2(backup_dir / (profile_path.name + ".backup"), profile_path)
            raise
        # Validate labels on disk without printing the stored API key or provider settings.
        _, _, after_meta, _ = selected_provider(db)
        after_profile = read_json_file(profile_path)
        for key, label in LABELS.items():
            assert after_meta["claudeDesktopModelRoutes"][key]["labelOverride"] == label
            assert next(m for m in after_profile["inferenceModels"] if isinstance(m, dict) and m.get("name") == key)["labelOverride"] == label
        print("APPLY PASS. Both CC Switch provider and Claude profile labels updated.")
        print("Backup:", backup_dir)
        print("Restart Claude Desktop; no restart needed for localhost:8787.")
        return 0
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
