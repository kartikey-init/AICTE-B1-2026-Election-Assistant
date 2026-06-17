from flask import Flask, request, jsonify, session, render_template
import requests
import os

# 1. Setup absolute paths to bypass any folder confusion
basedir = os.path.abspath(os.path.dirname(__file__))

# 2. Initialize Flask (pointing it exactly to the templates folder)
app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))

# 3. Secret key for session management
app.secret_key = "kartikey_secret_session_key"

# 4. PASTE YOUR FULL AQ. KEY HERE INSIDE THE QUOTES
GEMINI_API_KEY = "AQ.Ab8RN6IRVzTUPfROgOCMY0GG4LYszWOB_WCoOGzC3jjbYVrVGg"

# System Prompt
SYSTEM_INSTRUCTION = "You are Kartikey, a professional India Election Assistant. Keep answers concise."

@app.route('/')
def index():
    # This loads the index.html from your templates folder
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_data = request.json
    user_text = user_data.get('text')

    # Clean the key to remove accidental spaces
    clean_key = GEMINI_API_KEY.strip()

    if not clean_key or "PASTE_YOUR" in clean_key:
        return jsonify({"error": "Backend API Key is not configured in app.py."}), 500

    # Manage conversation history
    history = session.get('chat_history', [])
    history.append({"role": "user", "parts": [{"text": user_text}]})

    # THE URL (Notice there is NO ?key= at the end anymore)
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    # THE HEADERS (This is the required format for AQ. keys)
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
        # Send the request to Google using the new headers
        response = requests.post(url, headers=headers, json=payload)
        
        # If Google returns an error, this catches it
        response.raise_for_status()
        
        data = response.json()

        # Append the model's response to history if successful
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
    # Running on port 5001
    app.run(debug=True, port=5001)