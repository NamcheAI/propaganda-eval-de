"""Bounded temporary Arete concurrency settings; credentials only from environment."""
import argparse
import copy
import json
import os
from pathlib import Path
import urllib.request

BASE = 'https://api.verda.com/v1'
DEPLOY = '/container-deployments/arete-27b'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['inspect', 'set', 'restore', 'allow-idle'])
    parser.add_argument('--concurrency', type=int, choices=[2, 4, 8, 16], default=2)
    parser.add_argument('--state', type=Path, default=Path('work/arete-verda/runtime-original.json'))
    args = parser.parse_args()
    request = urllib.request.Request(BASE + '/oauth2/token', data=json.dumps({
        'grant_type': 'client_credentials', 'client_id': os.environ['VERDA_CLIENT_ID'],
        'client_secret': os.environ['VERDA_CLIENT_SECRET']}).encode(),
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=30) as response:
        token = json.load(response)['access_token']

    def api(path, body=None):
        request = urllib.request.Request(BASE + DEPLOY + path,
            data=None if body is None else json.dumps(body).encode(),
            headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'},
            method='GET' if body is None else 'PATCH')
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read()
            return json.loads(raw) if raw else None

    deployment, scaling = api(''), api('/scaling')
    assert deployment['compute'] == {'name': 'RTX PRO 6000', 'size': 1}
    assert scaling['max_replica_count'] == 1
    container, = deployment['containers']
    command = container['entrypoint_overrides']['cmd']
    assert command[0] == 'NousResearch/Arete-27B'
    assert command[command.index('--revision') + 1] == '108f0afbdcfaa1ceeda4a635004304dfff6d4da2'
    state = {'container': {k: container[k] for k in ('name', 'entrypoint_overrides')},
             'scaling': {k: scaling[k] for k in ('min_replica_count', 'concurrent_requests_per_replica')}}
    if args.action == 'inspect':
        print(json.dumps({'configuration': state, 'replicas': api('/replicas')}, indent=2))
        return
    if args.action == 'set':
        if not args.state.exists():
            args.state.parent.mkdir(parents=True, exist_ok=True)
            args.state.write_text(json.dumps(state, indent=2) + '\n')
        updated = copy.deepcopy(state['container'])
        command = updated['entrypoint_overrides']['cmd']
        command[command.index('--max-num-seqs') + 1] = str(args.concurrency)
        if updated != state['container']:
            api('', {'containers': [updated]})
        api('/scaling', {'min_replica_count': 1, 'concurrent_requests_per_replica': args.concurrency})
    elif args.action == 'allow-idle':
        api('/scaling', {'min_replica_count': 0})
    else:
        original = json.loads(args.state.read_text())
        if state['container'] != original['container']:
            api('', {'containers': [original['container']]})
        api('/scaling', original['scaling'])
    print(json.dumps({'action': args.action,
                      'requested_concurrency': args.concurrency if args.action == 'set' else None}))


if __name__ == '__main__':
    main()
