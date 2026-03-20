# Project Report: Human–Computer Interaction Using Chatbots

---

## 1. Aim

To design and implement an intelligent chatbot that demonstrates effective **Human-Computer Interaction (HCI)** by being interactive, adaptive, and user-friendly, using Natural Language Processing and Machine Learning techniques.

---

## 2. Objectives

1. Build an NLP-based chatbot that understands user queries and responds intelligently.
2. Implement an intent classification model using Machine Learning (Logistic Regression).
3. Integrate sentiment detection to adapt responses based on user mood.
4. Maintain context-aware conversations with basic memory and pronoun resolution.
5. Provide a clean, responsive web-based user interface following HCI usability principles.
6. Include optional voice input/output capabilities with graceful fallback.
7. Store conversation history in a persistent database (SQLite).

---

## 3. Methodology

### 3.1 Dataset Preparation
- Created a custom dataset (`intents.json`) containing **30 intents** covering greetings, college info, help desk, AI/ML topics, emotions, and general knowledge.
- Each intent has 5–10 example patterns and 2–4 response templates.
- Some intents include entity annotations for context tracking.

### 3.2 Text Preprocessing
- **Cleaning**: Lowercasing, removal of special characters.
- **Tokenization**: Splitting text into words using NLTK `word_tokenize`.
- **Lemmatization**: Reducing words to root form using `WordNetLemmatizer`.

### 3.3 Feature Extraction
- Applied **TF-IDF Vectorization** to convert preprocessed text into numerical feature vectors.

### 3.4 Intent Classification
- Trained a **Logistic Regression** model (`sklearn`) for multi-class intent prediction.
- Used `predict_proba()` to obtain confidence scores.
- Implemented a **confidence threshold** (35%): below this, the bot returns a fallback response asking the user to rephrase.

### 3.5 Sentiment Analysis
- Used **NLTK VADER** (Valence Aware Dictionary and sEntiment Reasoner) for rule-based sentiment analysis.
- Classifies user input as positive, negative, or neutral.
- Bot adapts its tone based on detected sentiment.

### 3.6 Context Management
- Stores the last recognized intent and key entities (person, topic).
- Implements **basic pronoun resolution**: replaces pronouns like "he/she/it" with the stored entity.
- Example: "Who is the president?" → stores "Droupadi Murmu" → "How old is she?" resolves to "How old is Droupadi Murmu?"

### 3.7 User Interface
- Built with **Flask** (Python web framework) serving HTML/CSS/JS.
- Follows HCI principles:
  - **Visibility**: Chat messages are clearly distinguished (bot vs. user).
  - **Feedback**: Typing indicator ("Bot is typing…") and confidence badges.
  - **Consistency**: Uniform design language throughout.
  - **Affordance**: Clear input field and send button.
  - **Responsiveness**: Works on desktop and mobile screens.

### 3.8 Voice Module (Optional)
- **Speech-to-Text**: `SpeechRecognition` library with Google Speech API.
- **Text-to-Speech**: `pyttsx3` for offline speech synthesis.
- **Fallback**: If microphone or API fails, automatically switches to text input.

### 3.9 Chat History
- All conversations are stored in an **SQLite database** with fields: user message, bot response, timestamp, and sentiment label.

---

## 4. Tools & Technologies

| Component | Technology |
|---|---|
| Language | Python 3.x |
| NLP | NLTK (tokenization, lemmatization, VADER) |
| ML Model | Logistic Regression (scikit-learn) |
| Feature Extraction | TF-IDF Vectorizer |
| Web Framework | Flask |
| Frontend | HTML5, CSS3, JavaScript |
| Database | SQLite |
| Voice (Optional) | SpeechRecognition, pyttsx3 |

---

## 5. Results

- The intent classification model achieved **high accuracy** on the training/test split, correctly identifying intents from user messages.
- The chatbot successfully:
  - Responds to 30 different intent categories.
  - Detects user sentiment and adjusts response tone accordingly.
  - Maintains context across turns and resolves basic pronouns.
  - Provides clear confidence indicators on each response.
  - Falls back gracefully when confidence is low.
- The web interface provides a smooth, responsive chat experience with typing delay simulation and sentiment badges.

---

## 6. Conclusion

This project successfully demonstrates effective **Human-Computer Interaction** through a chatbot system that is:

- **Interactive**: Real-time responses with natural conversation flow.
- **Adaptive**: Adjusts behavior based on user sentiment and conversation context.
- **User-Friendly**: Clean, minimal UI with clear visual feedback and responsive design.
- **Intelligent**: Uses ML-based intent classification with confidence thresholding.
- **Accessible**: Supports both text and voice input modes with automatic fallback.

The system proves that even lightweight ML models combined with strong HCI principles can deliver a compelling and effective user experience. The modular architecture allows easy extension with more intents, improved NLP, or integration with external APIs in the future.

---

## 7. Future Scope

- Integrate larger pre-trained language models for more natural responses.
- Add multi-language support.
- Implement user authentication and personalized profiles.
- Deploy on cloud platforms for public access.
- Add a feedback loop to retrain the model from user interactions.
