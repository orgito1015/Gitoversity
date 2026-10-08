# Gitoversity

An open university for offensive security. Learn by building, prove it by shipping.

Website: https://orgito1015.github.io/Gitoversity/ (enable GitHub Pages on branch `main`, folder `/docs`).

## How it works

- Every course is a folder with four parts: `notes/`, `lab/`, `challenge/`, `writeup/`.
- A course is passed only when something real is shipped: a tool, a new challenge, or a public writeup.
- Every course is mapped to MITRE ATT&CK, or MITRE ATLAS and the OWASP Top 10 for LLM Applications for AI courses.
- Free and open. Labs run locally and are never exposed to the internet.

## Start here

1. Read the [catalog](catalog/README.md) to see the faculties and courses.
2. Pick a course and open its folder.
3. Run the lab, solve the challenge, write your own `writeup/README.md`.
4. Add the course to the [transcript](catalog/TRANSCRIPT.md).

New courses start from [`course-template/`](course-template/README.md).

## Courses

| Code | Title | Status |
|------|-------|--------|
| [AIRT101](AIRT101/README.md) | Prompt Injection and Jailbreak Fundamentals | built, awaiting pass |

The full roadmap across all faculties (WEB, NET, PWN, CLD, AIRT, OPS) is in the [catalog](catalog/README.md).

## Faculties

| Code | Faculty |
|------|---------|
| WEB  | Web Application Security |
| NET  | Network and Active Directory |
| PWN  | Binary Exploitation and Reversing |
| CLD  | Cloud Security |
| AIRT | AI Red Teaming |
| OPS  | Red Team Operations |

## Rules

Everything here is for authorized testing and education only. Labs run locally, bound to `127.0.0.1`. Never use these techniques against systems you do not own or have written permission to test.

## License

Code is MIT. Written course content is CC BY 4.0. See each course's `LICENSE`.
