# 01: How the web works: HTTP requests, responses, methods and status codes
Time: ~30 min
Mapping: MITRE ATT&CK T1190 (Exploit Public-Facing Application)

## Why it matters

Every web attack is a specially crafted HTTP request. Before you can bend a request to do something the developer did not intend, you have to see requests clearly: what parts they have, which parts you control, and how the server answers. People who skip this stage guess at payloads and cannot tell a real finding from noise. Spend the half hour here and the rest of the course is you changing one part of a request and reading what comes back.

NorthWind Notes, the lab for this course, is small enough that you can watch every byte go over the wire. That is the point.

## How it works

HTTP is a text protocol. A client sends a request, the server sends a response, and then (for classic HTTP) they are done. A request looks like this:

```
GET /note?id=1 HTTP/1.1
Host: 127.0.0.1:8080
Cookie: sid=Ehkyhry5AtzUNzaS
User-Agent: curl/8.0

```

Three parts matter to you:

- **The request line**: a *method* (`GET`), a *path* with an optional query string (`/note?id=1`), and the version.
- **The headers**: key/value lines. `Host` says which site, `Cookie` carries your session, `Content-Type` describes a body, `User-Agent` names the client. You can set any of them.
- **The body** (optional): data sent with the request, used by `POST` and friends, for example form fields or JSON.

The server replies:

```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Server: NorthWindNotes/1.0 (Python)

<html>...</html>
```

- A **status code**: `2xx` success, `3xx` redirect, `4xx` you got it wrong (`401` unauthenticated, `403` forbidden, `404` not found), `5xx` the server broke. Status codes are the first thing you read when probing: a `403` becoming a `200` after you change one header is a finding.
- **Response headers**: `Set-Cookie` hands you a session, `Location` tells a `3xx` where to go, security headers (or their absence) tell you how carefully the app was built.
- **The body**: HTML, JSON, whatever.

**Methods** carry intent. `GET` reads and should not change state. `POST` submits data (NorthWind's login is a `POST`). `PUT`, `PATCH`, `DELETE` modify. The "should" matters: a bug class later in the course is a `GET` that changes state when it should not.

**Cookies and sessions.** HTTP has no memory on its own. When you log in, NorthWind sets `Set-Cookie: sid=...`. Your browser sends that `sid` back on every later request, and the server looks it up to know you are alice. The cookie *is* your identity to the app. That is why stealing or guessing one matters, and why access decisions that trust only the cookie (and not what you are asking for) go wrong, as you will see in Lesson 03.

**You control more than the browser shows.** The browser only lets you click links and submit forms. A tool like `curl`, or an intercepting proxy, lets you set any method, path, header, cookie or body you like. The server cannot tell a hand-crafted request from a browser's. Every trust the developer placed in "the browser will only send valid requests" is a bug waiting for you.

## Try it in the lab

Start the lab and sign in as `alice` / `password123`.

1. Watch a real exchange:
   ```
   curl -i http://127.0.0.1:8080/
   ```
   Read the status line, the `Server` header, and the body. `-i` shows the response headers.
2. Log in from the command line and capture your cookie:
   ```
   curl -i -d 'username=alice&password=password123' http://127.0.0.1:8080/login
   ```
   Find `Set-Cookie: sid=...` and the `303` redirect. That is a `POST` creating a session.
3. Use the cookie to read one of your notes:
   ```
   curl -i -H 'Cookie: sid=PASTE_HERE' 'http://127.0.0.1:8080/note?id=1'
   ```
   You just reproduced, by hand, what the browser does when you click a note. Now you can change any part of it.

## Key takeaways

- An HTTP request is method + path + headers + optional body; a response is status + headers + body. You can set every part of a request yourself.
- Status codes are your fastest signal: watch for a `4xx` turning into a `2xx` when you change one thing.
- HTTP is stateless; a cookie carries your identity, so the app's trust lives in that cookie.
- The server cannot distinguish a browser from `curl`. Any assumption that clients behave is exploitable.

## Further reading

- MDN, "An overview of HTTP": https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview
- MDN, HTTP response status codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
- MITRE ATT&CK T1190, Exploit Public-Facing Application: https://attack.mitre.org/techniques/T1190/
