import os
import secrets
from datetime import timedelta

import requests
from flask import Flask, g, jsonify, render_template, request, session
from werkzeug.exceptions import RequestEntityTooLarge

APP_ENV = os.environ.get("APP_ENV", "development").strip().lower()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "").strip()

if APP_ENV == "production" and (not GEMINI_API_KEY or not FLASK_SECRET_KEY):
    raise RuntimeError(
        "GEMINI_API_KEY and FLASK_SECRET_KEY must be configured in production."
    )

app = Flask(__name__)
app.config.update(
    SECRET_KEY=FLASK_SECRET_KEY or secrets.token_hex(32),
    MAX_CONTENT_LENGTH=16 * 1024,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=APP_ENV == "production",
)

SYSTEM_INSTRUCTION = (
    "You are Kartikey, a professional India Election Assistant. "
    "Give concise, neutral answers and distinguish verified facts from uncertainty. "
    "Encourage users to verify important election information with official sources."
)
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)
MAX_MESSAGE_LENGTH = 2000
MAX_HISTORY_MESSAGES = 4
MAX_STORED_TEXT_LENGTH = 400


@app.before_request
def create_csp_nonce():
    g.csp_nonce = secrets.token_urlsafe(18)


@app.context_processor
def inject_template_values():
    return {"csp_nonce": g.csp_nonce}


@app.after_request
def add_security_headers(response):
    nonce = getattr(g, "csp_nonce", "")
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}'; "
        f"style-src 'self' 'nonce-{nonce}' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; "
        "connect-src 'self'; "
        "img-src 'self' data:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), geolocation=(), microphone=(self)"
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@app.errorhandler(RequestEntityTooLarge)
def handle_request_too_large(_error):
    return jsonify({"error": "Request is too large."}), 413


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/chat")
def chat():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json."}), 415

    user_data = request.get_json(silent=True)
    if not isinstance(user_data, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    user_text = user_data.get("text")
    if not isinstance(user_text, str) or not user_text.strip():
        return jsonify({"error": "Enter a message before sending."}), 400
    user_text = user_text.strip()
    if len(user_text) > MAX_MESSAGE_LENGTH:
        return jsonify(
            {"error": f"Messages must be {MAX_MESSAGE_LENGTH} characters or fewer."}
        ), 400

    if not GEMINI_API_KEY:
        return jsonify(
            {"error": "The chat service is not configured. Please try again later."}
        ), 503

    history = session.get("chat_history", [])
    if not isinstance(history, list):
        history = []
    history = [
        message
        for message in history
        if isinstance(message, dict)
        and message.get("role") in {"user", "model"}
        and isinstance(message.get("parts"), list)
        and message["parts"]
        and isinstance(message["parts"][0], dict)
        and isinstance(message["parts"][0].get("text"), str)
    ][-MAX_HISTORY_MESSAGES:]
    history.append(
        {"role": "user", "parts": [{"text": user_text[:MAX_STORED_TEXT_LENGTH]}]}
    )

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
        "contents": history,
        "tools": [{"google_search": {}}],
        "generationConfig": {"maxOutputTokens": 512},
    }

    try:
        response = requests.post(
            GEMINI_URL,
            headers={"x-goog-api-key": GEMINI_API_KEY},
            json=payload,
            timeout=(5, 30),
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException:
        app.logger.exception("Gemini request failed.")
        return jsonify(
            {"error": "The chat service is temporarily unavailable. Please try again."}
        ), 502

    candidates = data.get("candidates") if isinstance(data, dict) else None
    if not isinstance(candidates, list) or not candidates:
        return jsonify(
            {"error": "The chat service could not provide a response. Please try again."}
        ), 502

    candidate = candidates[0]
    content = candidate.get("content") if isinstance(candidate, dict) else None
    parts = content.get("parts") if isinstance(content, dict) else None
    reply_text = (
        parts[0].get("text")
        if isinstance(parts, list) and parts and isinstance(parts[0], dict)
        else None
    )
    if not isinstance(reply_text, str) or not reply_text.strip():
        return jsonify(
            {"error": "The chat service could not provide a response. Please try again."}
        ), 502

    history.append(
        {
            "role": "model",
            "parts": [{"text": reply_text[:MAX_STORED_TEXT_LENGTH]}],
        }
    )
    session["chat_history"] = history[-MAX_HISTORY_MESSAGES:]
    session.permanent = True
    return jsonify(data)


@app.post("/api/chat/reset")
def reset_chat():
    session.pop("chat_history", None)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5001")),
        debug=False,
    )
