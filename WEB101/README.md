# WEB101: HTTP, Recon and the OWASP Top 10

**Faculty:** Web Application Security  **Level:** 1xx  **Prerequisites:** basic Python, how to use a browser and curl
**Framework mapping:** OWASP Top 10 (A01 Broken Access Control, A03 Injection, A05 Security Misconfiguration), MITRE ATT&CK (T1190 Exploit Public-Facing Application, T1083 File and Directory Discovery)

## Objectives
- Read and send raw HTTP: methods, status codes, headers, cookies.
- Map an unknown web app the way an attacker does, before touching a single exploit.
- Find and exploit a broken access control bug (IDOR) and an information-disclosure endpoint.
- Recognise reflected XSS and explain why output encoding stops it.
- Document a finding the way a client report expects it.

## Lessons (`notes/`)
1. How the web works: HTTP requests, responses, methods and status codes
2. Recon: mapping an app before you attack it
3. Broken access control and IDOR (A01)
4. Injection and reflected XSS (A03)
5. Security misconfiguration and information disclosure (A05)
6. Reporting: severity, reproducibility, evidence

## Lab (`lab/`)
NorthWind Notes, a small deliberately vulnerable note-taking app. You get one low-privilege account. Runs locally, standard library only, no external services.

## Challenge (`challenge/`)
Starting from one normal user account, read a note that is not yours (Flag 1), then find an endpoint the developers tried to hide and read what it leaks (Flag 2).

## Pass condition
Ship one of: a public writeup of both solves, a small recon or IDOR-testing script, or a new vulnerable endpoint added to the lab as a challenge.

## Rules
Authorized testing and education only. Run labs locally.

## License
Code is MIT. Written content (notes and writeup) is CC BY 4.0. See `LICENSE`.
