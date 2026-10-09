# Challenge: Map and break NorthWind Notes

## Scenario

NorthWind Lab, a fictional smart home company, runs an internal note-taking app called NorthWind Notes. They gave you one low-privilege account (`alice` / `password123`) and asked for a quick assessment before launch.

Two secrets are hidden in the running app. One belongs to another user. The other was never meant to be reachable at all. Find both by behaving like an attacker who only has alice's account and a browser.

## Objectives

| Flag | Goal | Class |
|------|------|-------|
| Flag 1 | Read a note that does not belong to you. | Broken Access Control / IDOR, [OWASP A01:2021](https://owasp.org/Top10/A01_2021-Broken_Access_Control/), MITRE ATT&CK [T1190](https://attack.mitre.org/techniques/T1190/) |
| Flag 2 | Find an endpoint the developers tried to hide, and read what it leaks. | Security Misconfiguration / Information Disclosure, [OWASP A05:2021](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/) |

Both flags have the format `GITO{...}`.

## Rules

- Attack only your local lab at `http://127.0.0.1:8080`.
- Log in as `alice`. Do not try to log in as `admin`; you are not meant to have those credentials.
- Do not read `lab/.env`, decode `.env.example`, or read the flags out of `lab/app.py` to get them. Black box first.
- Keep notes of every request and response. You will need them for your writeup.

## Verify a flag

```
python3 check_flag.py 'GITO{...}'
```

It prints `PASS: Flag 1 ...`, `PASS: Flag 2 ...` or `FAIL`.

## Harder mode

Set `LEVEL=2` in `lab/.env` and restart. The developers have now applied fixes: access control on notes, output escaping, and security headers. Confirm that both of your original attacks stop working, and explain in your writeup exactly which fix stopped which attack. (There is also a reflected XSS on the search box at `LEVEL=1` that carries no flag. Find it, and confirm `LEVEL=2` escapes it.)

## Hints

Try for at least 30 minutes before opening a hint.

<details>
<summary>Flag 1, hint 1</summary>

Open one of your own notes and look closely at the URL. What identifies the note?

</details>

<details>
<summary>Flag 1, hint 2</summary>

The note is selected by a number in the URL. You own some of those numbers. What happens if you ask for one you do not own? The app never checks whether the note is yours (at `LEVEL=1`).

</details>

<details>
<summary>Flag 2, hint 1</summary>

Before attacking an app you map it. There are well-known files a web server often exposes that tell you about paths the site does not link to. One of them is named after what it tells robots to do.

</details>

<details>
<summary>Flag 2, hint 2</summary>

`GET /robots.txt`. It disallows a path. "Disallowed" is not "protected": request what is under that path directly. Look for a config or status endpoint there.

</details>

## After you solve it

Write `../writeup/README.md` using the template there, then ship one output (see the course README). Never publish the flag values.
