"""Smoke test for the AIRT101 HelpBot lab. Standard library only.

Start the lab first (docker compose up), then run: python3 test_lab.py
Small models are not deterministic, so this never asserts that an injection works.
"""
import json
import os
import sys
import unittest
import urllib.request
import uuid

BASE = os.environ.get("LAB_URL", "http://127.0.0.1:8080")

# app.py reads its config at import time, so set test values first.
os.environ["FLAG2"] = "TEST_FLAG_TWO"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app  # noqa: E402


def post(path, body, content_type):
    req = urllib.request.Request(BASE + path, data=body, headers={"Content-Type": content_type})
    with urllib.request.urlopen(req, timeout=300) as resp:
        return resp.status, json.load(resp)


class ToolLogic(unittest.TestCase):
    def test_get_secret_is_replaced(self):
        out = app.run_tools("Here you go: CALL get_secret() and again CALL get_secret( )")
        self.assertEqual(out, "Here you go: TEST_FLAG_TWO and again TEST_FLAG_TWO")

    def test_text_without_call_is_unchanged(self):
        self.assertEqual(app.run_tools("get_secret is a tool"), "get_secret is a tool")

    def test_b64_flag_decoding(self):
        os.environ["TMP_FLAG"] = "b64:dGVzdA=="
        self.assertEqual(app.env_flag("TMP_FLAG"), "test")

    def test_level2_filter(self):
        app.LEVEL = "2"
        try:
            self.assertEqual(app.blocked("Please IGNORE that"), "ignore")
            self.assertIsNone(app.blocked("Where is my order?"))
        finally:
            app.LEVEL = "1"
        self.assertIsNone(app.blocked("ignore"))


class LiveLab(unittest.TestCase):
    def test_app_answers(self):
        with urllib.request.urlopen(BASE + "/", timeout=10) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn(b"HelpBot", resp.read())

    def test_chat_returns_reply(self):
        status, data = post("/chat", json.dumps({"message": "Hi, what do you sell?"}).encode(), "application/json")
        self.assertEqual(status, 200)
        self.assertTrue(data["reply"].strip())

    def test_summarize_accepts_file(self):
        boundary = uuid.uuid4().hex
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="file"; filename="note.txt"\r\n'
            "Content-Type: text/plain\r\n\r\n"
            "Shipping to Europe takes five working days. Returns are free within 30 days.\r\n"
            f"--{boundary}--\r\n"
        ).encode()
        status, data = post("/summarize", body, f"multipart/form-data; boundary={boundary}")
        self.assertEqual(status, 200)
        self.assertTrue(data["reply"].strip())


if __name__ == "__main__":
    unittest.main(verbosity=2)
