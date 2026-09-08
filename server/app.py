#!/usr/bin/env python3
import hashlib, html, json, os, re, sqlite3, threading, time, urllib.request
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
    conn.execute('CREATE TABLE IF NOT EXISTS investigations (id INTEGER PRIMARY KEY, topic TEXT, question TEXT, status TEXT, finding TEXT, created_at TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS proposals (id INTEGER PRIMARY KEY, text TEXT NOT NULL, normalized TEXT NOT NULL UNIQUE, votes INTEGER NOT NULL DEFAULT 1, status TEXT NOT NULL DEFAULT "open", created_at TEXT)')
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


TOPICS = [
    ('attention', 'What are people building to extend attention?'),
    ('trust', 'Where is the public web adding or removing trust?'),
    ('tools', 'Which tools are becoming infrastructure for other tools?'),
    ('coordination', 'How are strangers coordinating around shared signals?'),
]


def synthesize(topic, question):
    with LOCK:
        conn = db()
        rows = [r['value'] for r in conn.execute("SELECT value FROM observations WHERE kind IN ('internet','github','world') ORDER BY id DESC LIMIT 8")]
        prior = [r['body'] for r in conn.execute('SELECT body FROM artifacts ORDER BY id DESC LIMIT 3')]
        conn.close()
    joined = ' '.join(rows).lower()
    if topic == 'trust' or any(word in joined for word in ('security', 'attack', 'privacy')):
        hypothesis = 'The public web is spending as much energy defining trust boundaries as it is building features.'
        next_move = 'Compare the next trust cycle for warnings, permissions, and repair tools.'
    elif topic == 'tools' or any(word in joined for word in ('ai', 'model', 'open source', 'github')):
        hypothesis = 'The strongest public signals are tools that extend human attention and become tools for other tools.'
        next_move = 'Track whether these tools gain users, integrations, or only announcements.'
    elif topic == 'coordination':
        hypothesis = 'Coordination is visible as repeated signals: people return to the same objects and give them shared meaning.'
        next_move = 'Look for persistence across sources instead of trusting a single loud headline.'
    else:
        hypothesis = 'Attention is being shaped by systems that decide what deserves another minute.'
        next_move = 'Follow the next cycle and test whether the same attention pattern survives.'
    learning = 'No prior model to compare against.' if not prior else 'The machine is comparing this cycle against its last three reports instead of treating each cycle as new.'
    body = f"Investigation: {topic}\nQuestion: {question}\n\nWorking hypothesis: {hypothesis}\n\nNext action: {next_move}\n\nLearning: {learning}\n\nThis is a provisional machine report, not a claim of certainty."
    with LOCK:
        conn = db()
        conn.execute('INSERT INTO artifacts(title,body,created_at) VALUES(?,?,?)', (f'{topic.title()} investigation', body, now()))
        conn.execute('INSERT INTO investigations(topic,question,status,finding,created_at) VALUES(?,?,?,?,?)', (topic, question, 'complete', hypothesis, now()))
        conn.commit(); conn.close()
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
    try:
        gh = fetch_json('https://api.github.com/search/repositories?q=stars:%3E1000&sort=updated&order=desc&per_page=5')
        observations.append(('github', f"{len(gh.get('items', []))} recently active high-signal repositories in the public GitHub stream"))
    except Exception as exc:
        observations.append(('github', f'code stream quiet: {type(exc).__name__}'))
    try:
        world = fetch_json('https://api.le-systeme-solaire.net/rest/bodies/terre')
        observations.append(('world', f"Earth reference: gravity {world.get('gravity', 'unknown')} m/s², density {world.get('density', 'unknown')}"))
    except Exception as exc:
        observations.append(('world', f'world reference quiet: {type(exc).__name__}'))
    observations.append(('heartbeat', f'cycle completed at {now()}'))
    for kind, value in observations: observe(kind, value)
    with LOCK:
        conn = db(); cycle_count = conn.execute('SELECT COUNT(*) FROM investigations').fetchone()[0]; conn.close()
    topic, question = TOPICS[cycle_count % len(TOPICS)]
    synthesize(topic, question)


def worker():
    while True:
        cycle()
        time.sleep(60)


RATE = {}
RATE_LOCK = threading.Lock()


def client_key(handler):
    forwarded = handler.headers.get('X-Forwarded-For', '')
    return (forwarded.split(',')[0].strip() or handler.client_address[0])[:80]


def allowed(key, action, window=300, limit=6):
    stamp = time.time()
    with RATE_LOCK:
        bucket = [t for t in RATE.get((key, action), []) if stamp - t < window]
        if len(bucket) >= limit:
            RATE[(key, action)] = bucket
            return False
        bucket.append(stamp); RATE[(key, action)] = bucket
        return True


def proposals():
    with LOCK:
        conn = db(); rows = [dict(r) for r in conn.execute('SELECT id,text,votes,status,created_at FROM proposals WHERE status != "pruned" ORDER BY votes DESC,id DESC LIMIT 30')]; conn.close()
    return rows


def add_proposal(text, key):
    text = re.sub(r'\\s+', ' ', (text or '').strip())
    if not 8 <= len(text) <= 180: return {'error': 'Proposal must be 8-180 characters.'}
    if re.search(r'https?://|www\\.|<[^>]+>|[A-Za-z0-9+/]{36,}', text, re.I): return {'error': 'Links, markup, and token-like strings are not accepted.'}
    if not allowed(key, 'proposal', 3600, 3): return {'error': 'Proposal rate limit reached. Let the machine digest the queue first.'}
    normalized = re.sub(r'[^a-z0-9 ]', '', text.lower()).strip()
    digest = hashlib.sha256(normalized.encode()).hexdigest()[:16]
    with LOCK:
        conn = db()
        existing = conn.execute('SELECT id FROM proposals WHERE normalized=?', (digest,)).fetchone()
        if existing: conn.close(); return {'error': 'A similar proposal is already in the store.', 'duplicate': existing['id']}
        conn.execute('INSERT INTO proposals(text,normalized,created_at) VALUES(?,?,?)', (text, digest, now())); conn.commit(); conn.close()
    return {'ok': True, 'proposals': proposals()}


def vote_proposal(proposal_id, key):
    if not allowed(key, f'vote:{proposal_id}', 3600, 1): return {'error': 'You already voted on this proposal recently.'}
    with LOCK:
        conn = db(); cur = conn.execute('UPDATE proposals SET votes=votes+1 WHERE id=? AND status != "pruned"', (int(proposal_id),)); conn.commit(); conn.close()
    if cur.rowcount == 0: return {'error': 'Proposal not found.'}
    return {'ok': True, 'proposals': proposals()}


def state():
    with LOCK:
        conn = db()
        observations = [dict(row) for row in conn.execute('SELECT kind,value,created_at FROM observations ORDER BY id DESC LIMIT 18')]
        events = [dict(row) for row in conn.execute('SELECT action,result,created_at FROM events ORDER BY id DESC LIMIT 12')]
        artifacts = [dict(row) for row in conn.execute('SELECT title,body,created_at FROM artifacts ORDER BY id DESC LIMIT 5')]
        investigations = [dict(row) for row in conn.execute('SELECT topic,question,status,finding,created_at FROM investigations ORDER BY id DESC LIMIT 8')]
        count = conn.execute('SELECT COUNT(*) FROM observations').fetchone()[0]
        conn.close()
    latest = artifacts[0] if artifacts else {'title': 'No report yet', 'body': 'The first investigation has not completed.', 'created_at': None}
    return {'agent': 'open-internet-club', 'status': 'awake', 'mission': 'Rotate investigations across attention, trust, tools, and coordination; compare evidence across cycles.', 'investigations': investigations, 'observations': observations, 'events': events, 'artifacts': artifacts, 'latest_report': latest, 'observation_count': count, 'server_time': now()}


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
        if self.path == '/api/proposals': self.send_json({'proposals': proposals()}); return
        if self.path == '/api/health': self.send_json({'ok': True, 'service': 'open-internet-club', 'time': now()}); return
        super().do_GET()
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', '0')); payload = json.loads(self.rfile.read(length) or b'{}')
            key = client_key(self)
            if self.path == '/api/ask': self.send_json(act(payload.get('prompt', ''))); return
            if self.path == '/api/proposals': self.send_json(add_proposal(payload.get('text', ''), key)); return
            if self.path == '/api/proposals/vote': self.send_json(vote_proposal(payload.get('id', 0), key)); return
            self.send_json({'error': 'not found'}, 404)
        except Exception as exc: self.send_json({'error': str(exc)}, 400)
    def log_message(self, format, *args): print(f'{self.address_string()} {format % args}')


if __name__ == '__main__':
    db(); threading.Thread(target=worker, daemon=True).start()
    ThreadingHTTPServer(('0.0.0.0', int(os.environ.get('PORT', '8080'))), Handler).serve_forever()
