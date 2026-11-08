"""Run the Arete arm and permit scale-to-zero without another rolling update."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

from run import write


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, choices=[1, 2, 4, 8], required=True)
    args = parser.parse_args()
    state = Path('work/arete-verda/runtime-original.json')
    if not state.exists():
        parser.error('Original runtime settings must be saved first')
    child = None
    status = {'started_at': datetime.now(timezone.utc).isoformat(), 'workers': args.workers,
              'state': 'generating'}
    path = Path('work/arete-verda/experiment-status.json')

    def interrupted(signum, frame):
        raise SystemExit(128 + signum)

    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    write(path, status)
    try:
        env = {k: v for k, v in os.environ.items() if k not in ('VERDA_CLIENT_ID', 'VERDA_CLIENT_SECRET')}
        child = subprocess.Popen([sys.executable, '-u', 'scripts/generate_parallel.py',
            '--run', 'eval/arete-01', '--model', 'arete-27b', '--workers', str(args.workers)], env=env)
        subprocess.run([sys.executable, 'scripts/verda_runtime.py', 'allow-idle'], check=True, timeout=120)
        code = child.wait(timeout=6 * 60 * 60)
        status.update(state='generation_finished' if code == 0 else 'generation_failed', exit_code=code)
    finally:
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=30)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
        restored = subprocess.run([sys.executable, 'scripts/verda_runtime.py', 'allow-idle'], timeout=120)
        status.update(scale_to_zero_enabled=restored.returncode == 0,
                      server_concurrency=8,
                      ended_at=datetime.now(timezone.utc).isoformat())
        if status['state'] == 'generating':
            status['state'] = 'interrupted'
        write(path, status)


if __name__ == '__main__':
    main()
