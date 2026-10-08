# 06: Reporting: severity, reproducibility, evidence
Time: ~30 min
Mapping: MITRE ATLAS AML.T0051, OWASP LLM01

## Why it matters

A finding nobody can reproduce and nobody acts on is worth nothing. The report is the product. For LLM findings this is harder than for a normal web bug, because the target is non-deterministic: your exploit worked three times out of ten, and a reader who runs it once and sees a refusal will dismiss you. This lesson is how to write up the two flags you just captured so a developer believes them, understands the impact, and knows what to fix. It is also the course's deliverable: your `writeup/README.md`.

## How it works

A good finding answers four questions: what is broken, how badly, how do I see it myself, and what do I do about it.

**1. Severity, argued not asserted.** Rate impact and likelihood, and justify both.

- *Impact*: what does the attacker get? Flag 1 is disclosure of an internal escalation code to any customer. Flag 2 is disclosure of an internal support key with no authentication, triggered by a document the victim did not know was hostile. State what that secret would let a real attacker do next.
- *Likelihood*: who can trigger it and how hard is it? Flag 1 needs only the chat box and a few tries. Flag 2 needs the victim to summarize an attacker-supplied document, which is realistic for a support tool.
- Give a rating (for example Low/Medium/High/Critical, or a CVSS-style vector) and show your reasoning. For LLM bugs, note the non-determinism explicitly: a 30% success rate is still a High if the payoff is a credential, because the attacker just retries.

**2. Reproducibility, made deterministic enough.** This is the part people get wrong with AI bugs. You cannot promise one-shot success, so you report honestly and make it as repeatable as possible:

- Pin the environment: model tag, `LEVEL`, app version or commit, date.
- Give the exact prompt or the exact document, verbatim, in a code block. Not a paraphrase.
- Report a success rate: "succeeded on 4 of 10 attempts with the prompt below." That number is data, not an excuse.
- Give the reader the retry instruction: "run it up to ten times; it is probabilistic."

**3. Evidence, with the secret redacted.** Show the model's response that contains the leak, but mask the flag itself: `GITO{...}` or a black bar. You prove the leak happened without publishing the secret. Screenshot or copied text both work; label what the reader is looking at. Never commit a real flag to the writeup (the course rule and `git grep "GITO{"` will catch you).

**4. Remediation, specific and testable.** Do not write "add input validation". Write the fix for *this* bug and how to verify it:

- Flag 1: "Remove the escalation code from the system prompt; fetch it from a store behind an access check only when an authenticated agent requests it. Verify by re-running the Flag 1 attack set and confirming the code is never in context."
- Flag 2: "Gate `get_secret()` on the requesting user's authorisation in the application, before the tool runs; do not trigger it from model output alone. Verify by re-running the document attack set as an unauthenticated user and confirming zero leaks."

Tie each finding to a framework ID (MITRE ATLAS AML.T0051 and its sub-techniques, OWASP LLM01) so the reader can map it to their own risk register.

### Structure to reuse

```
Title: short, impact-first ("Unauthenticated disclosure of internal support key via document summarizer")
Summary: one paragraph a manager can read
Severity: rating + impact + likelihood + reasoning
Affected: endpoint, model, LEVEL, version/commit, date
Steps to reproduce: numbered, with the verbatim prompt/document and the success rate
Evidence: response excerpt with the flag redacted
Remediation: the specific fix and how to test it
Mapping: ATLAS / OWASP IDs
```

The `writeup/README.md` template in this repo follows this shape. Fill it in for both flags.

## Try it in the lab

1. Take the notes you kept while solving. For each flag, assemble the verbatim payload and your success rate.
2. Capture one evidence excerpt per flag and redact the flag value.
3. Write both findings into `writeup/README.md` using the structure above. Argue each severity; do not just label it.
4. Check the rule: run `git grep -i "GITO{"` in your repo and confirm it returns nothing but hashes and the `GITO{...}` placeholder. If a real flag shows up, remove it.
5. Ship one output and link it in the course README: your public writeup, a small automated injection-test harness (Lesson 05), or a new poisoned-document challenge for the lab.

## Key takeaways

- The report is the deliverable; an unreproducible or unactionable finding has no value.
- Argue severity from impact and likelihood, and state the non-deterministic success rate instead of hiding it.
- Make it reproducible: pin model/LEVEL/version, give verbatim payloads, report a hit rate, tell the reader to retry.
- Redact the secret in evidence; never commit a real flag.
- Remediation must be specific to the bug and come with a way to test the fix; map every finding to ATLAS and OWASP IDs.

## Further reading

- OWASP LLM01 Prompt Injection (impact and mitigation framing): https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- MITRE ATLAS case studies (how real AI incidents are written up): https://atlas.mitre.org/studies
- FIRST CVSS v3.1 specification (a vocabulary for severity): https://www.first.org/cvss/v3-1/specification-document
