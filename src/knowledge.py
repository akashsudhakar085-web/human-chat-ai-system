"""
============================================================
knowledge.py  –  Knowledge Module for Hybrid Assistant
============================================================
Provides an intelligent fallback mechanism to answer general
knowledge queries using Wikipedia and rule-based matching.
============================================================
"""

import wikipedia
import re
import random

# Set language
wikipedia.set_lang("en")

# ============================
# 🔥 MANUAL KNOWLEDGE (NEW)
# ============================

MANUAL_KNOWLEDGE = {
    # Tamil Nadu Politics
    "tamil nadu cm": "M. K. Stalin is the current Chief Minister of Tamil Nadu since 2021.",
    "cm tamil nadu": "M. K. Stalin is the current Chief Minister of Tamil Nadu.",
    "mk stalin": "M. K. Stalin is an Indian politician and current CM of Tamil Nadu.",

    # India Politics
    "prime minister india": "Narendra Modi is the Prime Minister of India since 2014.",
    "pm india": "Narendra Modi is the current Prime Minister of India.",
    "president india": "Droupadi Murmu is the current President of India.",

    # Cricket
    "virat kohli": "Virat Kohli is one of the greatest Indian cricketers and former captain of India.",
    "dhoni": "MS Dhoni is a legendary Indian cricketer and former captain known for his leadership.",
    "cricket": "Cricket is a popular bat-and-ball sport played between two teams worldwide.",

    # Cinema
    "vijay": "Thalapathy Vijay is a leading Tamil actor and political figure.",
    "ajith": "Ajith Kumar is a popular Tamil actor known for action films.",
    "kollywood": "Kollywood refers to the Tamil film industry based in Chennai.",

    # Technology
    "ai": "Artificial Intelligence enables machines to simulate human intelligence.",
    "machine learning": "Machine Learning is a subset of AI that learns from data.",
    "python": "Python is a powerful programming language used in AI and development.",

    # Finance
    "stock market": "Stock market is where shares of companies are bought and sold.",
    "bitcoin": "Bitcoin is a decentralized digital currency without central authority.",
    "crypto": "Cryptocurrency is digital money secured using cryptography.",

    # General
    "elon musk": "Elon Musk is a billionaire entrepreneur known for Tesla, SpaceX, and X.",
    "india": "India is a country in South Asia and the world's largest democracy."
}

# ============================
# 🔥 HELPER FUNCTION (NEW)
# ============================

def get_manual_answer(query: str) -> tuple[str|None, str|None]:
    """
    Check manual knowledge with flexible matching.
    Returns (response, matched_entity)
    """
    for key in MANUAL_KNOWLEDGE:
        if all(word in query for word in key.split()):
            prefixes = [
                "Boss, ",
                "Here's what I know, boss: ",
                "Got it boss, "
            ]
            return f"{random.choice(prefixes)}{MANUAL_KNOWLEDGE[key]}", key
    return None, None


# ============================
# EXISTING CODE (UNCHANGED)
# ============================

def get_wikipedia_summary(query: str) -> tuple[str|None, str|None]:
    try:
        summary = wikipedia.summary(query, sentences=1)
        prefixes = [
            f"Here's what I found, boss: ",
            f"Boss, ",
            f"According to my databanks, boss: "
        ]
        return f"{random.choice(prefixes)}{summary} 💡", query
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            summary = wikipedia.summary(e.options[0], sentences=1)
            return f"Boss, {summary} 💡", e.options[0]
        except:
            return "That topic is a bit too broad 🤔. Could you be more specific?", None
    except wikipedia.exceptions.PageError:
        return "I couldn't find any information on that. 🤔 Are you sure about the name?", None
    except Exception as e:
        return "I encountered an error trying to look that up. My apologies! 🔧", None


def extract_query(text: str) -> str:
    text = text.lower().strip()

    fillers = ["tell me", "about", "explain", "please", "can you", "what do you know"]
    for f in fillers:
        text = text.replace(f, "").strip()
        
    patterns = [
        r"^who is the (.*)",
        r"^who is (.*)",
        r"^what is a (.*)",
        r"^what is an (.*)",
        r"^what is the (.*)",
        r"^what is (.*)",
        r"^define (.*)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            extracted = match.group(1).replace("?", "").strip()
            return extracted
            
    return text.replace("?", "").strip()


def answer_general_knowledge(user_msg: str) -> tuple[str|None, str|None]:
    topic = extract_query(user_msg)
    
    if not topic or len(topic) < 2:
        return None, None

    # 🔥 STEP 1: Manual knowledge FIRST (NEW)
    manual_resp, manual_entity = get_manual_answer(topic)
    if manual_resp:
        return manual_resp, manual_entity

    # 🔥 STEP 2: Wikipedia fallback
    wiki_resp, wiki_entity = get_wikipedia_summary(topic)
    
    if wiki_resp and "I couldn't find any information" in wiki_resp:
        return None, None
        
    return wiki_resp, wiki_entity