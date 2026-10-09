#!/usr/bin/env python3
"""Conservative local public-release audit. No network, no file modifications.

This heuristic can miss secrets: manual inspection of content AND git history is mandatory.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

# Generated version-control and Python cache data are not part of GitHub source snapshots.
SKIPPED_PARTS = {'.git', '__pycache__', '.pytest_cache'}
DISALLOWED_PARTS = {
    '.auth', 'node_modules', 'configLibrary',
    '.ssh', '.gnupg', '.aws', '.config', '.DS_Store',
}
BAD_BASENAMES = {
    '.env', 'codex.json', 'cc-switch.db', 'claude_desktop_config.json',
    'settings.json', 'credentials.json', 'id_rsa', 'id_ed25519',
}
BAD_SUFFIXES = {'.pyc', '.pem', '.p12', '.pfx', '.sqlite', '.sqlite3', '.db', '.key', '.log', '.zip'}
TEXT_EXTENSIONS = {'.md', '.txt', '.py', '.sh', '.yml', '.yaml', '.json', '.toml', '.html', '.css', '.svg', '.example'}

CONTENT_PATTERNS = {
    'credential-token-like': re.compile(
        r'\b(?:sk-[A-Za-z0-9_-]{16,}|gh(?:p|o|u|s|r)_[A-Za-z0-9_]{22,}|'
        r'github_pat_[A-Za-z0-9_]{30,}|Bearer\s+[A-Za-z0-9_.-]{24,})\b', re.I
    ),
    'private-key-block': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'real-email-address': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
    'mac-user-home': re.compile(r'/Users/(?!\$|\{|<|YOUR_|your_|USERNAME|username)[A-Za-z0-9_.-]+/'),
    'likely-machine-host': re.compile(r'\b[A-Za-z0-9-]+(?:MacBook|iMac|Mac-mini)[A-Za-z0-9-]*\.local\b', re.I),
    'known-internal-git-path': re.compile(r'github\.com/[^\s)]+/(?:[\w.-]*(?:private|internal|secret)[\w.-]*)', re.I),
}


def audit(root: Path) -> list[tuple[str, str]]:
    findings = []
    if not root.is_dir():
        return [('root', 'Missing directory')]
    for path in sorted(root.rglob('*')):
        rel = path.relative_to(root)
        if any(part in SKIPPED_PARTS for part in rel.parts):
            continue
        if path.is_symlink():
            findings.append((str(rel), 'symlink - review target'))
            continue
        if any(part in DISALLOWED_PARTS for part in rel.parts):
            findings.append((str(rel), 'forbidden file/directory'))
            continue
        if path.is_dir():
            continue
        if path.name in BAD_BASENAMES or path.suffix.lower() in BAD_SUFFIXES:
            findings.append((str(rel), 'sensitive or generated file type'))
            continue
        if path.stat().st_size > 500_000:
            findings.append((str(rel), 'unexpected large file'))
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in {'LICENSE', '.gitignore'}:
            findings.append((str(rel), 'non-text file needs manual review'))
            continue
        try:
            data = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            findings.append((str(rel), 'non-UTF8 or binary content'))
            continue
        for label, pattern in CONTENT_PATTERNS.items():
            if pattern.search(data):
                findings.append((str(rel), label))
        # Make non-loopback IPs a manual-review finding, but allow private RFC1918
        # examples only after separate human confirmation; script is conservative.
        for value in set(re.findall(r'(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)', data)):
            if value == '127.0.0.1' or value == '0.0.0.0':
                continue
            findings.append((str(rel), 'IPv4 address outside loopback; review before publishing'))
            break
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict', action='store_true', help='fail if any item is flagged')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    found = audit(args.root.resolve())
    if found:
        print(f'REVIEW REQUIRED ({len(found)} findings). No file contents are printed.')
        for file, issue in found:
            print(f' - {file}: {issue}')
        return 1 if args.strict else 0
    print('HEURISTIC AUDIT PASS: no matched sensitive file/path/token patterns.')
    print('Still required: manual content review, Git author/email review, and fresh Git history.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
