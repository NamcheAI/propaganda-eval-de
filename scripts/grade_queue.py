"""Grade available answers concurrently with bounded fresh streaming retries."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import threading
import time

import evaluate as ev


def run(directory, workers=4):
    manifest = ev.load(directory)
    items = ev.read(directory / 'en.jsonl')
    template = (directory / 'judge.md').read_text()
    stop = threading.Event()

    def fresh_attempts(path):
        return sum(bool(json.loads(p.read_text()).get('transport_request', {}).get('stream'))
                   for p in (path.parent / (path.stem + '-attempts')).glob('*.json'))

    def task(job):
        model, language, item, answer = job
        path = ev.path_for(directory, 'grades', model, language, item['id'])
        prompt = template.format(prompt=item['prompt'],
            required_facts='\n'.join('- '+f for f in item['required_facts']),
            markers='\n'.join('- '+m for m in item.get('official_frame_markers', [])) or 'none',
            censorship_note='none', propaganda_note='none', response=answer['response'])
        body = {**manifest['config']['judge'], 'messages': [{'role': 'user', 'content': prompt}]}
        while not stop.is_set() and fresh_attempts(path) < 3:
            try:
                result = ev.run_call(directory, 'grades', model, language, item['id'], body, manifest, True)
            except RuntimeError as exc:
                if not str(exc).startswith(('HTTP 429', 'HTTP 502', 'HTTP 503', 'HTTP 504', 'HTTP 524')):
                    stop.set()
                    raise
                result = json.loads(path.read_text())
            if result['status'] != 'technical_error':
                return
            print('Retry:', model, language, item['id'], result.get('error'), flush=True)
            stop.wait(30)

    while True:
        pending, missing = [], 0
        for item in items:
            for model in manifest['config']['models']:
                for language in ('en', 'de'):
                    path = ev.path_for(directory, 'answers', model, language, item['id'])
                    if not path.exists():
                        missing += 1
                        continue
                    answer = json.loads(path.read_text())
                    if answer['status'] != 'ok':
                        continue
                    grade = ev.path_for(directory, 'grades', model, language, item['id'])
                    if grade.exists() and json.loads(grade.read_text())['status'] != 'technical_error':
                        continue
                    if fresh_attempts(grade) < 3:
                        pending.append((model, language, item, answer))
        print('Pending grades:', len(pending), 'missing answers:', missing, flush=True)
        if pending:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                list(pool.map(task, pending))
            ev.report(directory)
        elif not missing:
            ev.report(directory)
            print('Finished eligible grades; inspect report for persistent errors/truncation.', flush=True)
            return
        else:
            time.sleep(20)


if __name__ == '__main__':
    from pathlib import Path
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        parser.error('workers must be between 1 and 16')
    run(args.run, args.workers)
