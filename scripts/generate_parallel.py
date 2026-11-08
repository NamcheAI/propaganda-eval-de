"""Resume an immutable evaluation with bounded parallel answer generation."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import time
import threading

import evaluate as ev


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--workers', type=int, choices=range(1, 17), required=True)
    args = parser.parse_args()
    manifest = ev.load(args.run)
    if args.model not in manifest['config']['models']:
        parser.error('Model absent from immutable configuration')
    en, de = (ev.read(args.run / (language + '.jsonl')) for language in ('en', 'de'))
    jobs = []
    stop = threading.Event()
    for index, pair in enumerate(zip(en, de)):
        entries = list(zip(('en', 'de'), pair))
        jobs.extend(entries[::1 if index % 2 == 0 else -1])

    def call(job):
        if stop.is_set():
            return
        language, item = job
        path = ev.path_for(args.run, 'answers', args.model, language, item['id'])
        if path.exists() and json.loads(path.read_text())['status'] != 'technical_error':
            return
        body = {'model': args.model, **manifest['config']['generation'],
                'messages': [{'role': 'user', 'content': item['prompt']}]}
        attempts = path.parent / (item['id'] + '-attempts')
        while len(list(attempts.glob('*.json'))) < 3:
            if stop.is_set():
                return
            try:
                result = ev.run_call(args.run, 'answers', args.model, language, item['id'],
                                     body, manifest, True)
            except RuntimeError as error:
                if not str(error).startswith(('HTTP 429', 'HTTP 502', 'HTTP 503', 'HTTP 504', 'HTTP 524')):
                    stop.set()
                    raise
                result = json.loads(path.read_text())
            print(language, item['id'], result['status'], flush=True)
            if result['status'] != 'technical_error':
                return
            time.sleep(20)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(call, jobs))
    ev.report(args.run)


if __name__ == '__main__':
    main()
