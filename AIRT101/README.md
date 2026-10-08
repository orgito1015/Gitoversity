# AIRT101: Prompt Injection and Jailbreak Fundamentals

**Faculty:** AI Red Teaming  **Level:** 1xx  **Prerequisites:** basic Python, HTTP
**Framework mapping:** MITRE ATLAS (LLM Prompt Injection, LLM Jailbreak), OWASP Top 10 for LLM Applications (LLM01)

## Objectives
- Explain how system prompts, user input and retrieved content share one context window.
- Perform direct and indirect prompt injection against a local target.
- Write adversarial test cases and score them consistently.
- Document a finding the way a client report expects it.

## Lessons (`notes/`)
1. How LLM applications are built: system prompt, context, tools
2. Direct prompt injection
3. Indirect injection through documents and web content
4. Jailbreak families and why they work
5. Defenses and how to test them
6. Reporting: severity, reproducibility, evidence

## Lab (`lab/`)
A local chatbot with a secret in its system prompt and one document-reading feature. Runs against a local model, no external API needed.

## Challenge (`challenge/`)
Extract the flag from the system prompt, then extract it again through a poisoned document without typing the injection into the chat.

## Pass condition
Ship one of: a public writeup of both solves, a small injection test harness, or a new challenge for the lab.

## Rules
Authorized testing and education only. Run labs locally.
