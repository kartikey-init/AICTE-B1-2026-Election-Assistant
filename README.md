# Kartikey: Election Assistant

Kartikey is a responsive Flask web assistant for questions about Indian elections.
It sends conversations to Google Gemini using Google Search grounding and returns
source-backed AI responses to the browser. AI responses can be inaccurate or out
of date, so important information should always be verified with official
Election Commission of India (ECI) sources.

## Highlights

- Google Gemini-powered election chat
- Google Search grounding with links supplied by Gemini
- Browser speech recognition and text-to-speech, where supported
- Responsive, accessible chat interface
- Up to four recent messages retained as bounded conversation context
- Session reset control
- Request size limits and security headers
- Development and production configuration

## Requirements

- Python 3.10 or newer
- A Google Gemini API key
- PowerShell or another terminal capable of running Python and Flask

## Installation

Clone or download the project, open a terminal in the project directory, and
create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Configuration

Set the Gemini API key and a persistent Flask secret key in PowerShell:

```powershell
$env:GEMINI_API_KEY = "your-gemini-api-key"
$env:FLASK_SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(32))")
```

Environment variables are session-local unless exported through your system or
hosting platform.

| Variable | Required | Default | Purpose |
| --- | --- | --- | --- |
| `GEMINI_API_KEY` | Yes for chat | Empty | Authenticates requests to the Gemini API |
| `FLASK_SECRET_KEY` | Recommended | Random key in memory | Signs Flask session cookies |
| `APP_ENV` | No | `development` | Set to `production` to enable production checks and secure cookies |
| `HOST` | No | `127.0.0.1` | Host used by `python app.py` |
| `PORT` | No | `5001` | Port used by `python app.py` |

If `FLASK_SECRET_KEY` is not set in development, a random key is generated each
time the app starts. This invalidates existing sessions after a restart.

## Run locally

Start the development server:

```powershell
python app.py
```

Then open <http://127.0.0.1:5001>.

The app uses Flask's built-in server for development only, with debug mode
disabled.

## Tests

Run the unit tests from the project directory:

```powershell
python -m unittest discover -s tests -v
```

The tests cover security headers, request validation, API configuration,
Gemini error handling, bounded request history, and conversation reset behavior.

## Project structure

```text
app.py              Flask application and Gemini API integration
templates/
  index.html        Responsive chat interface
tests/
  test_app.py       Flask route and integration-focused unit tests
requirements.txt    Application dependencies
.gitignore          Local environment and Python cache exclusions
```

## Production

Configure `APP_ENV=production`, `GEMINI_API_KEY`, and `FLASK_SECRET_KEY` in the
hosting environment. The app refuses to start in production when either required
key is missing and marks session cookies as secure.

Serve the app with a production WSGI server, not Flask's development server.
For example, Waitress can be used on Windows:

```powershell
$env:APP_ENV = "production"
$env:GEMINI_API_KEY = "your-gemini-api-key"
$env:FLASK_SECRET_KEY = "a-long-random-persistent-secret"
waitress-serve --listen=127.0.0.1:5001 app:app
```

Put the WSGI server behind HTTPS and a reverse proxy or hosting platform.
Because the app creates Gemini API requests from the server, keep rate limiting,
platform-level monitoring, deployment secrets, and Gemini quota controls at the
hosting and proxy layers.

## Privacy and conversation storage

Conversation history is stored in Flask's signed, client-side session cookie.
The cookie is size-limited but is not encrypted. It is therefore unsuitable for
passwords, personal identifiers, or sensitive election-related case information.

For deployments requiring private or persistent conversations, use a server-side
session store such as Redis and a documented data-retention policy.

## API behavior

- `GET /` renders the chat page.
- `POST /api/chat` accepts JSON in the form `{"text": "Your question"}`.
- `POST /api/chat/reset` clears the current conversation history.

Messages are limited to 2,000 characters per request. The app sends at most four
recent messages to Gemini and limits stored response text to 400 characters per
message. Request bodies are limited to 16 KB.

## Troubleshooting

- **Chat returns 503:** Confirm that `GEMINI_API_KEY` is set in the environment
  used to run the app.
- **Chat returns 502:** Check network access and Gemini API availability, quota,
  and key permissions.
- **Users lose conversations after restart:** Set and persist
  `FLASK_SECRET_KEY`.
- **Production will not start:** Set both `GEMINI_API_KEY` and
  `FLASK_SECRET_KEY` before setting `APP_ENV=production`.

## Contributing

1. Create a branch for the change.
2. Keep dependencies in `requirements.txt`.
3. Add or update focused tests for behavioral changes.
4. Run the test suite before opening a pull request.
5. Never commit API keys or real session secrets.

## Disclaimer

Kartikey is an AI assistant and may provide incomplete or incorrect information.
Always verify critical election dates, voting procedures, candidate details, and
other information on the official [ECI website](https://eci.gov.in) or
[Voter Portal](https://voters.eci.gov.in/).
