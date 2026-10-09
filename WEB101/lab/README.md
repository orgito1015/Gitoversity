# Lab: NorthWind Notes

NorthWind Notes is a tiny note-taking web app for a fictional company. It is deliberately vulnerable. You log in as a normal user (`alice`) and your job in the challenge is to reach two secrets you should not be able to reach.

It is one Python file using only the standard library (`http.server`). No database, no framework, no external services. Everything runs on your machine, bound to `127.0.0.1:8080`.

## Requirements

- Docker with Docker Compose v2 (`docker compose version`), or just Python 3.10+ to run it directly.

## Run

With Docker:

```
cd lab
cp .env.example .env
docker compose up --build
```

Or without Docker:

```
cd lab
cp .env.example .env
set -a; . ./.env; set +a
python3 app.py
```

Then open <http://127.0.0.1:8080> and sign in as `alice` / `password123`.

## Settings (`.env`)

| Variable | Default | Meaning |
|----------|---------|---------|
| `LEVEL` | `1` | `1` vulnerable. `2` applies fixes: access control on notes, output escaping on search, and security headers. |
| `FLAG1`, `FLAG2` | encoded | The flags. Do not read or decode them: that skips the course. |

After changing `.env`, restart the app (`docker compose up -d --force-recreate`, or stop and re-run `app.py`).

## What is in here (intentionally)

- A **broken access control** bug on `GET /note?id=N`: at `LEVEL=1` the app never checks that the note belongs to you.
- An **information disclosure** path reachable through recon: `robots.txt` names a "hidden" directory that has no authentication.
- A **reflected XSS** on `GET /search?q=` at `LEVEL=1` (no flag, for the injection lesson).
- A verbose `Server` header and missing security headers, for the fingerprinting and misconfiguration lessons.

## Test

With the lab running:

```
python3 test_lab.py
```

The smoke test checks the app answers, `robots.txt` discloses the internal path, the internal config endpoint is reachable, login works, and the access-control rule behaves (open at `LEVEL=1`, enforced at `LEVEL=2`).

## Reset

```
docker compose down
```

The app keeps all state in memory, so a restart resets every note and session.
