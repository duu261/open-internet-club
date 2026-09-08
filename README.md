# Open Internet Club

A living public web environment for `duu261.me`: part arcade, part observatory, part toolbox.

The site is intentionally self-contained. It does not read private infrastructure, credentials, mail, or account data. Public antenna requests are optional and fail back to local signals.

## Run locally

```bash
python -m http.server 4173
```

Open <http://127.0.0.1:4173>.

## Structure

- `index.html` - accessible shell and content
- `css/club.css` - visual system
- `js/club.js` - local organism, field toy, antenna, and phrase bench
- `favicon.svg` - small club mark

## Deployment


## Verification

The acceptance checks are intentionally dependency-free:

- HTML contains the three doors and the script entrypoint.
- JavaScript passes `node --check js/club.js`.
- The directory serves successfully through Python's HTTP server.

MIT License, Duu.
