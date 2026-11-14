# Kartikey: Election Assistant

Kartikey is an AI-powered assistant for questions about Indian elections. It uses
Google Gemini with Google Search grounding. AI responses can be inaccurate or
out of date; verify important information with the Election Commission of India
(ECI).

## Requirements

- Python 3.10 or newer
- A Google Gemini API key

## Local setup

From the project directory, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set the required environment variables in PowerShell. Generate a strong Flask
session key rather than reusing a checked-in value:

```powershell
$env:GEMINI_API_KEY = "your-Gemini-API-key"
$env:FLASK_SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
python app.py
```

Open `http://127.0.0.1:5001`. The development run uses Flask's built-in server
with debug mode disabled.

## Production

Configure `APP_ENV=production`, `GEMINI_API_KEY`, and `FLASK_SECRET_KEY` in the
hosting environment. The app refuses to start in production if either key is
missing and marks session cookies secure. Serve it with a production WSGI server,
not Flask's built-in server. For example, with Waitress:

```powershell
$env:APP_ENV = "production"
waitress-serve --listen=127.0.0.1:5001 app:app
```

Put the WSGI server behind HTTPS and a reverse proxy or hosting platform. Add
request rate limits at that edge to protect the Gemini API quota and configure
platform-level monitoring, backups, and deployment secrets.

Conversation history is stored in Flask's signed client-side session cookie.
It is size-limited but not encrypted, so users should not enter sensitive
personal information. For deployments requiring private or persistent
conversations, use a server-side session store such as Redis.

## Features

- Gemini chat with Google Search grounding and source links
- Browser speech recognition and speech playback where supported
- Responsive layout and accessible chat controls
- Bounded conversation context and a control to clear it

## Disclaimer

Kartikey is an AI assistant and may provide incomplete or incorrect information.
Always verify critical election dates, procedures, and other details on the
official [ECI website](https://eci.gov.in) or the
[Voter Portal](https://voters.eci.gov.in/).
