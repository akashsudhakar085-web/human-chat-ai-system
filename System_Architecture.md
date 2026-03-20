# System Architecture: Human–Computer Interaction Using Chatbots

---

## 1. High-Level Architecture

The system follows a **modular, layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                         │
│         (Browser: HTML + CSS + JavaScript)                  │
│                                                             │
│   ┌──────────┐  ┌──────────────┐  ┌──────────────────┐     │
│   │ Text     │  │ Voice Toggle │  │ Sentiment Badge  │     │
│   │ Input    │  │ + Mic Button │  │ + Confidence %   │     │
│   └────┬─────┘  └──────┬───────┘  └──────────────────┘     │
│        │               │                                    │
└────────┼───────────────┼────────────────────────────────────┘
         │  HTTP/AJAX    │
         ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│                    FLASK WEB SERVER                          │
│                      (app.py)                               │
│                                                             │
│   Routes:  /api/chat  /api/history  /api/voice/*           │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                   CHATBOT ENGINE                            │
│                   (src/chatbot.py)                          │
│                                                             │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────────┐     │
│  │ NLP Utils   │ │   Sentiment  │ │ Context Manager  │     │
│  │ (preprocess)│ │   (VADER)    │ │ (entity tracking │     │
│  │             │ │              │ │  pronoun resolve) │     │
│  └──────┬──────┘ └──────┬───────┘ └────────┬─────────┘     │
│         │               │                  │               │
│         ▼               │                  │               │
│  ┌──────────────┐       │                  │               │
│  │ TF-IDF       │       │                  │               │
│  │ Vectorizer   │       │                  │               │
│  └──────┬───────┘       │                  │               │
│         ▼               │                  │               │
│  ┌──────────────┐       │                  │               │
│  │ Logistic     │◄──────┘                  │               │
│  │ Regression   │◄─────────────────────────┘               │
│  │ (predict +   │                                          │
│  │  confidence) │                                          │
│  └──────┬───────┘                                          │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │ Response     │    │ Voice Module │                      │
│  │ Generator    │    │ (optional)   │                      │
│  └──────┬───────┘    └──────────────┘                      │
│         │                                                   │
└─────────┼───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────┐    ┌────────────────────────┐
│  SQLite Database        │    │  intents.json          │
│  (chat_history.db)      │    │  (training dataset)    │
│  • user_msg             │    │  • 30 intent tags      │
│  • bot_msg              │    │  • patterns            │
│  • sentiment            │    │  • responses           │
│  • timestamp            │    │  • entities            │
└─────────────────────────┘    └────────────────────────┘
```

---

## 2. Data Flow (Conversation Flowchart)

```
User types / speaks a message
        │
        ▼
┌───────────────────┐
│ Input Received    │
│ (text or voice)   │
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│ Voice → Text      │──── If voice fails ──→ Fallback to text input
│ (if voice mode)   │
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│ Sentiment         │──→ Returns: positive / negative / neutral
│ Analysis (VADER)  │
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│ Pronoun           │──→ "she" → "Droupadi Murmu" (from context)
│ Resolution        │
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│ Preprocessing     │──→ clean → tokenize → lemmatize
│ (nlp_utils.py)    │
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│ TF-IDF            │──→ Convert text to numerical vector
│ Vectorization     │
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│ Intent            │──→ predict_proba() → tag + confidence
│ Classification    │
└───────┬───────────┘
        │
        ├── confidence < 0.35 ──→ Return fallback: "Can you rephrase?"
        │
        ▼
┌───────────────────┐
│ Response          │──→ Pick random response for the intent
│ Selection         │    + sentiment-aware prefix
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│ Update Context    │──→ Store intent, entities for follow-ups
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│ Save to SQLite    │──→ user_msg, bot_msg, sentiment, timestamp
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│ Display Response  │──→ Show in UI with confidence badge
│ + Speak (if on)   │    and sentiment indicator
└───────────────────┘
```

---

## 3. Module Descriptions

| Module | File | Responsibility |
|---|---|---|
| **NLP Utilities** | `src/nlp_utils.py` | Text cleaning, tokenization, lemmatization |
| **Model Trainer** | `src/model_trainer.py` | Trains and saves the Logistic Regression model |
| **Sentiment Analyzer** | `src/sentiment.py` | VADER-based sentiment detection |
| **Context Manager** | `src/context_manager.py` | Entity tracking, pronoun resolution, turn history |
| **Chatbot Engine** | `src/chatbot.py` | Orchestrates all components, generates final responses |
| **Chat History** | `src/history.py` | SQLite persistence for all conversations |
| **Voice Module** | `src/voice.py` | Optional STT/TTS with graceful fallback |
| **Web Server** | `app.py` | Flask routes serving the UI and API endpoints |
| **Frontend** | `templates/`, `static/` | HTML/CSS/JS for the chat interface |

---

## 4. HCI Design Principles Applied

| Principle | Implementation |
|---|---|
| **Visibility** | Clear message bubbles, confidence badges, sentiment indicators |
| **Feedback** | "Bot is typing…" animation, voice status toasts |
| **Consistency** | Uniform dark theme, consistent spacing and typography |
| **Error Prevention** | Confidence thresholding, graceful voice fallback |
| **Flexibility** | Text + voice input, toggle controls |
| **Aesthetics** | Modern dark UI with smooth micro-animations |
| **Responsiveness** | Works on desktop, tablet, and mobile screens |
