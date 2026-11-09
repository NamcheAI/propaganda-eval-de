"""Resume the hosted Qwen control with gradual concurrency and nonthinking checks."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import time
import evaluate as ev

RUN = Path('eval/qwen-01')
MODEL = 'qwen/qwen3.8-27b'


def main():
    lock = (RUN / '.generation.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    manifest = ev.load(RUN)
    request_fn = ev.configured_request

    def checked(endpoint, body):
        result = request_fn(endpoint, body)
        if body['model'] == MODEL:
            details = (result.get('usage') or {}).get('completion_tokens_details') or {}
            if details.get('reasoning_tokens', 0) != 0:
                raise ValueError('Nonthinking check failed: provider reports reasoning tokens')
        return result
    ev.configured_request = checked
    items = {lang: ev.read(RUN / (lang + '.jsonl')) for lang in ('en', 'de')}
    jobs = [(lang, items[lang][i]) for i in range(len(items['en']))
            for lang in (('en', 'de') if i % 2 == 0 else ('de', 'en'))]
    def needed(job):
        lang, item = job
        p = ev.path_for(RUN, 'answers', MODEL, lang, item['id'])
        return not p.exists() or (json.loads(p.read_text())['status'] == 'technical_error'
                                 and len(list((p.parent/(p.stem+'-attempts')).glob('*.json'))) < 3)
    jobs = [job for job in jobs if needed(job)]
    total_pending = len(jobs)
    started = datetime.now(timezone.utc).isoformat()
    done = 0
    def call(job):
        lang, item = job
        body = {'model': MODEL, **manifest['config']['generation'],
                'messages': [{'role': 'user', 'content': item['prompt']}]}
        p = ev.path_for(RUN, 'answers', MODEL, lang, item['id'])
        attempts = p.parent / (p.stem + '-attempts')
        while len(list(attempts.glob('*.json'))) < 3:
            try:
                result = ev.run_call(RUN, 'answers', MODEL, lang, item['id'], body, manifest, True)
            except RuntimeError:
                result = json.loads(p.read_text())
            if 'Nonthinking check failed' in result.get('error', ''):
                raise RuntimeError('Provider enabled reasoning; stop the run and inspect recorded error')
            if result['status'] != 'technical_error':
                return result
            time.sleep(15)
        return json.loads(p.read_text())
    for workers, count in [(1, 4), (2, 8), (4, 16), (8, len(jobs))]:
        batch, jobs = jobs[:count], jobs[count:]
        if not batch:
            continue
        failures = 0
        with ThreadPoolExecutor(max_workers=workers) as pool:
            for future in as_completed([pool.submit(call, job) for job in batch]):
                result = future.result(); done += 1
                failures += result['status'] == 'technical_error'
                print(result['language'], result['id'], result['status'], 'workers', workers, flush=True)
                ev.write(RUN / 'generation-progress.json', {'started_at': started,
                    'updated_at': datetime.now(timezone.utc).isoformat(), 'state': 'generating',
                    'workers': workers, 'completed_this_session': done, 'remaining_this_session': total_pending - done})
        if failures > max(1, len(batch) // 10):
            raise RuntimeError('Too many persistent technical failures; no further concurrency ramp')
    ev.report(RUN)
    ev.write(RUN / 'generation-progress.json', {'started_at': started,
        'updated_at': datetime.now(timezone.utc).isoformat(), 'state': 'generation_finished',
        'completed_this_session': done})

if __name__ == '__main__':
    main()
