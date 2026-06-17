# Kartikey: Election Assistant

Kartikey is a professional AI-powered India Election Assistant. It provides neutral, factual information based on the Election Commission of India (ECI) data, utilizing Google Search to fetch real-time updates.

## Features

-   **AI Conversations:** Powered by Google Gemini with integrated Google Search tools.
-   **Voice Support:** Male Indian-accented voice for responses.
-   **Speech-to-Text:** Use your microphone to ask questions.
-   **Real-time Info:** Fetches the latest election dates, candidate details, and procedures.
-   **Session Memory:** Maintains chat history within a session.
-   **Responsive Design:** Optimized for both desktop and mobile devices.

## Prerequisites

-   Python 3.8+
-   Google Gemini API Key

## Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set your environment variables:
    -   `GEMINI_API_KEY`: Your Google AI Studio API key.
    -   `FLASK_SECRET_KEY`: A secret string for session encryption.

## Usage

1.  Run the Flask server:
    ```bash
    python app.py
    ```
2.  Open your browser and navigate to `http://127.0.0.1:5000`.

## Disclaimer
Kartikey is an AI assistant and may occasionally provide incorrect information. Always verify critical election details on the official [ECI website](https://eci.gov.in).