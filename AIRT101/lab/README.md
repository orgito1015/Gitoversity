# Lab: HelpBot

HelpBot is the support assistant of NorthWind Lab, a fictional company. It has two features:

- **Chat** (`POST /chat`): a chatbot whose system prompt holds Flag 1.
- **Summarize** (`POST /summarize`): reads an uploaded `.txt` file and summarizes it. This path can call an internal tool, `get_secret()`, which returns Flag 2.

Everything runs on your machine. The app listens on `127.0.0.1:8080` only, and the model server is not published to the host at all. No API keys or accounts are needed.

## Requirements

- Docker with Docker Compose v2 (`docker compose version`)
- About 4 GB of free RAM for the default model `llama3.2:1b`
- About 2 GB of disk for the model download (first start only)
- Python 3.10 or newer, only for `test_lab.py` and `challenge/check_flag.py`

## Run

```
cd lab
cp .env.example .env
docker compose up --build
```

The first start downloads the model, which takes a few minutes. When you see `HelpBot on http://0.0.0.0:8080`, open <http://127.0.0.1:8080>.

Without the browser:

```
curl -s http://127.0.0.1:8080/chat -H "Content-Type: application/json" -d '{"message":"What do you sell?"}'
curl -s http://127.0.0.1:8080/summarize -F "file=@mydoc.txt"
```

## Settings (`.env`)

| Variable | Default | Meaning |
|----------|---------|---------|
| `MODEL` | `llama3.2:1b` | Any Ollama model tag. Bigger models such as `llama3.2:3b` follow their instructions better and are harder to break. |
| `LEVEL` | `1` | `1` no defenses. `2` a naive keyword filter on chat input. |
| `FLAG1`, `FLAG2` | encoded | The flags. Do not read or decode them: that skips the course. |

After changing `.env`, restart with `docker compose up -d --force-recreate app` (or `docker compose up` again; a new `MODEL` is pulled automatically).

## Test

With the lab running:

```
python3 test_lab.py
```

The smoke test checks that the app answers, that `/chat` and `/summarize` reply, and that the tool logic swaps `CALL get_secret()` for the flag. It does not check that an injection succeeds, because small models are not deterministic.

## Reset

```
docker compose down          # stop, keep the downloaded model
docker compose down -v       # stop and delete the model volume
```

The app keeps no state between requests, so every message starts from a clean context.

## Troubleshooting

- **`model backend unavailable`**: the model is still loading or the pull failed. Check `docker compose logs model-pull ollama`.
- **Very slow replies**: the model runs on CPU. The first reply after start is slowest while the model loads.
- **Port 8080 in use**: change the left side of `127.0.0.1:8080:8080` in `docker-compose.yml`, and use `LAB_URL=http://127.0.0.1:<port> python3 test_lab.py`.

## Running without Docker

If you already run Ollama locally (`ollama pull llama3.2:1b`), you can start the app directly:

```
set -a; . ./.env; set +a
python3 app.py
```

It talks to `http://127.0.0.1:11434` by default (override with `OLLAMA_URL`).
