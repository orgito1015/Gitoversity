"""Smoke test for the WEB101 NorthWind Notes lab. Standard library only.

Start the lab first (docker compose up), then run: python3 test_lab.py
"""
import http.client
import os
import sys
import unittest
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("LAB_URL", "http://127.0.0.1:8080")

os.environ.setdefault("FLAG1", "TEST1")
os.environ.setdefault("FLAG2", "TEST2")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app  # noqa: E402


def get(path, cookie=None):
    req = urllib.request.Request(BASE + path)
    if cookie:
        req.add_header("Cookie", cookie)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read().decode(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(), dict(e.headers)


def login():
    """Post credentials and return the sid cookie from the 303, without following it."""
    host = urllib.parse.urlparse(BASE).netloc
    conn = http.client.HTTPConnection(host, timeout=10)
    conn.request("POST", "/login", "username=alice&password=password123",
                 {"Content-Type": "application/x-www-form-urlencoded"})
    resp = conn.getresponse()
    cookie = resp.getheader("Set-Cookie")
    conn.close()
    return cookie.split(";")[0]


class AccessControlLogic(unittest.TestCase):
    def test_owns_rule(self):
        note = {"owner": "admin"}
        app.LEVEL = "1"
        self.assertTrue(app.owns("alice", note))   # IDOR open
        app.LEVEL = "2"
        try:
            self.assertFalse(app.owns("alice", note))  # fixed
            self.assertTrue(app.owns("admin", note))
        finally:
            app.LEVEL = "1"

    def test_b64_flag(self):
        os.environ["TMP"] = "b64:dGVzdA=="
        self.assertEqual(app.env_flag("TMP"), "test")


class LiveLab(unittest.TestCase):
    def test_home(self):
        status, body, _ = get("/")
        self.assertEqual(status, 200)
        self.assertIn("NorthWind Notes", body)

    def test_robots_discloses_internal(self):
        status, body, _ = get("/robots.txt")
        self.assertEqual(status, 200)
        self.assertIn("/internal/", body)

    def test_internal_config_reachable(self):
        status, body, _ = get("/internal/config")
        self.assertEqual(status, 200)
        self.assertIn("internal_api_key", body)

    def test_login_and_read_own_note(self):
        sid = login()
        status, body, _ = get("/note?id=1", sid)
        self.assertEqual(status, 200)
        self.assertIn("Shopping list", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
