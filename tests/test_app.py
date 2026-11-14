import re
import unittest
from unittest.mock import patch

import requests

import app as app_module


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        return None

    def json(self):
        return self.data


class AppTests(unittest.TestCase):
    def setUp(self):
        app_module.app.config.update(TESTING=True)
        self.client = app_module.app.test_client()

    def test_homepage_sets_security_headers_and_nonce(self):
        response = self.client.get("/")
        body = response.get_data(as_text=True)
        nonce = re.search(r'<script nonce="([^"]+)"', body).group(1)

        self.assertIn(f"nonce-{nonce}", response.headers["Content-Security-Policy"])
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_chat_rejects_non_json_and_invalid_messages(self):
        non_json = self.client.post("/api/chat", data="hello")
        invalid_json = self.client.post("/api/chat", json={"text": "  "})

        self.assertEqual(non_json.status_code, 415)
        self.assertEqual(invalid_json.status_code, 400)

    def test_chat_requires_api_key(self):
        with patch.object(app_module, "GEMINI_API_KEY", ""):
            response = self.client.post("/api/chat", json={"text": "Election date?"})

        self.assertEqual(response.status_code, 503)
        self.assertNotIn("API key", response.get_data(as_text=True))

    def test_chat_sends_bounded_history_and_returns_model_response(self):
        api_data = {
            "candidates": [
                {
                    "content": {"parts": [{"text": "Check the ECI website."}]},
                    "groundingMetadata": {"groundingChunks": []},
                }
            ]
        }
        with patch.object(app_module, "GEMINI_API_KEY", "test-key"), patch.object(
            app_module.requests, "post", return_value=FakeResponse(api_data)
        ) as post:
            response = self.client.post("/api/chat", json={"text": "Election date?"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), api_data)
        self.assertEqual(post.call_args.kwargs["timeout"], (5, 30))
        self.assertEqual(post.call_args.kwargs["json"]["contents"][0]["role"], "user")
        self.assertEqual(
            post.call_args.kwargs["headers"]["x-goog-api-key"], "test-key"
        )

    def test_upstream_error_does_not_expose_exception_details(self):
        with patch.object(app_module, "GEMINI_API_KEY", "test-key"), patch.object(
            app_module.requests,
            "post",
            side_effect=requests.exceptions.Timeout("private upstream detail"),
        ):
            response = self.client.post("/api/chat", json={"text": "Election date?"})

        self.assertEqual(response.status_code, 502)
        self.assertNotIn("private upstream detail", response.get_data(as_text=True))

    def test_reset_clears_session_history(self):
        with self.client.session_transaction() as chat_session:
            chat_session["chat_history"] = [{"role": "user", "parts": [{"text": "Hi"}]}]

        response = self.client.post("/api/chat/reset")

        self.assertEqual(response.get_json(), {"ok": True})
        with self.client.session_transaction() as chat_session:
            self.assertNotIn("chat_history", chat_session)


if __name__ == "__main__":
    unittest.main()
