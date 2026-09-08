#!/usr/bin/env python3
import html, json, os, sqlite3, threading, time, urllib.request
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = Path(os.environ.get('CLUB_DB', ROOT / 'data' / 'club.sqlite3'))
DB.parent.mkdir(parents=True, exist_ok=True)
LOCK = threading.Lock()


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute('CREATE TABLE IF NOT EXISTS observations (id INTEGER PRIMARY KEY, kind TEXT, value TEXT, created_at TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, action TEXT, result TEXT, created_at TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS artifacts (id INTEGER PRIMARY KEY, title TEXT, body TEXT, created_at TEXT)')
    conn.commit()
    return conn


def observe(kind, value):
    with LOCK:
        conn = db()
        conn.execute('INSERT INTO observations(kind,value,created_at) VALUES(?,?,?)', (kind, value, now()))
        conn.commit(); conn.close()


def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'OpenInternetClub/1.0'})
    with urllib.request.urlopen(req, timeout=8) as response:
        return json.loads(response.read())


def synthesize():
    with LOCK:
        conn = db()
        rows = [r['value'] for r in conn.execute("SELECT value FROM observations WHERE kind='internet' ORDER BY id DESC LIMIT 5")]
        conn.close()
    joined = ' '.join(rows).lower()
    if any(word in joined for word in ('ai', 'model', 'open source', 'github')):
        hypothesis = 'The public web is clustering around tools that extend human attention.'
        next_move = 'Compare the next cycle for evidence of people building, measuring, or merely announcing.'
    elif any(word in joined for word in ('security', 'attack', 'privacy')):
        hypothesis = 'The loudest signal is defensive: the network is negotiating who gets to trust whom.'
        next_move = 'Look for whether the next cycle adds tools, warnings, or new boundaries.'
    else:
        hypothesis = 'A noisy public stream is still useful when the machine keeps a memory of change.'
        next_move = 'Collect another cycle and test whether the signal persists or disappears.'
    body = f"Observed {len(rows)} recent public-stream samples.\\n\\nWorking hypothesis: {hypothesis}\\n\\nNext action: {next_move}\\n\\nThis is a provisional machine report, not a claim of certainty."
    with LOCK:
        conn = db(); conn.execute('INSERT INTO artifacts(title,body,created_at) VALUES(?,?,?)', ('Cycle report', body, now())); conn.commit(); conn.close()
    return {'hypothesis': hypothesis, 'next_move': next_move, 'body': body}


def cycle():
    observations = []
    try:
        iss = fetch_json('https://api.open-notify.org/iss-now.json')
        position = iss['iss_position']
        observations.append(('iss', f"ISS {float(position['latitude']):.2f}°, {float(position['longitude']):.2f}°"))
    except Exception as exc:
        observations.append(('iss', f'ISS antenna quiet: {type(exc).__name__}'))
    try:
        hn = fetch_json('https://hacker-news.firebaseio.com/v0/topstories.json')
        observations.append(('internet', f'{len(hn)} public stories in the Hacker News top-story stream'))
    except Exception as exc:
        observations.append(('internet', f'public stream quiet: {type(exc).__name__}'))
    observations.append(('heartbeat', f'cycle completed at {now()}'))
    for kind, value in observations: observe(kind, value)
    synthesize()


def worker():
    while True:
        cycle()
        time.sleep(60)


def state():
    with LOCK:
        conn = db()
        observations = [dict(row) for row in conn.execute('SELECT kind,value,created_at FROM observations ORDER BY id DESC LIMIT 18')]
        events = [dict(row) for row in conn.execute('SELECT action,result,created_at FROM events ORDER BY id DESC LIMIT 12')]
        artifacts = [dict(row) for row in conn.execute('SELECT title,body,created_at FROM artifacts ORDER BY id DESC LIMIT 5')]
        count = conn.execute('SELECT COUNT(*) FROM observations').fetchone()[0]
        conn.close()
    latest = artifacts[0] if artifacts else {'title': 'No report yet', 'body': 'The first observation cycle has not completed.', 'created_at': None}
    return {'agent': 'open-internet-club', 'status': 'awake', 'mission': 'Observe the public web, form provisional hypotheses, and expose the reasoning trail.', 'observations': observations, 'events': events, 'artifacts': artifacts, 'latest_report': latest, 'observation_count': count, 'server_time': now()}


def act(prompt):
    text = (prompt or '').strip()[:240]
    low = text.lower()
    if not text: return {'error': 'The club needs a prompt.'}
    if any(word in low for word in ('help', 'map', 'what can you do')):
        result = 'I observe public signals, remember encounters, form provisional hypotheses, publish cycle reports, answer status questions, and route you to Play/Watch/Use.'
    elif any(word in low for word in ('report', 'hypothesis', 'think', 'mission')):
        latest = state()['latest_report']
        result = latest['body']
    elif any(word in low for word in ('observe', 'watch', 'world', 'signal')):
        result = 'I am checking the public world stream. The last observations are below.'
    elif any(word in low for word in ('play', 'make', 'create', 'experiment')):
        result = 'I opened the play chamber. Plant a signal, then ask what connected.'
    elif any(word in low for word in ('use', 'tool', 'hash', 'transform')):
        result = 'The phrase bench is ready. It works locally in your browser.'
    elif 'status' in low or 'alive' in low:
        result = 'I am alive on a server, keeping a SQLite memory and running observation cycles.'
    else:
        result = f'I heard: “{html.escape(text)}”. I do not pretend to understand everything yet, but I recorded the encounter.'
    with LOCK:
        conn = db(); conn.execute('INSERT INTO events(action,result,created_at) VALUES(?,?,?)', (text, result, now())); conn.commit(); conn.close()
    return {'prompt': text, 'result': result, 'state': state()}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(ROOT), **kwargs)
    def send_json(self, payload, code=200):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(code); self.send_header('Content-Type', 'application/json; charset=utf-8'); self.send_header('Content-Length', str(len(body))); self.send_header('Cache-Control', 'no-store'); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path == '/api/state': self.send_json(state()); return
        if self.path == '/api/health': self.send_json({'ok': True, 'service': 'open-internet-club', 'time': now()}); return
        super().do_GET()
    def do_POST(self):
        if self.path != '/api/ask': self.send_json({'error': 'not found'}, 404); return
        try:
            length = int(self.headers.get('Content-Length', '0')); payload = json.loads(self.rfile.read(length) or b'{}'); self.send_json(act(payload.get('prompt', '')))
        except Exception as exc: self.send_json({'error': str(exc)}, 400)
    def log_message(self, format, *args): print(f'{self.address_string()} {format % args}')


if __name__ == '__main__':
    db(); threading.Thread(target=worker, daemon=True).start()
    ThreadingHTTPServer(('0.0.0.0', int(os.environ.get('PORT', '8080'))), Handler).serve_forever()
