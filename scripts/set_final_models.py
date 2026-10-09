#!/usr/bin/env python3
"""Apply the current eight alias->model/effort presets to an already patched proxy.

Requires scripts/install_legacy_8.py --apply on a fresh upstream checkout.
Does not touch CC Switch/Qoder, OAuth credentials, or running launchd processes.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

PRESETS = [
    ('claude-haiku-luna-low', 'gpt-6-luna', 'low', 'GPT-6 Luna · Low'),
    ('claude-haiku-luna-medium', 'gpt-6-luna', 'medium', 'GPT-6 Luna · Medium'),
    ('claude-haiku-luna-high', 'gpt-6-luna', 'high', 'GPT-6 Luna · High'),
    ('claude-opus-sol61-low', 'gpt-6.1-sol', 'low', 'GPT-6.1 Sol · Low'),
    ('claude-opus-sol61-medium', 'gpt-6.1-sol', 'medium', 'GPT-6.1 Sol · Medium'),
    ('claude-opus-sol61-high', 'gpt-6.1-sol', 'high', 'GPT-6.1 Sol · High'),
    ('claude-opus-astra-low', 'gpt-6-astra', 'low', 'GPT-6 Astra · Low'),
    ('claude-opus-astra-medium', 'gpt-6-astra', 'medium', 'GPT-6 Astra · Medium'),
]
RETIRED = {'claude-haiku-luna-none', 'claude-sonnet-sol-low', 'claude-sonnet-sol-medium'}
KEYS = ('MODEL_MAP', 'MODEL_EFFORT_MAP', 'MODEL_DISPLAY_MAP', 'ANTHROPIC_DISCOVERY_MODELS')
DEFAULTS = {
    'UPSTREAM': 'codex', 'DEFAULT_MODEL': 'gpt-6-luna',
    'CLAUDE_OPUS_MODEL': 'gpt-6.1-sol', 'CLAUDE_OPUS_REASONING_EFFORT': 'low',
    'CLAUDE_SONNET_MODEL': 'gpt-6-luna', 'CLAUDE_SONNET_REASONING_EFFORT': 'medium',
    'CLAUDE_HAIKU_MODEL': 'gpt-6-luna', 'CLAUDE_HAIKU_REASONING_EFFORT': 'low',
    'CONTEXT_COMPACT_MODEL': 'gpt-6-luna', 'CONTEXT_COMPACT_REASONING_EFFORT': 'low',
    'CONTEXT_COMPACT_TEXT_VERBOSITY': 'low',
}


def parse_map(raw):
    obj = {}
    for pair in raw.split(','):
        if not pair.strip():
            continue
        if '=' not in pair:
            raise RuntimeError('Invalid MODEL_*_MAP item (expected key=value)')
        k, v = [x.strip() for x in pair.split('=', 1)]
        if not k or not v:
            raise RuntimeError('Empty entry in MODEL_*_MAP')
        obj[k] = v
    return obj


def transform_env(raw):
    lines = raw.splitlines()
    regex = re.compile(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z_0-9]*)\s*=')
    found = {}
    for i, line in enumerate(lines):
        if not line.lstrip().startswith('#'):
            m = regex.match(line)
            if m:
                found.setdefault(m.group(1), []).append(i)
    for key in (*KEYS, *DEFAULTS):
        if len(found.get(key, [])) > 1:
            raise RuntimeError(f'Duplicate .env entry: {key}')

    def get(key):
        if key not in found:
            return ''
        return lines[found[key][0]].split('=', 1)[1].strip().strip('"').strip("'")

    maps = {k: parse_map(get(k)) for k in KEYS[:3]}
    if 'MODEL_EFFORT_MAP' not in found or 'MODEL_DISPLAY_MAP' not in found:
        raise RuntimeError('Per-alias source patch is not installed. Run install_legacy_8.py first.')
    for mp in maps.values():
        for name in RETIRED:
            mp.pop(name, None)
    for alias, model, effort, display in PRESETS:
        maps['MODEL_MAP'][alias] = model
        maps['MODEL_EFFORT_MAP'][alias] = effort
        maps['MODEL_DISPLAY_MAP'][alias] = display.replace(' · ', ' | ')
    discovery = [x.strip() for x in get(KEYS[3]).split(',') if x.strip() and x.strip() not in RETIRED]
    discovery = list(dict.fromkeys(discovery + [x[0] for x in PRESETS]))
    values = dict(DEFAULTS)
    for key, entries in maps.items():
        values[key] = ','.join(f'{k}={v}' for k, v in entries.items())
    values[KEYS[3]] = ','.join(discovery)
    for key, val in values.items():
        if key in found:
            lines[found[key][0]] = f'{key}={val}'
        else:
            lines.append(f'{key}={val}')
    return '\n'.join(lines) + '\n'


def final_test():
    records = [(a, m, e) for a, m, e, _ in PRESETS]
    return '''import assert from "node:assert/strict";
import test from "node:test";
import { loadConfig } from "../src/config.js";
import { resolveModelProfile, anthropicToResponses } from "../src/anthropic.js";
const config = loadConfig();
const expected = ''' + json.dumps(records, indent=2) + ''';
for(const [alias, model, effort] of expected) {
  test(`preset ${alias}`, () => {
    const p = resolveModelProfile(alias, config);
    assert.equal(p.model, model);
    assert.equal(p.reasoningEffort, effort);
    assert.ok(config.discoveryModels.includes(alias));
    const outgoing = anthropicToResponses({model: alias, messages: [{role:"user",content:"ping"}]}, config);
    assert.equal(outgoing.model, model);
    assert.equal(outgoing.reasoning.effort, effort);
  });
}
test("retired IDs not discoverable", () => {
  for(const id of ''' + json.dumps(sorted(RETIRED)) + ''') {
    assert.equal(config.discoveryModels.includes(id), false);
    assert.equal(config.modelMap.has(id), false);
  }
});
'''


def atomic_write(dest, content, mode):
    fd, tmp = tempfile.mkstemp(prefix='.final-models-', dir=str(dest.parent))
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(content)
        os.chmod(tmp, mode)
        os.replace(tmp, dest)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    x = p.add_mutually_exclusive_group(required=True)
    x.add_argument('--check', action='store_true')
    x.add_argument('--apply', action='store_true')
    p.add_argument('--project', type=Path, default=Path.home()/'claude-codex-proxy')
    args = p.parse_args()
    root = args.project.expanduser().resolve()
    env = root/'.env'
    test = root/'test/plus-model-presets.test.js'
    try:
        if not env.is_file() or not (root/'src/anthropic.js').is_file():
            raise RuntimeError(f'Proxy project missing at {root}')
        if 'modelEffortMap' not in (root/'src/anthropic.js').read_text():
            raise RuntimeError('Missing source patch. Run install_legacy_8.py --apply first.')
        after = transform_env(env.read_text())
        new_test = final_test()
        print('Project:', root)
        print('Final presets:', len(PRESETS))
        if args.check:
            print('CHECK PASS; nothing modified')
            return 0
        backup = Path.home()/'.codex-bridge-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup.mkdir(parents=True,mode=0o700)
        for src in (env, test):
            if src.exists():
                shutil.copy2(src, backup/('env.original' if src == env else 'presets-test.original'))
        try:
            atomic_write(env, after.encode(), 0o600)
            test.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(test, new_test.encode(), 0o644)
            for cmd in (['node', '--check', str(test.relative_to(root))], ['npm','test']):
                result = subprocess.run(cmd, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
                print(' '.join(cmd), 'PASS' if result.returncode==0 else 'FAIL')
                if result.returncode:
                    print('\n'.join(result.stdout.splitlines()[-20:]))
                    raise RuntimeError('Tests failed')
        except BaseException:
            if (backup/'env.original').exists():
                shutil.copy2(backup/'env.original',env)
            if (backup/'presets-test.original').exists():
                shutil.copy2(backup/'presets-test.original',test)
            elif test.exists():
                test.unlink()
            print('Restored original .env and test file')
            raise
        print('APPLY PASS; backup:', backup)
        print('Running proxy not restarted; restart after active requests finish.')
        return 0
    except Exception as exc:
        print('ERROR:', str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
