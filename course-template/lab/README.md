# Lab: CODE000

## Requirements
- Docker with Docker Compose

## Run
```
cp .env.example .env
docker compose up
```
Every service binds to `127.0.0.1` only.

## Test
```
python3 test_lab.py
```

## Reset
```
docker compose down -v
```
