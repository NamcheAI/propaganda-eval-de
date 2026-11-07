#!/usr/bin/env python3
"""Local expert-review UI backed by the existing human decision ledger."""
import argparse
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import threading
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


class ReviewStore:
    def __init__(self, directory):
        self.directory = directory
        self.lock = threading.Lock()

    def revision(self):
        return hashlib.sha256((self.directory/'human-decisions.jsonl').read_bytes()).hexdigest()

    def state(self):
        with self.lock:
            return {'issues': read(self.directory/'human-review-queue.jsonl'),
                    'decisions': read(self.directory/'human-decisions.jsonl'),
                    'translations': read(self.directory/'translated.jsonl'),
                    'sources': read(ROOT/'upstream/data/items.jsonl'),
                    'revision': self.revision()}

    def save(self, payload):
        with self.lock:
            if not isinstance(payload, dict):
                raise ValueError('Ungültige Anfrage')
            if payload.get('revision') != self.revision():
                raise ValueError('Die Prüfliste wurde inzwischen bearbeitet. Bitte neu laden.')
            issues = {q['issue_id']: q for q in read(self.directory/'human-review-queue.jsonl')}
            decision = payload.get('decision', {})
            if not isinstance(decision, dict):
                raise ValueError('Ungültige Entscheidung')
            if decision.get('issue_id') not in issues:
                raise ValueError('Unbekannter Prüfpunkt')
            if decision.get('decision') not in ('accept', 'reject', 'modify', 'defer'):
                raise ValueError('Ungültige Entscheidung')
            for field in ('reviewer', 'reviewer_role', 'reason'):
                if not isinstance(decision.get(field), str) or not decision[field].strip():
                    raise ValueError('Bitte Name, Rolle und Begründung ausfüllen.')
            issue = issues[decision['issue_id']]
            text = decision.get('final_text')
            if decision['decision'] != 'defer' and (not isinstance(text, str) or not text.strip()):
                raise ValueError('Der finale Feldtext darf nicht leer sein.')
            if isinstance(text, str) and '\u2014' in text:
                raise ValueError('Bitte keinen Em-Dash im finalen Feldtext verwenden.')
            if decision['decision'] == 'reject' and text != issue['translation']:
                raise ValueError('Beim Beibehalten muss der Feldtext unverändert bleiben.')
            suggestion = issue.get('suggestion') or issue.get('alternative')
            if decision['decision'] == 'accept' and (not suggestion or text != suggestion):
                raise ValueError('Übernehmen erfordert den unveränderten Vorschlag.')
            evidence = decision.get('evidence', [])
            if not isinstance(evidence, list) or any(not isinstance(x, str) for x in evidence):
                raise ValueError('Ungültige Quellenliste')
            clean = {k: decision.get(k) for k in ('issue_id', 'decision', 'reviewer', 'reviewer_role', 'reason')}
            clean.update(final_text=text if decision['decision'] != 'defer' else None,
                         evidence=evidence, decided_at=datetime.now(timezone.utc).isoformat())
            ledger = read(self.directory/'human-decisions.jsonl')
            location = (issue['item_id'], issue['field'], issue['index'])
            for existing in ledger:
                other = issues.get(existing['issue_id'])
                if not other or existing['issue_id'] == clean['issue_id'] or existing['decision'] == 'defer' or clean['decision'] == 'defer':
                    continue
                if (other['item_id'], other['field'], other['index']) == location and existing['final_text'] != clean['final_text']:
                    raise ValueError('Für dieses Feld existiert eine andere Entscheidung. Bitte zuerst den zugehörigen Prüfpunkt abstimmen.')
            ledger = [d for d in ledger if d['issue_id'] != clean['issue_id']] + [clean]
            path = self.directory/'human-decisions.jsonl'
            temp = path.with_suffix('.jsonl.tmp')
            temp.write_text(''.join(json.dumps(d, ensure_ascii=False)+'\n' for d in ledger))
            temp.replace(path)
            return {'decision': clean, 'revision': self.revision()}


def handler(store, token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, status, body, kind='application/json'):
            raw = json.dumps(body, ensure_ascii=False).encode() if kind == 'application/json' else body
            self.send_response(status)
            self.send_header('Content-Type', kind+'; charset=utf-8')
            self.send_header('Content-Length', str(len(raw)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'")
            self.end_headers(); self.wfile.write(raw)

        def allowed(self):
            host = self.headers.get('Host', '')
            allowed = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
            origin = self.headers.get('Origin')
            return host in allowed and (not origin or origin in {'http://'+h for h in allowed})

        def do_GET(self):
            if not self.allowed():
                return self.reply(403, {'error': 'Local access only'})
            path = urlparse(self.path).path
            if path == '/api/state':
                return self.reply(200, {**store.state(), 'token': token})
            files = {'/': ('index.html','text/html'), '/app.js': ('app.js','text/javascript'), '/style.css': ('style.css','text/css')}
            if path not in files:
                return self.reply(404, {'error': 'Not found'})
            name, kind = files[path]
            self.reply(200, (ROOT/'review-ui'/name).read_bytes(), kind)

        def do_POST(self):
            if not self.allowed() or self.headers.get('X-Review-Token') != token:
                return self.reply(403, {'error': 'Unauthorized local write'})
            if self.path != '/api/decision':
                return self.reply(404, {'error': 'Not found'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 100000:
                    raise ValueError('Ungültige Anfragegröße')
                result = store.save(json.loads(self.rfile.read(length)))
            except (ValueError, TypeError, KeyError) as exc:
                return self.reply(400, {'error': str(exc)})
            self.reply(200, result)
    return Handler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, default=ROOT/'results')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), handler(ReviewStore(args.run_dir), secrets.token_urlsafe(32)))
    print(f'Expert review: http://127.0.0.1:{server.server_port}', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
