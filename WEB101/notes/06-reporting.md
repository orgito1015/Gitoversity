# 06: Reporting: severity, reproducibility, evidence
Time: ~30 min
Mapping: OWASP A01/A03/A05, MITRE ATT&CK T1190

## Why it matters

Finding a bug is half the job. The report is the deliverable, the thing a developer reads and acts on, and the thing that gets a bug bounty paid or rejected. A web finding that is clearly reproduced, correctly rated, and tied to a concrete fix gets taken seriously. One that says "I think there might be an IDOR somewhere" gets ignored. This lesson turns the two flags you captured into write-ups a client would accept, and it is the course deliverable: your `writeup/README.md`.

## How it works

Unlike the LLM bugs in AIRT101, web bugs like these are deterministic: the IDOR returns admin's note every time, and the config endpoint leaks every time. That makes reproduction easy, so there is no excuse for a vague report. A good web finding answers four questions.

**1. Severity, argued from impact and likelihood.** Do not just stamp "High". Reason it:

- *Impact*: what does the attacker get or do? Flag 1 is unauthorized read of another user's data by any logged-in user. Say whether it scales (can you read *every* note by walking ids?) and whether it extends to writes (could you modify admin's note?), because those change the rating. Flag 2 is disclosure of an internal API key with no authentication at all, which is worse: no account is even required.
- *Likelihood*: who can trigger it and how hard? Flag 1 needs only a normal account and editing a URL. Flag 2 needs only to read `robots.txt` and request a path. Both are trivial.
- Give a rating and, ideally, a CVSS vector so the reader can map it to their process. Broken access control that exposes other users' data is typically High; an unauthenticated secret leak can be High to Critical depending on what the key unlocks.

**2. Reproducibility: exact, copy-pasteable steps.** For a web bug this is just the precise requests:

- Pin the environment: the app, the `LEVEL`, the account used, the date/commit.
- Give the literal request. For Flag 1: "Logged in as alice, send `GET /note?id=2` with alice's session cookie. Response 200 contains admin's note." Include the `curl` line. No paraphrase.
- State the starting privilege clearly (you are a low-privilege user, not admin). That is what makes it a vulnerability rather than intended access.

**3. Evidence, with the secret redacted.** Show the response that proves the leak, but mask the flag value itself (`GITO{...}` or a black bar). A screenshot or a copied response both work; label what the reader is looking at and highlight the status code and the leaked field. Never commit a real flag to your writeup; the course rule is `git grep -i "GITO{"` returns nothing but hashes and placeholders.

**4. Remediation, specific and testable.** Name the fix for *this* bug and how to confirm it:

- Flag 1: "Before returning a note, verify it belongs to the authenticated user (or that their role allows access). Verify by repeating `GET /note?id=2` as alice and confirming `403`." This is exactly what `LEVEL=2` does, so you can demonstrate the fixed behaviour.
- Flag 2: "Require authentication and authorization on `/internal/*`, or remove it from the production build; disable `debug`. Verify by requesting `/internal/config` unauthenticated and confirming it is refused."

Tie each finding to its framework ID (OWASP A01 for the IDOR, A05 for the disclosure, A03 for the XSS) so the reader can slot it into their own risk tracking.

### Structure to reuse

```
Title: impact-first ("Any user can read other users' private notes via IDOR on /note")
Summary: one paragraph for a manager
Severity: rating + impact + likelihood + reasoning (CVSS vector if you can)
Affected: endpoint, account used, LEVEL, version/commit, date
Steps to reproduce: numbered, with the exact request(s)
Evidence: response excerpt with the secret redacted, status code highlighted
Remediation: the specific fix and how to test it
Mapping: OWASP / ATT&CK IDs
```

The `writeup/README.md` template in this repo follows this shape. Fill it in for both flags and the bonus XSS.

## Try it in the lab

1. For each flag, assemble the exact `curl` request and the response that proves it, with the flag value redacted.
2. For Flag 1, test and report whether it scales (walk `id=1..N`) and whether it affects writes. That detail sets the severity.
3. Write both findings into `writeup/README.md` using the structure above, plus a short note on the search-box XSS and what `LEVEL=2` changed.
4. Run `git grep -i "GITO{"` in the repo and confirm only hashes and the `GITO{...}` placeholder appear, never a real flag.
5. Ship one output and link it in the course README: your public writeup, a small IDOR/recon testing script, or a new vulnerable endpoint added to the lab.

## Key takeaways

- The report is the deliverable; web bugs are deterministic, so vagueness is inexcusable, give exact requests.
- Argue severity from impact (does it scale? does it allow writes? is auth even needed?) and likelihood, with a CVSS vector where you can.
- Reproduce with pinned environment, starting privilege, and literal requests; prove with a redacted response excerpt.
- Remediation must be specific to the bug and come with a test; map every finding to OWASP and ATT&CK IDs.
- Never commit a real flag; `git grep` must come back clean.

## Further reading

- OWASP Web Security Testing Guide, Reporting: https://owasp.org/www-project-web-security-testing-guide/
- FIRST CVSS v3.1 specification: https://www.first.org/cvss/v3-1/specification-document
- OWASP Top 10 (2021), index of categories: https://owasp.org/Top10/
