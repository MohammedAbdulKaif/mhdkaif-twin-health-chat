from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# --------------------------------------------------
# Load knowledge.txt (section-based)
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_PATH = os.path.join(BASE_DIR, "data", "knowledge.txt")

sections = {}
current_section = None

if os.path.exists(KNOWLEDGE_PATH):
    with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].lower()
                sections[current_section] = []
            elif current_section:
                sections[current_section].append(line)

# --------------------------------------------------
# Predefined polite responses (NEW)
# --------------------------------------------------
small_talk = {
    "hi": "Hello! 👋 How can I help you with Twin Health today?",
    "hello": "Hi there! 👋 Feel free to ask about Twin Health.",
    "good morning": "Good morning! ☀️ How can I assist you with Twin Health?",
    "good afternoon": "Good afternoon! 😊 How can I help you today?",
    "good evening": "Good evening! 🌆 Let me know if you have questions about Twin Health.",
    "who are you": "I’m the Twin Health Assistant. I can help answer questions about Twin Health, ICAPP, coaching, and program features.",
    "what are you": "I’m a virtual assistant designed to provide information about Twin Health.",
    "thank you": "You’re welcome! 😊 Let me know if you need anything else.",
    "thankyou": "welcome",
    "thanks": "Happy to help! 👍",
    "bye": "Goodbye! 👋 Have a great day and take care.",
    "goodbye": "Goodbye! 👋 Feel free to come back anytime."
}

# --------------------------------------------------
# Section keyword mapping
# --------------------------------------------------
section_keywords = {
    "overview": ["twin health", "about twin health", "what is twin health"],
    "whole_body_digital_twin": ["digital twin", "whole body digital twin"],
    "icapp": ["icapp"],
    "coaching": ["coach", "coaching"],
    "nutrition_journey": ["nutrition", "food", "diet"],
    "care_team": ["care team", "support team"],
    "plans": ["plan", "pricing", "subscription"],
    "diabetes_reversal_approach": [
        "diabetes", "diabetes reversal", "type 2 diabetes",
        "metabolism", "metabolic health", "lifestyle disease"
    ]
}

# --------------------------------------------------
# Domain & medical filters
# --------------------------------------------------
domain_keywords = {
    "twin", "twin health", "digital twin", "icapp",
    "coach", "coaching", "nutrition", "care",
    "plan", "subscription", "metabolism", "diabetes"
}

medical_keywords = {
    "medicine", "tablet", "drug", "dosage", "diagnosis",
    "treatment", "cure", "insulin", "doctor",
    "hospital", "prescription", "therapy"
}

# --------------------------------------------------
# Routes
# --------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    user_input = data.get("message", "").lower().strip()

    if not user_input:
        return jsonify({"reply": "Please ask a question related to Twin Health."})

    # 1️⃣ Small talk handling (NEW – highest priority)
    for key, reply in small_talk.items():
        if user_input == key or user_input.startswith(key):
            return jsonify({"reply": reply})

    # 2️⃣ Medical block
    if any(word in user_input for word in medical_keywords):
        return jsonify({
            "reply": "I’m not a medical professional. Please consult your doctor or Twin Health care team."
        })

    # 3️⃣ Domain lock
    if not any(word in user_input for word in domain_keywords):
        return jsonify({
            "reply": "I can only answer questions related to Twin Health."
        })

    # 4️⃣ Section-based knowledge response
    for section, keywords in section_keywords.items():
        if any(key in user_input for key in keywords):
            content = sections.get(section, [])
            if content:
                response = (
                    f"Here’s some information about {section.replace('_', ' ').title()}:\n\n"
                    + " ".join(content)
                )
                return jsonify({"reply": response})

    # 5️⃣ Fallback inside domain
    return jsonify({
        "reply": (
            "I can help with Twin Health features, ICAPP, coaching, nutrition, "
            "metabolic health, and subscription plans. Please rephrase your question."
        )
    })

# --------------------------------------------------
# Run app
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
