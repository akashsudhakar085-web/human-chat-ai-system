"""
============================================================
model_trainer.py  –  Intent Classification Model
============================================================
Trains a Logistic Regression classifier on the intents
dataset using TF-IDF vectorization.

Run this file directly to train and save the model:
    python -m src.model_trainer
============================================================
"""

import json
import os
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Import our preprocessing pipeline
from src.nlp_utils import preprocess

# ── Paths ──────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "intents.json")
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "intent_model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, "label_classes.pkl")


def load_intents(filepath: str) -> dict:
    """Load the intents JSON file and return parsed dict."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def prepare_training_data(intents: dict):
    """
    Build parallel lists of preprocessed sentences and
    their corresponding intent tags.
    """
    sentences = []
    labels = []

    for intent in intents["intents"]:
        tag = intent["tag"]
        for pattern in intent["patterns"]:
            processed = preprocess(pattern)
            sentences.append(processed)
            labels.append(tag)

    return sentences, labels


def train_model():
    """
    Full training pipeline:
      1. Load intents
      2. Preprocess text
      3. Vectorize with TF-IDF
      4. Train Logistic Regression
      5. Evaluate accuracy
      6. Save artifacts (model, vectorizer, label classes)
    """
    print("=" * 50)
    print("  Intent Classification – Model Training")
    print("=" * 50)

    # ── 1. Load data ──────────────────────────────────────
    intents = load_intents(DATA_PATH)
    sentences, labels = prepare_training_data(intents)
    print(f"\n✔ Loaded {len(sentences)} training samples across "
          f"{len(set(labels))} intents.")

    # ── 2. TF-IDF vectorization ───────────────────────────
    vectorizer = TfidfVectorizer(ngram_range=(1,2), stop_words='english')
    X = vectorizer.fit_transform(sentences)

    # ── 3. Train / test split ─────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # ── 4. Train Logistic Regression ──────────────────────
    model = LogisticRegression(
        max_iter=200,
        multi_class="multinomial",
        solver="lbfgs",
        C=10                   # slight regularization for small data
    )
    model.fit(X_train, y_train)

    # ── 5. Evaluate ───────────────────────────────────────
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n✔ Test Accuracy: {acc * 100:.2f}%\n")
    print(classification_report(y_test, y_pred, zero_division=0))

    # ── 6. Save model artifacts ───────────────────────────
    os.makedirs(MODEL_DIR, exist_ok=True)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    with open(LABEL_ENCODER_PATH, "wb") as f:
        pickle.dump(model.classes_, f)

    print(f"✔ Model saved to  : {MODEL_PATH}")
    print(f"✔ Vectorizer saved : {VECTORIZER_PATH}")
    print(f"✔ Labels saved     : {LABEL_ENCODER_PATH}")
    print("=" * 50)


# ── Allow running directly ────────────────────────────────
if __name__ == "__main__":
    train_model()
