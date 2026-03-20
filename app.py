"""
============================================================
app.py  –  Flask Web Application
============================================================
Serves the chatbot UI and handles API endpoints for:
  • Sending messages       POST /api/chat
  • Retrieving history     GET  /api/history
  • Clearing history       POST /api/clear
  • Voice status check     GET  /api/voice/status
  • Voice input capture    POST /api/voice/listen
============================================================
"""

import os
from flask import Flask, render_template, request, jsonify, session
from src.chatbot import ChatBot
from src.context_manager import ContextManager
from src.sentiment import get_sentiment_label
from src.history import save_chat, get_recent_chats, clear_history
from src.voice import listen_from_mic, speak, is_voice_available

# ── Flask app setup ───────────────────────────────────────
app = Flask(__name__)
app.secret_key = "hci-chatbot-secret-key-2024"

# ── Initialize chatbot (loaded once) ─────────────────────
bot = ChatBot()

# ── In-memory context store keyed by session id ──────────
contexts = {}


def _get_ctx() -> ContextManager:
    """Get or create a ContextManager for the current session."""
    sid = session.get("sid")
    if sid is None or sid not in contexts:
        import uuid
        sid = str(uuid.uuid4())
        session["sid"] = sid
        contexts[sid] = ContextManager()
    return contexts[sid]


# ──────────────────────────────────────────────────────────
#  Page Routes
# ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main chat interface."""
    return render_template("index.html")


# ──────────────────────────────────────────────────────────
#  API Routes
# ──────────────────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Receive a user message and return the bot's response.

    Request JSON:  { "message": "..." }
    Response JSON: { "response", "intent", "confidence", "sentiment" }
    """
    data = request.get_json(force=True)
    user_msg = data.get("message", "").strip()

    if not user_msg:
        return jsonify({"error": "Empty message"}), 400

    ctx = _get_ctx()
    result = bot.get_response(user_msg, ctx)

    # Persist to SQLite
    save_chat(
        user_msg=user_msg,
        bot_msg=result["response"],
        sentiment=result["sentiment"]["label"],
    )

    return jsonify(result)


@app.route("/api/history", methods=["GET"])
def history():
    """Return recent chat history from SQLite."""
    chats = get_recent_chats(limit=100)
    return jsonify(chats)


@app.route("/api/clear", methods=["POST"])
def clear():
    """Clear chat history and reset context."""
    clear_history()
    ctx = _get_ctx()
    ctx.reset()
    return jsonify({"status": "cleared"})


@app.route("/api/voice/status", methods=["GET"])
def voice_status():
    """Check if voice features are available."""
    return jsonify(is_voice_available())


@app.route("/api/voice/listen", methods=["POST"])
def voice_listen():
    """
    Capture speech from the microphone.
    Returns { "text": "..." } or { "text": null } on failure.
    """
    text = listen_from_mic()
    if text:
        return jsonify({"text": text})
    return jsonify({"text": None, "fallback": True})


@app.route("/api/voice/speak", methods=["POST"])
def voice_speak():
    """Speak the given text aloud via TTS."""
    data = request.get_json(force=True)
    text = data.get("text", "")
    success = speak(text)
    return jsonify({"spoken": success})


# ──────────────────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  HCI Chatbot – Starting Flask Server")
    print("  Open http://127.0.0.1:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, host="127.0.0.1", port=5000, use_reloader=False)
