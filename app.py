from flask import Flask, request, jsonify, session, render_template
import requests
import os

# 1. Setup absolute paths
basedir = os.path.abspath(os.path.dirname(__file__))

# 2. Initialize Flask 
app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))

# 3. Secret key for session management
app.secret_key = "kartikey_secret_session_key"

# 4. PASTE YOUR FULL AQ. KEY HERE INSIDE THE QUOTES
GEMINI_API_KEY = "PASTE_YOUR_FULL_API_KEY_HERE"

# System Prompt
SYSTEM_INSTRUCTION = "You are Kartikey, a professional India Election Assistant. Keep answers concise."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_data = request.json
    user_text = user_data.get('text')
    clean_key = GEMINI_API_KEY.strip()

    if not clean_key or "PASTE_YOUR" in clean_key:
        return jsonify({"error": "Backend API Key is not configured in app.py."}), 500

    # Manage conversation history
    history = session.get('chat_history', [])
    history.append({"role": "user", "parts": [{"text": user_text}]})
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": clean_key
    }

    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "contents": history
    }

    try:
        
        response = requests.post(url, headers=headers, json=payload)
        
        response.raise_for_status()
        
        data = response.json()

        if "candidates" in data and data["candidates"]:
            model_content = data["candidates"][0]["content"]
            history.append(model_content)
            session['chat_history'] = history

        return jsonify(data)
        
    except requests.exceptions.RequestException as e:
        # Send the exact error to the frontend so we can see it
        error_msg = f"API Error: {str(e)}"
        
        # Add detailed error message from Google if available
        if getattr(e, 'response', None) is not None and e.response.text:
            error_msg += f" | Details: {e.response.text}"
            
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)