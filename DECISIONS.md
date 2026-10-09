# Decisions

Short log of choices made while building Gitoversity. Newest last.

## Phase 1: Scaffold cleanup
- Added `.gitignore` (ignores `.env`), `LICENSE` (MIT for code, CC BY 4.0 for content), and an empty `writeup/README.md` template to both `course-template/` and `AIRT101/`.
- Filled `course-template/` stubs (one note, lab README + `.env.example`, challenge README) so the template matches the section 4 shape out of the box.
- Removed `.gitkeep` files from folders that now hold real files.

## Phase 2: AIRT101 lab
- Flags are stored base64-encoded (`b64:` prefix) in `.env.example`, not plain text, so the repo never ships a readable flag. `app.py` decodes them. This also satisfies the "no plain-text flag in git" rule for the example file.
- Chose a `model-pull` one-shot service in compose to pull `MODEL` into a named volume on first start, so `docker compose up` is the only command needed. The Ollama port is not published to the host at all; only the app container reaches it.
- `app.py` is stdlib only (`http.server`, `urllib`, `email` for multipart parsing). `ThreadingHTTPServer` so a slow model request does not block the health check.
- Added `/health`, a 64 KB body cap, and `.txt`-only enforcement on uploads as basic robustness. These are not "defenses" in the course sense; the `LEVEL` filter is.
- `test_lab.py` imports `app` to test `run_tools`, `env_flag`, and the `LEVEL 2` filter deterministically, and hits the live server for the smoke checks. It never asserts an injection succeeds (models are non-deterministic).
- Verified end to end against a stub Ollama server: all 7 tests pass, `/summarize` swaps the tool call for Flag 2, `/chat` does not run tools, non-`.txt` and oversize uploads and bad JSON are rejected, `LEVEL=2` blocks filtered words.

## Phase 3: AIRT101 challenge
- `check_flag.py` is stdlib only and compares SHA-256 of the input against the two stored hashes, naming which flag passed. Verified both real flags print PASS and a wrong flag prints FAIL.
- Challenge README states the scenario, two objectives mapped to ATLAS/OWASP, rules (including "do not decode `.env.example`"), a harder `LEVEL=2` mode, and three progressive hints per flag in `<details>` blocks.

## Phase 4: AIRT101 notes
- Wrote the six lessons as descriptively-named files (`01-how-llm-apps-are-built.md` ... `06-reporting.md`), each in the required format, 400-1200 words, each "Try it in the lab" pointing at a concrete action against HelpBot.

## Publish
- Shipped as a single monorepo (`orgito1015/Gitoversity`) rather than one repo per folder. `CLAUDE.md` and the build zip are kept out of the repo via a top-level `.gitignore` and by not copying them in.
- Added a root `README.md` as the repo landing page, since `.github/profile/README.md` only renders as a profile for a dedicated org `.github` repo, not for this monorepo.

## Phase 6: Website (built early, on owner request)
- Spec gates this behind "3 courses passed"; built now because the owner asked. Deviation noted here.
- `docs/build.py` (stdlib only) parses `catalog/README.md` and `catalog/TRANSCRIPT.md` and writes a self-contained `docs/index.html` (inline CSS, no Jekyll, no dependencies). Status words render as colored badges; `[label](url)` cells become links; the empty transcript placeholder row is dropped.
- Serve by enabling GitHub Pages on branch `main`, folder `/docs`. Regenerate after editing the catalog with `python3 docs/build.py`.
- Skipped a GitHub Actions auto-deploy workflow (the catalog changes rarely); add one if manual regeneration becomes a chore.

## WEB101 (second course, on owner request)
- Built WEB101 "HTTP, Recon and the OWASP Top 10" to the full course standard: README, six notes, lab, challenge, writeup template.
- Lab is "NorthWind Notes", a stdlib-only `http.server` app (no DB, no framework, no model), so `docker compose` is a single service and it also runs directly with `python3 app.py`.
- Two flags: Flag 1 = broken access control / IDOR on `GET /note?id=N` (OWASP A01); Flag 2 = information disclosure at `/internal/config`, discovered via `robots.txt` (OWASP A05). Flags base64-encoded in `.env.example`, SHA-256 in `check_flag.py`.
- `LEVEL=2` applies real fixes (ownership check, output escaping, security headers) so the defenses lesson has a before/after. Also a no-flag reflected XSS on `/search?q=` for the injection lesson (A03).
- Verified: both flags reachable by intended attacks at LEVEL 1, both blocked at LEVEL 2, XSS escaped at LEVEL 2, `test_lab.py` 6/6 pass, `check_flag.py` PASS/FAIL correct, no plaintext flags, no em dashes.
- Updated catalog and the Pages site (now 2 available courses).
