"""
============================================================
context_manager.py  –  Conversation Context & Memory
============================================================
Maintains per-session state so the chatbot can handle
follow-up questions and basic pronoun resolution.

Stores:
  • Last recognized intent
  • Key entities (person name, topic)
  • Simple pronoun → entity mapping
============================================================
"""


class ContextManager:
    """
    Lightweight in-memory context store.

    Each user session gets its own ContextManager instance
    (managed by the Flask app via session or a dict).
    """

    # Pronouns that should resolve to the stored person entity
    PERSON_PRONOUNS = {
        "he", "she", "him", "her", "his", "hers",
        "they", "them", "their", "theirs",
    }

    # Pronouns / phrases that refer to the current topic
    TOPIC_PRONOUNS = {"it", "that", "this", "about it", "about that"}

    def __init__(self):
        """Initialize an empty context."""
        self.last_intent = None          # e.g. "president_india"
        self.last_entities = {}          # e.g. {"person": "...", "topic": "..."}
        self.conversation_turns = []     # list of (user_msg, bot_msg) tuples

    # ── Setters ────────────────────────────────────────────

    def set_intent(self, intent: str):
        """Store the most recently recognized intent tag."""
        self.last_intent = intent

    def set_entities(self, entities: dict):
        """
        Merge new entities into the context.
        Existing keys are overwritten if the new dict has them.
        """
        if entities:
            self.last_entities.update(entities)

    def add_turn(self, user_msg: str, bot_msg: str):
        """
        Record a conversation turn for reference.
        Keep only the last 10 turns to save memory.
        """
        self.conversation_turns.append((user_msg, bot_msg))
        if len(self.conversation_turns) > 10:
            self.conversation_turns = self.conversation_turns[-10:]

    def set_context(self, topic: str | None = None, entity: str | None = None):
        """Explicitly store the last topic or entity."""
        if topic:
            self.last_entities["topic"] = topic
        if entity:
            self.last_entities["person"] = entity

    def get_context(self) -> dict:
        """Return the current active context entities."""
        return {
            "topic": self.last_entities.get("topic"),
            "entity": self.last_entities.get("person")
        }

    # ── Getters ────────────────────────────────────────────

    def get_last_intent(self) -> str:
        """Return the last intent, or None."""
        return self.last_intent

    def get_entity(self, key: str) -> str:
        """Return a stored entity value (e.g. 'person'), or None."""
        return self.last_entities.get(key)

    # ── Pronoun Resolution ─────────────────────────────────

    def resolve_pronouns(self, text: str) -> str:
        """
        Very basic pronoun resolution:
        Replace personal pronouns with the stored person entity
        and topic pronouns with the stored topic entity.

        Example conversation flow:
          User: "Who is the president of India?"
          Bot : "Droupadi Murmu …"   → context stores person
          User: "How old is she?"
          →  resolved to: "How old is Droupadi Murmu?"
        """
        words = text.lower().split()

        person = self.last_entities.get("person")
        topic = self.last_entities.get("topic")

        resolved_words = []
        for word in words:
            clean_word = word.strip("?!.,;:")
            if person and clean_word in self.PERSON_PRONOUNS:
                resolved_words.append(person)
            elif topic and clean_word in self.TOPIC_PRONOUNS:
                resolved_words.append(topic)
            else:
                resolved_words.append(word)

        return " ".join(resolved_words)

    # ── Reset ──────────────────────────────────────────────

    def reset(self):
        """Clear all context (for a new session)."""
        self.last_intent = None
        self.last_entities = {}
        self.conversation_turns = []

    # ── String representation (debugging) ──────────────────

    def __repr__(self):
        return (
            f"ContextManager(intent={self.last_intent}, "
            f"entities={self.last_entities}, "
            f"turns={len(self.conversation_turns)})"
        )
