# 02: Recon: mapping an app before you attack it
Time: ~30 min
Mapping: MITRE ATT&CK T1083 (File and Directory Discovery), T1595 (Active Scanning)

## Why it matters

Attackers do not start by firing payloads. They start by building a map: what pages exist, what technology runs them, what the app expects, and what it accidentally reveals. Most of the time the map itself contains the bug. Flag 2 in this lab is pure recon: nothing is "exploited" in the clever sense, you simply find a door the developers forgot was unlocked. The skill that finds it, reading what an app discloses about itself, is the one that pays off most often on real targets.

## How it works

Recon on a single web app has a few reliable moves. Do them in roughly this order.

**1. Read every response header.** Headers leak the stack. NorthWind sends `Server: NorthWindNotes/1.0 (Python)`, which tells you it is a custom Python app, not a known framework, so you will look for hand-rolled mistakes rather than CVEs. Missing headers matter too: no `Content-Security-Policy` or `X-Content-Type-Options` hints the developer was not thinking about client-side defenses, which makes the XSS in Lesson 04 more likely to be real. Fingerprinting the technology (T1592/T1595) decides what you look for next.

**2. Ask for the well-known files.** Web servers and conventions expose files that are not linked from any page:

- `robots.txt` tells search engines which paths to skip. It is not a security control; it is a *list of paths the owner cares about enough to hide*, handed straight to you. Disallowed is not protected.
- `sitemap.xml`, `/.well-known/`, `security.txt`, `/favicon.ico` (can fingerprint a framework), and backup or dotfiles (`.git/`, `.env`, `*.bak`) are all worth a request.

**3. Enumerate paths.** Walk the links the app does show, then guess the ones it does not: `/admin`, `/api`, `/debug`, `/internal`, `/config`, `/backup`, `/status`, `/health`. On real targets this is automated with a wordlist (tools like ffuf or gobuster) against a `404` baseline, but the thinking is the same: try names a developer would plausibly have used, and watch the status codes. A `200` or `403` where you expected `404` is a live path.

**4. Understand the app's own vocabulary.** Click through the real features and note every parameter: `id`, `q`, `page`, `file`, `user`. Each parameter is an input you can tamper with later. Note which ones look like database keys (`id=1`), because those are the IDOR candidates for Lesson 03.

**5. Map auth boundaries.** Which pages work logged out, which need the cookie, which mention an `admin`. The gap between "what the app shows alice" and "what the app will actually serve alice if asked directly" is where broken access control lives.

The mindset: the app is constantly telling you about itself through headers, error messages, status codes, and conventional files. Recon is listening carefully before you speak. A good map turns the rest of a test from guessing into checking a list.

A word on scope and noise: recon is active, it sends requests and shows up in logs. On a real engagement you stay inside the authorized scope and keep the request volume sane. Here, the whole lab is yours and local, so enumerate freely.

## Try it in the lab

1. Fingerprint it:
   ```
   curl -I http://127.0.0.1:8080/
   ```
   Note the `Server` header and which security headers are absent (at `LEVEL=1`).
2. Pull the well-known file that lists hidden paths:
   ```
   curl http://127.0.0.1:8080/robots.txt
   ```
   Read what it disallows. That is a path the developer wanted hidden.
3. Request what is under that path directly. Try an obvious config or status name beneath it. When you get JSON back, you have found Flag 2's home.
4. List the parameters you have seen so far across the app (`id` on notes, `q` on search). Write them down; Lessons 03 and 04 attack exactly those.

## Key takeaways

- Recon comes before exploitation; the map often contains the bug.
- Response headers fingerprint the stack and reveal missing defenses; read them on every request.
- `robots.txt` and other well-known files hand you paths that are hidden but not protected.
- Enumerate paths by trying names a developer would use, and watch status codes against a `404` baseline.
- Catalogue every parameter and every auth boundary; those are your tampering targets in later lessons.

## Further reading

- OWASP Web Security Testing Guide, Information Gathering: https://owasp.org/www-project-web-security-testing-guide/stable/4-Web_Application_Security_Testing/01-Information_Gathering/
- Google, robots.txt specification: https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt
- MITRE ATT&CK T1083, File and Directory Discovery: https://attack.mitre.org/techniques/T1083/
