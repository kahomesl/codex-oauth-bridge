#!/usr/bin/env python3
"""Fresh-install launchd service, refuses to replace an existing 8787 listener.

For existing service labels, keep the current LaunchAgent and use its normal kickstart command.
"""
import argparse
from pathlib import Path
import os
import plistlib
import shutil
import socket
import sys

LABEL = 'com.local.codex-subscription-bridge'
PORT = 8787


def port_active():
    try:
        with socket.create_connection(('127.0.0.1', PORT), timeout=0.35):
            return True
    except OSError:
        return False


def main():
    a = argparse.ArgumentParser(description=__doc__)
    action = a.add_mutually_exclusive_group(required=True)
    action.add_argument('--check', action='store_true')
    action.add_argument('--apply', action='store_true')
    args = a.parse_args()
    repo = Path(__file__).resolve().parent.parent
    wrapper = repo/'scripts/run_proxy_macos.sh'
    source = Path.home()/'claude-codex-proxy/src/server.js'
    node = shutil.which('node')
    plist = Path.home()/f'Library/LaunchAgents/{LABEL}.plist'
    if not node or not Path(node).is_file() or not wrapper.exists() or not source.exists():
        print('ERROR: Node, bridge runner, or ~/claude-codex-proxy not found', file=sys.stderr)
        return 1
    if port_active():
        print('PORT 8787 IS ALREADY LISTENING. Existing service detected; not installing another.', file=sys.stderr)
        return 1
    if plist.exists():
        print(f'LaunchAgent already exists: {plist}; refusing to overwrite', file=sys.stderr)
        return 1
    data = {
        'Label': LABEL,
        'ProgramArguments': ['/bin/bash', str(wrapper)],
        'EnvironmentVariables': {
            'CODEX_BRIDGE_PROJECT': str(Path.home()/'claude-codex-proxy'),
            'CODEX_BRIDGE_NODE': str(Path(node).resolve()),
        },
        'WorkingDirectory': str(Path.home()/'claude-codex-proxy'),
        'RunAtLoad': True, 'KeepAlive': True, 'ThrottleInterval': 5,
        'StandardOutPath': str(Path.home()/'Library/Logs/codex-subscription-bridge.log'),
        'StandardErrorPath': str(Path.home()/'Library/Logs/codex-subscription-bridge.err.log'),
    }
    print('Prepared LaunchAgent:', plist)
    print('Node:', node)
    if args.check:
        print('CHECK PASS. No files modified.')
        return 0
    plist.parent.mkdir(parents=True,exist_ok=True)
    with plist.open('wb') as f:
        plistlib.dump(data,f)
    os.chmod(plist,0o600)
    print('Created:', plist)
    print('Start with: launchctl bootstrap "gui/$(id -u)"', repr(str(plist)))
    print('No service was started by this script.')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
