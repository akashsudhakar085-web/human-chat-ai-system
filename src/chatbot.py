"""
============================================================
chatbot.py  –  Core Chatbot Engine
============================================================
Ties together:
  • Intent classification  (Logistic Regression + TF-IDF)
  • Confidence thresholding (predict_proba)
  • Sentiment-aware responses
  • Context management (follow-up questions)
  • Response selection from intents.json
============================================================
"""

import json
import os
import pickle
import random

from src.nlp_utils import preprocess
from src.sentiment import analyze_sentiment, get_sentiment_emoji
from src.context_manager import ContextManager
from src.knowledge import answer_general_knowledge

# ── Paths ──────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "intents.json")
MODEL_PATH = os.path.join(BASE_DIR, "model", "intent_model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "model", "tfidf_vectorizer.pkl")

# ── Confidence threshold ──────────────────────────────────
CONFIDENCE_THRESHOLD = 0.7

# ── Fallback responses ────────────────────────────────────
FALLBACK_RESPONSES = [
    "Let me think, boss 🤔",
    "That’s a tricky one, boss. Can you clarify a bit?",
]

# ── Sentiment-adaptive prefixes ───────────────────────────
SENTIMENT_PREFIXES = {
    "positive": [
        "That's awesome! 😄 I'm glad to hear that! ",
        "Great to hear! 😄 ",
    ],
    "negative": [
        "I'm really sorry you're feeling this way. 💙 I'm here for you. ",
        "I understand that can be frustrating. Let's see how I can help. ",
    ],
    "neutral": [""],
}


class ChatBot:
    """
    Main chatbot class – instantiate once per app,
    then call `get_response(user_msg, ctx)` per message.
    """

    def __init__(self):
        """Load the trained model, vectorizer, and intents data."""
        # Load intents
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            self.intents = json.load(f)

        # Build a quick lookup: tag → intent dict
        self.intent_map = {
            intent["tag"]: intent for intent in self.intents["intents"]
        }

        # Load ML artifacts
        with open(MODEL_PATH, "rb") as f:
            self.model = pickle.load(f)

        with open(VECTORIZER_PATH, "rb") as f:
            self.vectorizer = pickle.load(f)

    # ──────────────────────────────────────────────────────
    #  Public API
    # ──────────────────────────────────────────────────────

    def get_response(self, user_msg: str, ctx: ContextManager) -> dict:
        """
        Generate a response for the user's message.

        Parameters
        ----------
        user_msg : Raw text from the user.
        ctx      : The user's ContextManager instance.

        Returns
        -------
        dict with keys:
            response   : str   – the bot's reply
            intent     : str   – predicted intent tag
            confidence : float – model's confidence
            sentiment  : dict  – sentiment analysis result
        """
        # 0. Quick Manual Intents
        # Avoid ML matching errors for purely exact matches
        clean_msg = user_msg.lower().strip()
        quick_intents = ["hello", "hi", "hey", "vanakkam", "thanks", "thank you", "thanks jarvis"]
        if any(word == clean_msg or clean_msg.startswith(word + " ") for word in quick_intents):
            if "thank" in clean_msg:
                return {
                    "response": self._apply_sentiment("You're very welcome, boss! 😊", analyze_sentiment(user_msg), "greeting"),
                    "intent": "greeting",
                    "confidence": 1.0,
                    "sentiment": analyze_sentiment(user_msg),
                }

            intent_data = self.intent_map.get("greeting", {})
            # If dataset has greeting responses, use them; otherwise defaults
            default_greetings = [
                "Hello boss 😎, JARVIS online. How can I assist you?",
                "Right here, boss. What do you need? ✨",
                "Greetings boss! Systems are online."
            ]
            response = random.choice(intent_data.get("responses", default_greetings))
            return {
                "response": self._apply_sentiment(response, analyze_sentiment(user_msg), "greeting"),
                "intent": "greeting",
                "confidence": 1.0,
                "sentiment": analyze_sentiment(user_msg),
            }

        # 1. Sentiment analysis on the raw message
        sentiment = analyze_sentiment(user_msg)

        # 2. Resolve pronouns using context
        resolved_msg = ctx.resolve_pronouns(user_msg)

        # 3. Preprocess for the model
        processed = preprocess(resolved_msg)

        # 4. Predict intent + confidence
        X = self.vectorizer.transform([processed])
        proba = self.model.predict_proba(X)[0]
        max_idx = proba.argmax()
        confidence = float(proba[max_idx])
        predicted_tag = self.model.classes_[max_idx]

        # ── DEBUG: Print to terminal for testing ──────────
        print(f"[DEBUG] Input: '{user_msg}' | Processed: '{processed}' "
              f"| Intent: '{predicted_tag}' | Confidence: {confidence:.3f}")

        # 5. Check confidence threshold and implement Tiered Routing
        if confidence > CONFIDENCE_THRESHOLD:
            # High confidence -> ML Intent (Skip Knowledge API)
            pass # Continues to step 6
            
        else:
            # Medium or Low confidence -> Ask Knowledge Module
            knowledge_response, knowledge_entity = answer_general_knowledge(user_msg)
            
            if knowledge_response:
                # Store the extracted entity into context memory
                ctx.set_context(topic=knowledge_entity, entity=knowledge_entity)
                
                if confidence > 0.4:
                    # Medium confidence -> Try Knowledge Mix, else Intent
                    intent_data = self.intent_map.get(predicted_tag, {})
                    intent_responses = intent_data.get("responses", [""])
                    intent_resp = random.choice(intent_responses) if intent_responses else ""
                    
                    final_resp = f"{knowledge_response} Also, {intent_resp.lower()}"
                    return {
                        "response": self._apply_sentiment(final_resp, sentiment),
                        "intent": f"{predicted_tag} (mixed)",
                        "confidence": round(float(confidence), 3),
                        "sentiment": sentiment,
                    }
                else:
                    # Low confidence -> Strict Knowledge Fallback
                    return {
                        "response": self._apply_sentiment(knowledge_response, sentiment),
                        "intent": "general_knowledge",
                        "confidence": round(float(confidence), 3),
                        "sentiment": sentiment,
                    }

            # Knowledge failed, check if we can fall back to intent
            if confidence <= 0.4:
                # ── Standard Fallback ──
                response = random.choice(FALLBACK_RESPONSES)
                return {
                    "response": self._apply_sentiment(response, sentiment),
                    "intent": "unknown",
                    "confidence": round(float(confidence), 3),
                    "sentiment": sentiment,
                }

        # 6. Fetch a random response for the predicted intent
        intent_data = self.intent_map.get(predicted_tag, {})
        responses = intent_data.get("responses", FALLBACK_RESPONSES)
        response = random.choice(responses)

        # 7. Add sentiment-aware prefix (skip if intent already emotional)
        emotional_intents = {"sad", "happy", "angry", "compliment", "insult"}
        if predicted_tag not in emotional_intents:
            prefix = random.choice(
                SENTIMENT_PREFIXES.get(sentiment["label"], [""])
            )
            response = prefix + response

        # 8. Update context
        ctx.set_intent(predicted_tag)
        if "entities" in intent_data:
            ctx.set_entities(intent_data["entities"])
        ctx.add_turn(user_msg, response)

        return {
            "response": response,
            "intent": predicted_tag,
            "confidence": round(float(confidence), 3),
            "sentiment": sentiment,
        }

    def _apply_sentiment(self, response: str, sentiment: dict, intent: str = "unknown") -> str:
        """Helper to prefix response based on sentiment."""
        emotional_intents = {"sad", "happy", "angry", "compliment", "insult"}
        if intent not in emotional_intents:
            prefix = random.choice(
                SENTIMENT_PREFIXES.get(sentiment.get("label", "neutral"), [""])
            )
            return prefix + response
        return response
