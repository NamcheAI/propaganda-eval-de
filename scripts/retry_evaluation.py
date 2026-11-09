"""Make a bounded repair pass over failed/missing requests without replacing successes."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import time
import evaluate as ev


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--stage', choices=['answers', 'grades'], required=True)
    p.add_argument('--workers', type=int, default=8)
    p.add_argument('--additional-attempts', type=int, default=2)
    p.add_argument('--transport-endpoint')
    p.add_argument('--only-missing', action='store_true')
    p.add_argument('--include-truncated', action='store_true', help='Also retry incomplete answer generations at the same token cap')
    args = p.parse_args()
    if args.include_truncated and args.stage != 'answers':
        p.error('--include-truncated applies only to answers')
    retry_statuses = ('technical_error', 'truncated') if args.include_truncated else ('technical_error',)
    if not 1 <= args.workers <= 8 or not 1 <= args.additional_attempts <= 3:
        p.error('Use 1-8 workers and 1-3 additional attempts')
    lock = (args.run / ('.repair-' + args.stage + '.lock')).open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    manifest = ev.load(args.run)
    items = ev.read(args.run / 'en.jsonl')
    german = {x['id']: x for x in ev.read(args.run / 'de.jsonl')}
    template = (args.run / 'judge.md').read_text()
    if args.transport_endpoint:
        original = ev.configured_request
        ev.configured_request = lambda endpoint, body: original(args.transport_endpoint, body)
    tasks = []
    for item in items:
        for model in manifest['config']['models']:
            for lang in ('en', 'de'):
                path = ev.path_for(args.run, args.stage, model, lang, item['id'])
                if args.only_missing and path.exists(): continue
                existing = json.loads(path.read_text()) if path.exists() else None
                if existing and existing['status'] not in retry_statuses:
                    continue
                if args.stage == 'grades':
                    answer_path = ev.path_for(args.run, 'answers', model, lang, item['id'])
                    if not answer_path.exists(): continue
                    answer = json.loads(answer_path.read_text())
                    if answer['status'] != 'ok': continue
                    prompt = template.format(prompt=item['prompt'], required_facts='\n'.join('- ' + f for f in item['required_facts']),
                        markers='\n'.join('- ' + x for x in item.get('official_frame_markers', [])) or 'none',
                        censorship_note='none', propaganda_note='none', response=answer['response'])
                    body = {**manifest['config']['judge'], 'messages': [{'role': 'user', 'content': prompt}]}
                else:
                    source = item if lang == 'en' else german[item['id']]
                    body = {'model': model, **manifest['config']['generation'], 'messages': [{'role': 'user', 'content': source['prompt']}]}
                tasks.append((model, lang, item['id'], body))
    audit = {'started_at': datetime.now(timezone.utc).isoformat(), 'run': str(args.run), 'stage': args.stage,
             'additional_attempts_per_target': args.additional_attempts,
             'retry_statuses': retry_statuses,
             'transport_endpoint': args.transport_endpoint or manifest['config']['endpoint'],
             'targets': [{'model': m, 'language': l, 'id': i} for m,l,i,b in tasks]}
    path = args.run / ('repair-' + args.stage + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '.json')
    ev.write(path, audit)
    print('Repair targets', args.stage, len(tasks), flush=True)
    def call(job):
        model, lang, sid, body = job
        result = None
        for attempt in range(args.additional_attempts):
            try:
                result = ev.run_call(args.run, args.stage, model, lang, sid, body, manifest, True,
                                     retry_statuses=retry_statuses)
            except RuntimeError:
                result = json.loads(ev.path_for(args.run, args.stage, model, lang, sid).read_text())
            if result['status'] not in retry_statuses: break
            if attempt + 1 < args.additional_attempts: time.sleep(10)
        return {'model': model, 'language': lang, 'id': sid, 'status': result['status'], 'error': result.get('error')}
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(call, j) for j in tasks]):
            r = future.result(); results.append(r); print(json.dumps(r), flush=True)
    audit.update(completed_at=datetime.now(timezone.utc).isoformat(), results=results)
    ev.write(path, audit)
    ev.report(args.run)
    lock.close()

if __name__ == '__main__': main()
