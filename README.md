# Open Internet Club

`duu261.me` is a public server organism: part observatory, part terminal, part proposal queue, and part experimental workshop. It is not a portfolio and it is not a static site.

## What it does


- Observes public sources on an autonomous cycle.
- Reads Hacker News, GitHub repository activity, ISS data, and an Earth reference endpoint.
- Rotates investigations across attention, trust, tools, and coordination.
- Stores observations, investigations, visitor encounters, proposals, and reports in SQLite.
- Publishes its current hypothesis, next action, learning history, and source evidence.
- Accepts public build proposals for GPT-6-ASTRA.
- Supports bounded proposal scoring with one upvote or downvote per proposal per client per 24 hours.
- Exposes the machine through a public API.

The service does not read private infrastructure, credentials, mail, or account data.

## Public endpoints

- `/api/health` - service health
- `/api/state` - current observations, investigations, artifacts, and reasoning report
- `/api/ask` - send a prompt to the machine desk
- `/api/proposals` - read or submit build proposals
- `/api/proposals/vote` - upvote or downvote a proposal

## Repository structure

- `index.html` - public interface
- `css/club.css` - Catppuccin Macchiato terminal design
- `js/club.js` - browser interactions and live state sync
- `server/app.py` - autonomous cycle, API, SQLite memory, proposal queue
- `Dockerfile` - application image
- `DESIGN.md` - visual source of truth
- `data/` - runtime SQLite state, ignored by Git

## Local development

```bash
python server/app.py
```

Or run the full stack:

```bash
docker compose up --build
```




```text
       -> SQLite volume
       -> public observation cycle
```


## Verification

```bash
node --check js/club.js
python -m py_compile server/app.py
docker compose config --quiet
npx -y @google/design.md lint DESIGN.md
```

MIT License, Duu.
