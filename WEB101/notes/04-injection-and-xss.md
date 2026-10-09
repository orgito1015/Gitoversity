# 04: Injection and reflected XSS (A03)
Time: ~35 min
Mapping: OWASP A03:2021 Injection, MITRE ATT&CK T1059 (Command and Scripting Interpreter, client-side analogue)

## Why it matters

Injection is what happens when data you send gets treated as code. SQL injection, command injection and cross-site scripting (XSS) are all the same mistake in different places: the app built a program (a query, a shell command, an HTML page) by pasting untrusted input straight into it, and your input broke out of the "data" slot into the "code" slot. XSS is the version that runs in other users' browsers, and it is the injection you are most likely to meet on a modern web app. NorthWind's search box has a reflected XSS so you can see the mechanism directly.

## How it works

NorthWind's search page echoes what you searched for: "You searched for: `<your text>`". At `LEVEL=1` it pastes your text into the HTML without changing it. HTML does not have a wall between text and markup, so if your text *is* markup, the browser treats it as markup.

Send `q=<b>hi</b>` and the page shows a bold "hi": your tags became real tags. Now send a `<script>` tag instead, and the browser runs it as JavaScript, in the context of that page, with access to that page's cookies and DOM. That is XSS. The classic proof is:

```
/search?q=<script>alert(document.domain)</script>
```

If an alert box pops, arbitrary script ran. In a real attack the script would not pop an alert; it would steal the session cookie, make requests as the victim, or rewrite the page to phish them.

This is **reflected** XSS: the payload is in the request and is reflected straight back in the response, so the attack is to get a victim to open a link you crafted. The two other families, for your vocabulary:

- **Stored XSS**: the payload is saved by the app (a comment, a profile name, a note title) and served to every viewer later. More dangerous, because no link is needed and it can hit many users.
- **DOM XSS**: the unsafe join happens in client-side JavaScript, not the server.

The root cause is always the same: **output rendered in a context without encoding for that context.** The fix is contextual output encoding. When the app puts user data into HTML, it must convert the characters that mean something in HTML (`<`, `>`, `&`, `"`) into their harmless entity forms (`&lt;`, `&gt;`, and so on). Then `<script>` arrives at the browser as the literal text "`<script>`" and is shown, not executed. At `LEVEL=2` NorthWind does exactly this with an HTML-escape on the search term, and the same payload becomes inert text. A second layer, a `Content-Security-Policy` header, is also added at `LEVEL=2` and would block inline script even if an encoding bug slipped through; defense in depth.

The same "data became code" lens applies to the server-side injections you will meet in later courses:

- **SQL injection**: input pasted into a SQL string, so `' OR 1=1 --` changes the query's logic. Fixed with parameterised queries, never string concatenation.
- **Command injection**: input pasted into a shell command, so `; rm -rf` runs. Fixed by not building shell strings from input.

NorthWind is intentionally a no-database, no-shell app, so it has no SQL or command injection to find. The reflected XSS is here to teach the pattern; recognising "my input came back inside the program" is the transferable skill.

A note on testing XSS safely: prove it with a harmless marker (`<b>`, or `alert(document.domain)`), capture the evidence, and stop. Do not run real cookie-stealing payloads against anything but your own lab, and never against other users.

## Try it in the lab

1. At `LEVEL=1`, search for `<b>hello</b>` (type it in the box, or `curl 'http://127.0.0.1:8080/search?q=<b>hello</b>'`). The word is bold: your tags were interpreted.
2. Prove script execution in the browser by visiting:
   ```
   http://127.0.0.1:8080/search?q=<script>alert(document.domain)</script>
   ```
   An alert confirms arbitrary JavaScript ran in the page.
3. Look at the raw response and find your payload sitting unescaped in the HTML. That is the bug, visible in one line.
4. Switch to `LEVEL=2`, restart, and repeat. The response now contains `&lt;script&gt;`, shown as text, not executed. Note the new `Content-Security-Policy` header too. Record both for your writeup. (This bug carries no flag; it is practice for the real thing.)

## Key takeaways

- Injection is untrusted input being treated as code; XSS is the browser-side case where your input becomes live HTML/JavaScript.
- Reflected XSS echoes your request back unencoded; stored XSS is saved and served to others; DOM XSS happens in client JS.
- The root cause is output without contextual encoding; the fix is to HTML-encode data when it is placed into HTML (seen at `LEVEL=2`).
- The same "data became code" pattern explains SQL and command injection, fixed by parameterisation and by not building commands from input.
- Prove XSS with a harmless marker and stop; never run real payloads outside your own lab.

## Further reading

- OWASP Top 10 A03:2021, Injection: https://owasp.org/Top10/A03_2021-Injection/
- OWASP Cross Site Scripting Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- PortSwigger Web Security Academy, Cross-site scripting: https://portswigger.net/web-security/cross-site-scripting
