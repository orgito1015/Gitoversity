"""NorthWind Notes: a deliberately vulnerable web app for WEB101.

Fictional company, local only, standard library only (http.server).
It intentionally contains: broken access control (IDOR), reflected XSS,
and an information-disclosure endpoint reachable through recon.
"""
import base64
import html
import http.cookies
import json
import os
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def env_flag(name):
    """Read a flag. A b64: prefix is decoded, so .env never ships plain text."""
    value = os.environ.get(name, "")
    return base64.b64decode(value[4:]).decode() if value.startswith("b64:") else value


FLAG1 = env_flag("FLAG1")  # IDOR: lives in admin's private note
FLAG2 = env_flag("FLAG2")  # recon: lives at a hidden endpoint
LEVEL = os.environ.get("LEVEL", "1").strip()
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8080"))
TEMPLATE = Path(__file__).with_name("index.html").read_text(encoding="utf-8")

# Seed data. You log in as alice. Note 2 belongs to admin and holds Flag 1.
USERS = {"alice": "password123"}
SESSIONS = {}  # token -> username
NOTES = {
    1: {"owner": "alice", "title": "Shopping list", "body": "milk, bread, sensors"},
    2: {"owner": "admin", "title": "Escalation runbook", "body": f"Support override code: {FLAG1}"},
    3: {"owner": "alice", "title": "Reminder", "body": "call the courier about order 4471"},
}


def page(title, body):
    return TEMPLATE.replace("{{TITLE}}", html.escape(title)).replace("{{BODY}}", body)


def owns(user, note):
    """Access rule. At LEVEL 2 the IDOR is fixed: you may only read your own notes."""
    return LEVEL != "2" or (note and note["owner"] == user)


class Handler(BaseHTTPRequestHandler):
    server_version = "NorthWindNotes/1.0 (Python)"  # verbose banner: fingerprinting lesson

    # --- helpers -------------------------------------------------------------
    def user(self):
        cookie = http.cookies.SimpleCookie(self.headers.get("Cookie", ""))
        return SESSIONS.get(cookie["sid"].value) if "sid" in cookie else None

    def html(self, status, body, cookie=None):
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        # LEVEL 1 deliberately omits security headers; LEVEL 2 adds them.
        if LEVEL == "2":
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'")
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(data)

    def redirect(self, location, cookie=None):
        self.send_response(303)
        self.send_header("Location", location)
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()

    def text(self, status, body, ctype="text/plain; charset=utf-8"):
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # --- routes --------------------------------------------------------------
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path, query = url.path, urllib.parse.parse_qs(url.query)
        user = self.user()

        if path == "/":
            return self.html(200, self.home(user))
        if path == "/robots.txt":
            # Recon: discloses a path the developer wanted hidden (security by obscurity).
            return self.text(200, "User-agent: *\nDisallow: /internal/\n")
        if path == "/note":
            return self.note_view(user, query)
        if path == "/search":
            return self.search(query)
        if path.startswith("/internal/"):
            return self.internal(path)
        if path == "/logout":
            return self.redirect("/", cookie="sid=; Max-Age=0; Path=/")
        return self.html(404, page("Not found", "<p>No such page.</p><p><a href='/'>Home</a></p>"))

    def do_POST(self):
        if self.path != "/login":
            return self.html(404, page("Not found", "<p>No such page.</p>"))
        length = int(self.headers.get("Content-Length") or 0)
        form = urllib.parse.parse_qs(self.rfile.read(length).decode())
        name = (form.get("username") or [""])[0]
        pw = (form.get("password") or [""])[0]
        if USERS.get(name) == pw:
            token = base64.urlsafe_b64encode(os.urandom(12)).decode()
            SESSIONS[token] = name
            return self.redirect("/", cookie=f"sid={token}; Path=/; HttpOnly")
        return self.html(401, self.home(None, error="Wrong username or password."))

    # --- views ---------------------------------------------------------------
    def home(self, user, error=""):
        if not user:
            err = f"<p style='color:#b00'>{html.escape(error)}</p>" if error else ""
            return page("Sign in", f"""{err}
              <h2>Sign in</h2>
              <form method="post" action="/login">
                <p><input name="username" placeholder="username" required></p>
                <p><input name="password" type="password" placeholder="password" required></p>
                <button>Sign in</button>
              </form>
              <p class="hint">Demo account: alice / password123</p>""")
        mine = "".join(
            f'<li><a href="/note?id={i}">{html.escape(n["title"])}</a></li>'
            for i, n in NOTES.items() if n["owner"] == user
        )
        return page("Your notes", f"""
          <p>Signed in as <strong>{html.escape(user)}</strong>. <a href="/logout">Log out</a></p>
          <h2>Your notes</h2>
          <ul>{mine}</ul>
          <h2>Search notes</h2>
          <form method="get" action="/search">
            <input name="q" placeholder="search your notes"><button>Search</button>
          </form>""")

    def note_view(self, user, query):
        if not user:
            return self.redirect("/")
        try:
            note_id = int((query.get("id") or ["0"])[0])
        except ValueError:
            return self.html(400, page("Bad request", "<p>id must be a number.</p>"))
        note = NOTES.get(note_id)
        if not note:
            return self.html(404, page("Not found", "<p>No such note.</p><p><a href='/'>Home</a></p>"))
        if not owns(user, note):  # IDOR at LEVEL 1: this check is effectively off
            return self.html(403, page("Forbidden", "<p>That note is not yours.</p><p><a href='/'>Home</a></p>"))
        return self.html(200, page(note["title"], f"""
          <h2>{html.escape(note["title"])}</h2>
          <p>Owner: {html.escape(note["owner"])}</p>
          <pre>{html.escape(note["body"])}</pre>
          <p><a href="/">Back</a></p>"""))

    def search(self, query):
        q = (query.get("q") or [""])[0]
        # Reflected XSS at LEVEL 1: q is echoed unescaped. LEVEL 2 escapes it.
        shown = html.escape(q) if LEVEL == "2" else q
        return self.html(200, page("Search", f"""
          <h2>Search</h2>
          <p>You searched for: {shown}</p>
          <p>No matching notes.</p>
          <p><a href="/">Back</a></p>"""))

    def internal(self, path):
        # No authentication: information disclosure once the path is discovered.
        if path == "/internal/config":
            cfg = {"app": "NorthWind Notes", "env": "production",
                   "debug": True, "internal_api_key": FLAG2}
            return self.text(200, json.dumps(cfg, indent=2), "application/json")
        return self.html(404, page("Not found", "<p>No such page.</p>"))


if __name__ == "__main__":
    if not FLAG1 or not FLAG2:
        raise SystemExit("FLAG1 and FLAG2 must be set (copy .env.example to .env)")
    print(f"NorthWind Notes on http://{HOST}:{PORT} level={LEVEL}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
