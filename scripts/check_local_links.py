#!/usr/bin/env python3
"""Check relative Markdown file links; anchor headings are not parsed."""
from __future__ import annotations
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
pattern = re.compile(r'(?<!!)\[[^\]]+\]\(([^)]+)\)')
errors = []
for file in ROOT.rglob('*.md'):
    for i, line in enumerate(file.read_text(encoding='utf-8').splitlines(), 1):
        for match in pattern.finditer(line):
            ref = match.group(1).strip().split(' ', 1)[0]
            if not ref or ref.startswith(('#', 'http://', 'https://', 'mailto:')):
                continue
            local = unquote(ref.split('#')[0].split('?')[0])
            if local and not (file.parent/local).exists():
                errors.append(f'{file.relative_to(ROOT)}:{i}: missing {local}')
if errors:
    print('\n'.join(errors))
    sys.exit(1)
print('Markdown relative links: PASS')
