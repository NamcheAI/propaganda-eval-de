"""Ask the same judge to correct formal errors with a published validation message."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import time

import evaluate as ev

PROMPT = ev.ROOT / 'prompts/judge-validation-repair.md'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--attempts', type=int, default=2)
    p.add_argument('--targets', type=Path, help='Optional explicit model/language/id selection')
    p.add_argument('--endpoint', default='https://inference.namche.net/v1/chat/completions')
    args = p.parse_args()
    if not 1 <= args.workers <= 8 or not 1 <= args.attempts <= 3:
        p.error('Use 1-8 workers and 1-3 attempts')
    lock = (args.run / '.judge-validation-repair.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    manifest = ev.load(args.run)
    selected = None if args.targets is None else {
        (r['model'], r['language'], r['id']) for r in json.loads(args.targets.read_text())}
    request = ev.configured_request
    ev.configured_request = lambda endpoint, body: request(args.endpoint, body)
    template = PROMPT.read_text()
    jobs = []
    for model in manifest['config']['models']:
        for lang in ('en', 'de'):
            for sid in manifest['item_ids']:
                if selected is not None and (model, lang, sid) not in selected: continue
                source = ev.path_for(args.run, 'grades', model, lang, sid)
                if not source.exists(): continue
                raw = json.loads(source.read_text())
                if raw['status'] != 'technical_error' or not raw.get('response'): continue
                if ev.selected_grade_path(args.run, model, lang, sid) != source: continue
                body = {**manifest['config']['judge'], 'messages': [
                    *raw['request']['messages'], {'role': 'assistant', 'content': raw['response']},
                    {'role': 'user', 'content': template.format(validation_error=raw['error'])}]}
                provenance = {'procedure': 'judge-validation-repair-v1', 'source_grade_sha256': ev.digest(source),
                              'prompt_sha256': ev.digest(PROMPT), 'transport_endpoint': args.endpoint}
                jobs.append((model, lang, sid, body, provenance))
    audit = {'started_at': datetime.now(timezone.utc).isoformat(), 'procedure': 'judge-validation-repair-v1',
             'prompt_sha256': ev.digest(PROMPT), 'attempt_cap': args.attempts,
             'targets': [{'model': m, 'language': l, 'id': sid} for m,l,sid,b,pr in jobs]}
    audit_path = args.run / ('validation-repair-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S') + '.json')
    ev.write(audit_path, audit)
    print('Validation repair targets:', len(jobs), flush=True)
    def call(job):
        model, lang, sid, body, provenance = job
        path = ev.path_for(args.run, 'grade-repairs', model, lang, sid)
        attempt_dir = path.parent / (sid + '-attempts')
        while len(list(attempt_dir.glob('*.json'))) < args.attempts:
            try:
                result = ev.run_call(args.run, 'grade-repairs', model, lang, sid, body, manifest, True, provenance)
            except RuntimeError:
                result = json.loads(path.read_text())
            if result['status'] == 'ok': break
            time.sleep(10)
        result = json.loads(path.read_text())
        return {'model': model, 'language': lang, 'id': sid, 'status': result['status'], 'error': result.get('error')}
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(call, job) for job in jobs]):
            row = future.result(); results.append(row); print(json.dumps(row), flush=True)
    audit.update(completed_at=datetime.now(timezone.utc).isoformat(), results=results)
    ev.write(audit_path, audit)
    ev.report(args.run)
    lock.close()


if __name__ == '__main__': main()
