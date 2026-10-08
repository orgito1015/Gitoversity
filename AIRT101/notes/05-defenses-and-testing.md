# 05: Defenses and how to test them
Time: ~35 min
Mapping: MITRE ATLAS AML.M0020 (Generative AI Guardrails), OWASP LLM01

## Why it matters

A red teamer who only breaks things is half-trained. The value you deliver is telling the developer what to change and then proving the change works or does not. Most proposed defenses for prompt injection are partial, and some give false comfort. You need to know which is which, and you need a way to measure a defense instead of eyeballing it. This lesson turns the lab's `LEVEL` switch into a lesson about why the easy defense fails and what actually helps.

## How it works

Start with the defense in the lab. `LEVEL=2` adds a keyword filter on the chat input: it blocks messages containing words like "ignore", "system prompt", or "escalation code". This is the single most common first attempt at defending an LLM app, and it is close to useless on its own:

- It is a denylist, so it only catches the exact words someone thought of. Synonyms, typos, spacing, other languages, and encodings all walk past it (Lesson 04).
- It inspects the input, but injection can succeed without any banned word. You can extract a secret by asking for a "repeat" or a "translation" with entirely innocent vocabulary.
- Crucially, it protects only the chat path. Flag 2 arrives in a document, which the filter never touches. A filter in the wrong place is not a weak defense, it is no defense.

Now the defenses that actually move the needle, roughly in order of value:

1. **Do not put secrets in the prompt.** Flag 1 is extractable only because it is in the system prompt at all. If the escalation code lived in a database behind an access check and was never placed in the model's context, no injection could reach it. The strongest fix is to remove the asset from the blast radius.

2. **Constrain what tools can do, not whether the model calls them.** Flag 2 leaks because `get_secret()` returns a secret to anyone whose document triggers it. Treat every tool call as if the attacker made it: enforce authorisation in the application, on the user's identity, before the tool runs, and never gate a sensitive tool on model output alone.

3. **Separate data from instructions as much as the platform allows.** Clearly delimit untrusted content, mark it as data, and (on capable models) instruct the model to treat anything inside those bounds as text to be processed, never obeyed. This raises the bar but does not close the hole: the model can still be convinced, so it is defence in depth, not a guarantee.

4. **Filter output and actions, not just input.** Scan responses for the secret's format before returning them. Rate-limit and log tool calls. Require a human step for high-impact actions. These catch cases the input filter misses.

5. **Least privilege and isolation everywhere.** Minimum tool scope, minimum data in context, local network only (HelpBot binds to 127.0.0.1 and never publishes the model port). If a bug fires, it should reach as little as possible.

The honest summary: there is no known complete fix for prompt injection today. You stack partial controls and you reduce impact. That is the message to put in a report, not "add an input filter and you're safe".

### How to test a defense

Testing is where red teamers earn trust. The method:

- **Build a fixed attack set.** Collect the prompts and documents that worked, plus variations. Keep them in a file so every run uses the same inputs.
- **Measure a success rate, not a yes/no.** Because models are non-deterministic (Lesson 02), run each attack N times and record how many succeed. "Blocks 10/10 of the DAN variant but 3/10 of the translation variant" is a finding; "it's filtered" is not.
- **Test every path.** Run the set against `/chat` and `/summarize`, at `LEVEL=1` and `LEVEL=2`, and across models. A defense that only helps one path or one model should be reported that way.
- **Test the defense's own failure mode.** Does the filter block legitimate users? A support bot that refuses the word "instructions" in a normal question has a usability bug. Note false positives too.
- **Re-test after the fix.** Re-run the exact same set. The only proof a fix works is the attack set dropping to a success rate you can live with.

This is what `test_lab.py` is a seed of. It checks the mechanics deterministically (the tool swap, the filter) and leaves the probabilistic attack scoring to you. Building a small harness that automates "send attack set N times, report hit rate per model and level" is one of the shippable outputs that passes this course.

## Try it in the lab

1. Get Flag 1 at `LEVEL=1`, then at `LEVEL=2`. Write down which prompts the filter stopped and which still worked.
2. Confirm the filter is on the wrong path: get Flag 2 at `LEVEL=2`. It should be exactly as easy as at `LEVEL=1`, because the document path has no filter.
3. Pick five of your best attacks. Run each ten times at each level. Record a table of hit rates. That table is your test result.
4. Design a better defense on paper for Flag 2 specifically (hint: authorisation on the tool). Describe how you would test it, then, if you want the deeper exercise, edit `app.py` to add it and re-run your attack set.

## Key takeaways

- Input keyword filters are denylists in the wrong place: they miss innocent-word attacks and never see the document path. Do not sell them as a fix.
- The real fixes reduce blast radius: keep secrets out of the prompt, authorise tool calls on the user before they run, apply least privilege, and filter outputs and actions.
- No complete defense against prompt injection exists today; you stack partial controls and reduce impact.
- Test defenses with a fixed attack set, a success rate over many runs, every path and model, and a re-test after the fix. Measure, do not eyeball.

## Further reading

- MITRE ATLAS mitigation, Generative AI Guardrails (AML.M0020): https://atlas.mitre.org/mitigations/AML.M0020
- OWASP GenAI, LLM01 Prompt Injection prevention section: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- NIST AI 100-2, Adversarial Machine Learning taxonomy: https://csrc.nist.gov/pubs/ai/100/2/e2023/final
