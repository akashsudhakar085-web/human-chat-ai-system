# Human–Computer Interaction Using Chatbots

An AI/ML project demonstrating an intelligent chatbot built with **Python**, **NLTK**, **scikit-learn**, and **Flask**.

---

## 📁 Project Structure

```
aiml project/
├── app.py                  # Flask web server (entry point)
├── requirements.txt        # Python dependencies
├── data/
│   └── intents.json        # 30 intents with training patterns
├── model/                  # (auto-generated after training)
│   ├── intent_model.pkl
│   ├── tfidf_vectorizer.pkl
│   └── label_classes.pkl
├── src/
│   ├── __init__.py
│   ├── nlp_utils.py        # Text preprocessing (NLTK)
│   ├── model_trainer.py    # Train the intent classifier
│   ├── sentiment.py        # VADER sentiment analysis
│   ├── context_manager.py  # Context & pronoun resolution
│   ├── chatbot.py          # Core chatbot engine
│   ├── history.py          # SQLite chat history
│   └── voice.py            # Optional voice I/O
├── templates/
│   └── index.html          # Chat interface HTML
├── static/
│   ├── style.css           # Dark-themed UI styles
│   └── script.js           # Frontend chat logic
├── README.md
├── Project_Report.md
└── System_Architecture.md
```

---

## 🚀 How to Run

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download NLTK Data (one time, small download)

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('vader_lexicon')"
```

### 3. Train the Model

```bash
python -m src.model_trainer
```

This will create the `model/` directory with the trained classifier.

### 4. Start the Chatbot

```bash
python app.py
```

Open your browser and go to **http://127.0.0.1:5000**

---

## ✨ Features

| Feature | Details |
|---|---|
| **NLP Processing** | Tokenization, lemmatization via NLTK |
| **Intent Classification** | Logistic Regression + TF-IDF (30 intents) |
| **Confidence Handling** | Uses `predict_proba()` with fallback below 35% |
| **Sentiment Analysis** | VADER (offline, no heavy downloads) |
| **Context Memory** | Tracks entities, handles pronoun resolution |
| **Chat History** | Stored in SQLite with timestamps & sentiment |
| **Voice I/O** | Optional SpeechRecognition + pyttsx3 with fallback |
| **Web UI** | Flask + responsive dark-themed interface |
| **Typing Effect** | Simulated "Bot is typing…" delay |

---

## 🐍 Running in Python IDLE

If you prefer Python IDLE instead of the terminal:

1. Open `app.py` in IDLE
2. Press `F5` (Run Module)
3. The server will start — open http://127.0.0.1:5000 in a browser

> **Note**: Train the model first by running `src/model_trainer.py` in IDLE.

---

## 📄 Documentation

- **[Project Report](Project_Report.md)** – Aim, Objective, Methodology, Results, Conclusion
- **[System Architecture](System_Architecture.md)** – Flowchart and module explanation
