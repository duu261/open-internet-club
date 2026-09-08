(() => {
  'use strict';

  const $ = (selector) => document.querySelector(selector);
  const root = document.documentElement;
  const state = {
    started: Date.now(),
    seed: Math.floor(Math.random() * 9000) + 1000,
    route: 'undecided',
    nodes: [],
    listener: { x: 480, y: 210 },
  };

  const els = {
    status: $('#status-line'), greeting: $('#greeting'), why: $('#why'), signal: $('#signal-now'),
    mood: $('#fact-mood'), route: $('#fact-route'), seed: $('#fact-seed'), session: $('#fact-session'),
    voice: $('#organism-voice'), curiosity: $('#curiosity'), reportMission: $('#agent-mission'), reportBody: $('#agent-report-body'), sources: $('#agent-sources'), proposalForm: $('#proposal-form'), proposalInput: $('#proposal-input'), proposalMessage: $('#proposal-message'), proposalList: $('#proposal-list'), chamber: $('#chamber'), chamberLede: $('#chamber-lede'),
    deskForm: $('#desk-form'), deskInput: $('#desk-input'), deskReply: $('#desk-reply'), deskError: $('#desk-error'),
    field: $('#field'), fieldEmpty: $('#field-empty'), meter: $('#play-meter'),
    useForm: $('#use-form'), useInput: $('#use-input'), useOut: $('#use-out'), useEmpty: $('#use-empty'), useError: $('#use-error'),
    swatch: $('#use-swatch'), color: $('#use-color'), hash: $('#use-hash'), slug: $('#use-slug'), rot13: $('#use-rot13'), reverse: $('#use-reverse'), bytes: $('#use-bytes'),
    iss: $('#iss-body'), equator: $('#equator-body'), today: $('#today-body'), watchError: $('#watch-error'), log: $('#radio-log')
  };
  const doors = [...document.querySelectorAll('[data-door]')];
  const panels = [...document.querySelectorAll('[data-panel]')];
  const phrases = ['the page noticed the hour', 'a small route has opened', 'the browser brought its own weather', 'nothing private crossed the threshold'];
  const curiosities = ['What should a machine reveal before it asks for trust?', 'Can a useful tool also feel like a place?', 'Which signal would you keep if the network went quiet?', 'A good interface leaves a little room for mischief.'];

  function hashSeed(text) {
    let h = 2166136261;
    for (let i = 0; i < text.length; i += 1) h = Math.imul(h ^ text.charCodeAt(i), 16777619);
    return (`00000000${(h >>> 0).toString(16)}`).slice(-8);
  }
  function setRoute(route) {
    state.route = route;
    els.route.textContent = route;
    doors.forEach((door) => door.setAttribute('aria-pressed', door.dataset.door === route ? 'true' : 'false'));
    panels.forEach((panel) => { panel.hidden = panel.dataset.panel !== route; });
    els.chamberLede.textContent = route === 'undecided' ? 'Walk a door, or let me choose.' : `The ${route} chamber is open.`;
    if (route !== 'undecided') els.chamber.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  function refreshPulse() {
    const seconds = Math.floor((Date.now() - state.started) / 1000);
    const minute = new Date().getMinutes();
    const mood = ['listening', 'curious', 'restless', 'clear'][minute % 4];
    els.status.textContent = `${mood} / local time ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    els.mood.textContent = mood;
    els.seed.textContent = state.seed;
    els.session.textContent = `${seconds}s`;
    els.signal.textContent = `${phrases[(minute + seconds) % phrases.length]} · pulse ${String((state.seed + seconds * 7) % 100).padStart(2, '0')}`;
    els.curiosity.textContent = curiosities[(minute + Math.floor(seconds / 15)) % curiosities.length];
  }
  function greeting() {
    const hour = new Date().getHours();
    const time = hour < 6 ? 'The network is quiet enough to hear the small things.' : hour < 12 ? 'Good morning. The club is already rearranging its furniture.' : hour < 18 ? 'The room is open. Bring a question or leave with a tool.' : 'Evening mode: fewer answers, better signals.';
    els.greeting.textContent = time;
    els.why.textContent = 'I can play, watch, use, or choose for you. Nothing here pretends to be your private system.';
    els.voice.textContent = 'I keep time, make routes, and expose my limits. I do not see your accounts or touch your machines.';
  }
  function openDoor(route) { setRoute(route); if (route === 'play') drawField(); if (route === 'watch') loadWatch(); }

  // Replies are assembled only from fixed strings and escaped route labels, never raw user input.
  function reply(html) { els.deskError.hidden = true; els.deskReply.innerHTML = `<p class="reply">${html}</p>`; }
  function ask(input) {
    const q = input.trim().toLowerCase();
    if (!q) { els.deskError.textContent = 'The desk needs a few words.'; els.deskError.hidden = false; return; }
    fetch('/api/ask', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ prompt: input }) })
      .then((response) => response.json())
      .then((data) => { if (data.result) reply(`<strong>server mind:</strong> ${data.result}`); })
      .catch(() => {});
    if (/help|map|door/.test(q)) { reply('Three doors: <button class="inline-action" data-open="play">play</button>, <button class="inline-action" data-open="watch">watch</button>, and <button class="inline-action" data-open="use">use</button>.'); return; }
    if (/play|plant|field|game/.test(q)) { openDoor('play'); reply('Opening the signal field. Plant a node and see whether it finds company.'); return; }
    if (/watch|signal|sky|world|iss/.test(q)) { openDoor('watch'); reply('Opening the antenna. It tries public sources, then falls back honestly to the local radio.'); return; }
    if (/use|hash|color|phrase|tool/.test(q)) { openDoor('use'); reply('Opening the phrase bench. Give it something that has not been polished yet.'); return; }
    const object = ['a blue hour', 'a future tool', 'one honest constraint', 'a door without a room'][state.seed % 4];
    reply(`I found <strong>${object}</strong>. It is not an answer yet. Try “play”, “watch”, or “use”, then make it earn its name.`);
  }

  function drawField() {
    const canvas = els.field; const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect(); const scale = canvas.width / rect.width; const point = (event) => ({ x: (event.clientX - rect.left) * scale, y: (event.clientY - rect.top) * scale });
    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height); ctx.fillStyle = '#10212a'; ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.strokeStyle = 'rgba(102, 194, 190, .12)'; ctx.lineWidth = 1;
      for (let x = 0; x < canvas.width; x += 48) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke(); }
      for (let y = 0; y < canvas.height; y += 48) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke(); }
      state.nodes.forEach((node, index) => { state.nodes.slice(index + 1).forEach((other) => { const d = Math.hypot(node.x - other.x, node.y - other.y); if (d < 220) { ctx.strokeStyle = `rgba(199,146,62,${1 - d / 260})`; ctx.beginPath(); ctx.moveTo(node.x, node.y); ctx.lineTo(other.x, other.y); ctx.stroke(); } }); });
      state.nodes.forEach((node, index) => { ctx.fillStyle = index % 2 ? '#66c2be' : '#c7923e'; ctx.beginPath(); ctx.arc(node.x, node.y, 6 + (index % 3), 0, Math.PI * 2); ctx.fill(); });
      ctx.strokeStyle = '#f3eee4'; ctx.beginPath(); ctx.arc(state.listener.x, state.listener.y, 12, 0, Math.PI * 2); ctx.stroke();
      const links = state.nodes.reduce((sum, n, i) => sum + state.nodes.slice(i + 1).filter((m) => Math.hypot(n.x - m.x, n.y - m.y) < 220).length, 0);
      els.meter.textContent = `nodes ${state.nodes.length} / links ${links} / density ${state.nodes.length > 7 ? 'alive' : state.nodes.length > 2 ? 'forming' : 'quiet'}`; els.fieldEmpty.hidden = state.nodes.length > 0;
    };
    if (!canvas.dataset.bound) { canvas.dataset.bound = 'true'; canvas.addEventListener('click', (event) => { state.nodes.push(point(event)); render(); }); document.addEventListener('keydown', (event) => { if (state.route !== 'play') return; const step = 18; if (event.key === 'ArrowLeft') state.listener.x -= step; if (event.key === 'ArrowRight') state.listener.x += step; if (event.key === 'ArrowUp') state.listener.y -= step; if (event.key === 'ArrowDown') state.listener.y += step; if (event.key.toLowerCase() === 'c') state.nodes = []; state.listener.x = Math.max(15, Math.min(canvas.width - 15, state.listener.x)); state.listener.y = Math.max(15, Math.min(canvas.height - 15, state.listener.y)); render(); }); }
    render();
  }

  async function loadWatch() {
    els.watchError.hidden = true;
    try { const response = await fetch('https://api.open-notify.org/iss-now.json'); if (!response.ok) throw new Error('tracker unavailable'); const data = await response.json(); els.iss.textContent = `over ${Number(data.iss_position.latitude).toFixed(2)}°, ${Number(data.iss_position.longitude).toFixed(2)}° at ${new Date(data.timestamp * 1000).toLocaleTimeString()}`; } catch { els.iss.textContent = 'public tracker unavailable; local radio remains online'; els.watchError.textContent = 'One antenna did not answer. The other signals are generated locally, not faked as live data.'; els.watchError.hidden = false; }
    try { const response = await fetch('https://api.open-meteo.com/v1/forecast?latitude=0&longitude=0&current=temperature_2m,wind_speed_10m'); if (!response.ok) throw new Error(); const data = await response.json(); els.equator.textContent = `${data.current.temperature_2m}°C · wind ${data.current.wind_speed_10m} km/h`; } catch { els.equator.textContent = 'equator antenna offline'; }
    els.today.textContent = `the local date is ${new Date().toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' })}`;
    const li = document.createElement('li'); li.textContent = `${new Date().toLocaleTimeString()} · antenna checked · browser only`; els.log.prepend(li); while (els.log.children.length > 5) els.log.lastElementChild.remove();
  }

  async function transform(event) {
    event.preventDefault(); const text = els.useInput.value; if (!text.trim()) { els.useError.textContent = 'Give the phrase bench something to work with.'; els.useError.hidden = false; return; }
    els.useError.hidden = true; const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text)); const hash = [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join(''); const color = `#${hash.slice(0, 6)}`;
    els.swatch.style.background = color; els.color.textContent = `${color} · ${text.length} characters`; els.hash.textContent = hash; els.slug.textContent = text.toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'empty'; els.rot13.textContent = text.replace(/[a-z]/gi, (c) => String.fromCharCode(c.charCodeAt(0) + (/[a-m]/i.test(c) ? 13 : -13))); els.reverse.textContent = [...text].reverse().join(''); els.bytes.textContent = new TextEncoder().encode(text).length; els.useEmpty.hidden = true; els.useOut.hidden = false;
  }

  async function refreshProposals() {
    try {
      const response = await fetch('/api/proposals', { cache: 'no-store' });
      const data = await response.json();
      els.proposalList.replaceChildren();
      if (!data.proposals?.length) { const li = document.createElement('li'); li.textContent = '[?] no proposals yet'; els.proposalList.append(li); return; }
      data.proposals.forEach((proposal) => {
        const li = document.createElement('li');
        const label = document.createElement('span'); label.textContent = `[+] ${proposal.text}`;
        const vote = document.createElement('button'); vote.type = 'button'; vote.className = 'proposal-vote'; vote.textContent = '[↑] vote'; vote.setAttribute('aria-label', `Vote for ${proposal.text}`); vote.addEventListener('click', async () => { const result = await fetch('/api/proposals/vote', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: proposal.id }) }).then((r) => r.json()); els.proposalMessage.textContent = result.error || '[+] vote recorded'; refreshProposals(); });
        li.append(label, vote); els.proposalList.append(li);
      });
    } catch { els.proposalMessage.textContent = '[x] proposal store unavailable'; }
  }
  els.proposalForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const text = els.proposalInput.value.trim();
    const result = await fetch('/api/proposals', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) }).then((r) => r.json());
    els.proposalMessage.textContent = result.error || '[+] proposal stored';
    if (!result.error) { els.proposalInput.value = ''; refreshProposals(); }
  });
  refreshProposals();
  setInterval(refreshProposals, 30000);

  async function syncAgent() {
    try {
      const response = await fetch('/api/state', { cache: 'no-store' });
      if (!response.ok) throw new Error('server unavailable');
      const live = await response.json();
      els.status.textContent = `server awake / ${live.observation_count} observations / ${new Date(live.server_time).toLocaleTimeString()}`;
      els.voice.textContent = `I am alive on a server. I have remembered ${live.observation_count} observations and I run a world cycle every minute.`;
      els.reportMission.textContent = live.mission;
      els.reportBody.textContent = live.latest_report?.body || 'waiting for the first completed cycle';
      const latestSources = new Map();
      (live.observations || []).filter((item) => ['internet', 'github', 'iss', 'world'].includes(item.kind)).forEach((item) => { if (!latestSources.has(item.kind)) latestSources.set(item.kind, item); });
      els.sources.textContent = [...latestSources.values()].map((item) => `[${item.kind}] ${item.value}`).join('\n') || '[?] no source readings yet';
      if (live.observations?.[0]) els.signal.textContent = `${live.observations[0].value} · persistent memory online`;
    } catch {
      els.voice.textContent = 'The server mind is unreachable. Local play remains available.';
    }
  }
  syncAgent();
  setInterval(syncAgent, 30000);
  doors.forEach((door) => door.addEventListener('click', () => openDoor(door.dataset.door)));
  els.deskForm.addEventListener('submit', (event) => { event.preventDefault(); ask(els.deskInput.value); });
  els.deskReply.addEventListener('click', (event) => { const target = event.target.closest('[data-open]'); if (target) openDoor(target.dataset.open); });
  els.useForm.addEventListener('submit', transform); $('#use-clear').addEventListener('click', () => { els.useInput.value = ''; els.useOut.hidden = true; els.useEmpty.hidden = false; });
  document.addEventListener('keydown', (event) => { if (event.target.matches('input, textarea')) return; if (event.key === '1') openDoor('play'); if (event.key === '2') openDoor('watch'); if (event.key === '3') openDoor('use'); if (event.key === '/') { event.preventDefault(); els.deskInput.focus(); } if (event.key === '?') reply('Keys: <kbd>1</kbd> play, <kbd>2</kbd> watch, <kbd>3</kbd> use, <kbd>/</kbd> focus the desk.'); });
  greeting(); refreshPulse(); setInterval(refreshPulse, 1000);
})();
