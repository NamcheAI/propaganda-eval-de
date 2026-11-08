"""Repeat a fixed bilingual workload at measured client concurrency."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import urllib.request

from run import load_key, write
from evaluate import read_stream


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--concurrency', type=int, choices=[1, 2, 4, 8, 16], required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Use a new output path')
    jobs = []
    for language in ('en', 'de'):
        items = [json.loads(line) for line in Path('eval/main-01', language + '.jsonl').read_text().splitlines()]
        for index in (0, 100, 200, 300, 400, 500, 600, 700):
            jobs.append((language, items[index]))
    key = load_key()

    def call(job, max_tokens=512):
        language, item = job
        body = {'model': 'arete-27b', 'messages': [{'role': 'user', 'content': item['prompt']}],
                'temperature': 0, 'max_tokens': max_tokens, 'stream': True,
                'stream_options': {'include_usage': True},
                'chat_template_kwargs': {'enable_thinking': False},
                'cache': {'no-cache': True, 'no-store': True}}
        request = urllib.request.Request('https://inference.khumbu.namche.net/v1/chat/completions',
            data=json.dumps(body).encode(), headers={'Authorization': 'Bearer ' + key,
            'Content-Type': 'application/json', 'User-Agent': 'curl/8.7.1'})
        started = time.monotonic()
        record = {'id': item['id'], 'language': language, 'request': body}
        try:
            with urllib.request.urlopen(request, timeout=1800) as response:
                record['response'] = read_stream(response)
            record['status'] = 'ok'
        except Exception as error:
            record.update(status='error', error=type(error).__name__ + ': ' + str(error))
        record['seconds'] = time.monotonic() - started
        print(language, item['id'], record['status'], round(record['seconds'], 2), flush=True)
        return record

    warmup = call(('warmup', {'id': 'warmup', 'prompt': 'Reply with OK.'}), max_tokens=16)
    if warmup['status'] != 'ok':
        raise RuntimeError('Warmup failed; no throughput measurement started')
    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        records = list(pool.map(call, jobs))
    elapsed = time.monotonic() - started
    tokens = sum((r.get('response', {}).get('usage') or {}).get('completion_tokens', 0) for r in records)
    result = {'created_at': datetime.now(timezone.utc).isoformat(), 'concurrency': args.concurrency,
              'seconds': elapsed, 'completion_tokens': tokens, 'tokens_per_second': tokens / elapsed,
              'errors': sum(r['status'] != 'ok' for r in records), 'records': records, 'warmup': warmup,
              'note': 'Throughput probe capped at 512 tokens; not an evaluation result. Warm cache across stages.'}
    write(args.output, result)
    print(json.dumps({k: v for k, v in result.items() if k != 'records'}), flush=True)


if __name__ == '__main__':
    main()
