/* ============================================================
   script.js  –  HCI Chatbot – Frontend Logic
   ============================================================
   Handles:
     • Sending messages via AJAX to the Flask API
     • Rendering messages with typing-delay simulation
     • Voice toggle and microphone input
     • Sentiment badge display
     • Clear chat history
   ============================================================ */

// ── DOM References ───────────────────────────────────────
const chatMessages     = document.getElementById("chat-messages");
const userInput        = document.getElementById("user-input");
const sendBtn          = document.getElementById("send-btn");
const micBtn           = document.getElementById("mic-btn");
const voiceToggleBtn   = document.getElementById("voice-toggle-btn");
const clearBtn         = document.getElementById("clear-btn");
const typingIndicator  = document.getElementById("typing-indicator");
const sentimentBadge   = document.getElementById("sentiment-badge");
const voiceToast       = document.getElementById("voice-toast");
const statusText       = document.getElementById("status-text");

// ── State ────────────────────────────────────────────────
let voiceEnabled = false;      // Is voice mode active?
let isProcessing = false;      // Prevent double-send

// ── Helpers ──────────────────────────────────────────────

/** Get a short time string like "12:34 PM" */
function getTimeStr() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

/** Scroll chat to the bottom smoothly */
function scrollToBottom() {
    chatMessages.scrollTo({ top: chatMessages.scrollHeight, behavior: "smooth" });
}

/** Show/hide an element by toggling the "hidden" class */
function setVisible(el, visible) {
    el.classList.toggle("hidden", !visible);
}

// ── Typing Indicator ─────────────────────────────────────

function showTyping() {
    setVisible(typingIndicator, true);
    scrollToBottom();
}

function hideTyping() {
    setVisible(typingIndicator, false);
}

// ── Render Messages ──────────────────────────────────────

/**
 * Append a message bubble to the chat area.
 * @param {string} text      – message text (supports HTML)
 * @param {"bot"|"user"} who – sender
 * @param {object} meta      – optional { confidence, sentiment }
 */
function addMessage(text, who, meta = {}) {
    const msg = document.createElement("div");
    msg.className = `message ${who}-message`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.textContent = who === "bot" ? "🤖" : "👤";

    const content = document.createElement("div");
    content.className = "message-content";

    const p = document.createElement("p");
    p.innerHTML = text;
    content.appendChild(p);

    // Confidence badge for bot messages
    if (who === "bot" && meta.confidence !== undefined) {
        const badge = document.createElement("span");
        const conf  = meta.confidence;
        let level   = "confidence-high";
        if (conf < 0.4) level = "confidence-low";
        else if (conf < 0.7) level = "confidence-mid";
        badge.className = `confidence-badge ${level}`;
        badge.textContent = `${(conf * 100).toFixed(0)}%`;
        content.appendChild(badge);
    }

    // Timestamp
    const time = document.createElement("span");
    time.className = "message-time";
    time.textContent = getTimeStr();
    content.appendChild(time);

    msg.appendChild(avatar);
    msg.appendChild(content);
    chatMessages.appendChild(msg);
    scrollToBottom();
}

// ── Sentiment Badge ──────────────────────────────────────

function showSentiment(sentimentData) {
    if (!sentimentData) return;
    const label = sentimentData.label || "neutral";
    const emojis = { positive: "😊", negative: "😟", neutral: "😐" };
    sentimentBadge.textContent = `Mood: ${emojis[label] || ""} ${label}`;
    setVisible(sentimentBadge, true);

    // Auto-hide after 3 seconds
    setTimeout(() => setVisible(sentimentBadge, false), 3000);
}

// ── Voice Toast ──────────────────────────────────────────

function showToast(message, duration = 2500) {
    voiceToast.textContent = message;
    setVisible(voiceToast, true);
    setTimeout(() => setVisible(voiceToast, false), duration);
}

// ── Send Message ─────────────────────────────────────────

async function sendMessage(text) {
    if (!text.trim() || isProcessing) return;

    isProcessing = true;
    addMessage(text, "user");
    userInput.value = "";

    // Show typing indicator with a simulated delay
    showTyping();

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text }),
        });
        const data = await res.json();

        // Simulate dynamic typing delay based on message length
        const textLength = data.response ? data.response.length : 0;
        const delay = Math.min(3000, Math.max(500, textLength * 30));
        await new Promise(r => setTimeout(r, delay));

        hideTyping();
        addMessage(data.response, "bot", {
            confidence: data.confidence,
            sentiment: data.sentiment,
        });
        showSentiment(data.sentiment);

        // If voice is on, speak the response
        if (voiceEnabled) {
            fetch("/api/voice/speak", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: data.response }),
            });
        }

    } catch (err) {
        hideTyping();
        addMessage("⚠️ Connection error. Please try again.", "bot");
    }

    isProcessing = false;
}

// ── Event Listeners ──────────────────────────────────────

// Send on button click
sendBtn.addEventListener("click", () => {
    sendMessage(userInput.value);
});

// Send on Enter key
userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage(userInput.value);
    }
});

// ── Voice Toggle ─────────────────────────────────────────

voiceToggleBtn.addEventListener("click", async () => {
    voiceEnabled = !voiceEnabled;
    voiceToggleBtn.classList.toggle("active", voiceEnabled);
    setVisible(micBtn, voiceEnabled);

    if (voiceEnabled) {
        // Check if voice features are available on the server
        try {
            const res = await fetch("/api/voice/status");
            const status = await res.json();
            if (!status.stt) {
                showToast("⚠️ Speech Recognition not installed – text only");
                voiceEnabled = false;
                voiceToggleBtn.classList.remove("active");
                setVisible(micBtn, false);
            } else {
                showToast("🎤 Voice mode enabled");
            }
        } catch {
            showToast("⚠️ Could not check voice status");
            voiceEnabled = false;
            voiceToggleBtn.classList.remove("active");
            setVisible(micBtn, false);
        }
    } else {
        showToast("Voice mode disabled");
    }
});

// ── Microphone Button ────────────────────────────────────

micBtn.addEventListener("click", async () => {
    if (isProcessing) return;

    showToast("🎤 Listening…", 4000);
    micBtn.style.opacity = "0.5";

    try {
        const res = await fetch("/api/voice/listen", { method: "POST" });
        const data = await res.json();

        if (data.text) {
            // Successfully recognized speech
            userInput.value = data.text;
            showToast(`Heard: "${data.text}"`);
            sendMessage(data.text);
        } else {
            // Fallback to text input
            showToast("⚠️ Couldn't hear you — please type instead");
            userInput.focus();
        }
    } catch {
        showToast("⚠️ Voice error — switching to text input");
        userInput.focus();
    }

    micBtn.style.opacity = "1";
});

// ── Clear Chat ───────────────────────────────────────────

clearBtn.addEventListener("click", async () => {
    if (!confirm("Clear all chat history?")) return;

    try {
        await fetch("/api/clear", { method: "POST" });

        // Remove all messages except the welcome message
        const messages = chatMessages.querySelectorAll(".message");
        messages.forEach((msg, i) => { if (i > 0) msg.remove(); });

        showToast("Chat cleared ✓");
    } catch {
        showToast("⚠️ Could not clear history");
    }
});

// ── Initial Focus ────────────────────────────────────────
userInput.focus();
