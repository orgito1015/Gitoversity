# 05: Security misconfiguration and information disclosure (A05)
Time: ~30 min
Mapping: OWASP A05:2021 Security Misconfiguration, MITRE ATT&CK T1083

## Why it matters

Not every bug is a clever exploit. A huge share of real breaches start with something left switched on, left exposed, or left too verbose: a debug endpoint in production, a directory listing, a stack trace that prints a database password, default credentials, a backup file served as plain text. This is security misconfiguration, and it is where recon (Lesson 02) turns into a finding. Flag 2 in this lab is exactly this: an internal config endpoint with no authentication, reachable once you know the path. It is worth understanding on its own because it is so common and so cheap to exploit.

## How it works

Misconfiguration is a broad family. The thread connecting it is that the vulnerability is in how the app or server was *set up*, not in the application logic. The common cases:

- **Exposed internal endpoints.** Debug consoles, health and status pages, admin panels, metrics, and "internal" APIs that were meant for the ops team but are reachable by anyone who finds the URL. NorthWind has `/internal/config`, which returns a JSON blob including an `internal_api_key` (Flag 2) and `debug: true`. Nothing stops you reading it; it simply assumed nobody would find it.

- **Security by obscurity.** Hiding a path instead of protecting it. NorthWind's `robots.txt` even advertises the path. "Hard to find" is not "access controlled". The fix is authentication and authorization on the endpoint, not a secret URL.

- **Verbose errors and debug mode.** Stack traces, framework version banners, and `debug=true` hand attackers a map of the internals: file paths, library versions, sometimes credentials or tokens in the error text. Production should return generic errors and never run in debug mode.

- **Information disclosure through responses.** Over-sharing in normal responses: a user object that includes a password hash, an API that returns more fields than the UI shows, comments in HTML, or source maps that reveal client code. Always read the *full* response, not just what the UI renders.

- **Missing security headers.** No `Content-Security-Policy`, no `X-Content-Type-Options`, no HSTS. Each absence makes another attack easier (the XSS in Lesson 04 is worse without CSP). At `LEVEL=2` NorthWind adds these headers.

- **Defaults left in place.** Default admin passwords, sample apps, open cloud storage buckets, directory listing enabled. These are found by convention: try the defaults, try the common paths.

Why it keeps happening: configuration drifts. A debug endpoint is added for a staging environment and ships to production. A header is forgotten. An ops tool is bound to all interfaces instead of localhost. None of it shows up in a feature demo, so it survives until someone looks. Your job as a tester is to look: enumerate, read every header and every full response body, and try the conventional names.

Impact ranges widely. A leaked version banner is low on its own but feeds other attacks. A leaked API key or credential is high to critical, because it is often a direct path to data or to other systems. When you report a disclosure, state not just what leaked but what an attacker does with it next.

The fixes are mostly about posture: authenticate internal endpoints, turn off debug in production, return generic errors, send security headers, change defaults, and bind internal services to localhost. NorthWind's `LEVEL=2` adds headers; a real fix for Flag 2 would also put `/internal/` behind authentication or remove it from the production build entirely.

## Try it in the lab

1. From Lesson 02 you found `/internal/` in `robots.txt`. Request the config endpoint under it:
   ```
   curl http://127.0.0.1:8080/internal/config
   ```
   Read the whole JSON. Note `debug: true` and the `internal_api_key` (Flag 2). Verify the flag with `check_flag.py`.
2. Confirm it needs no session: send the same request with no cookie at all. It still works. That is the bug: no authentication on an internal endpoint.
3. Compare headers between `LEVEL=1` and `LEVEL=2`:
   ```
   curl -I http://127.0.0.1:8080/
   ```
   Note which security headers appear only at `LEVEL=2`.
4. For your writeup, describe what an attacker does with a leaked internal API key, not just that it leaked.

## Key takeaways

- Misconfiguration is a setup flaw, not a logic flaw: exposed endpoints, debug mode, verbose errors, missing headers, defaults.
- Hiding a path is not protecting it; the only real fix is authentication and authorization on the endpoint.
- Read full response bodies and all headers: disclosure often hides in fields the UI never shows.
- Rate impact by what the leaked thing enables next; a leaked key or credential is often a direct path deeper.
- Fixes are about posture: authenticate internals, disable debug, generic errors, security headers, change defaults, bind to localhost.

## Further reading

- OWASP Top 10 A05:2021, Security Misconfiguration: https://owasp.org/Top10/A05_2021-Security_Misconfiguration/
- OWASP WSTG, Testing for Error Handling and configuration: https://owasp.org/www-project-web-security-testing-guide/stable/4-Web_Application_Security_Testing/08-Testing_for_Error_Handling/
- Mozilla Observatory (security header posture): https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
