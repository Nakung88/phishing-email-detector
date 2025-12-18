import joblib
import numpy as np
from server.modules.rules import rule_check

model = joblib.load("model/email_phishing_model.pkl")
vectorizer = joblib.load("model/tfidf_vectorizer.pkl")


DANGEROUS_KEYWORDS = [
    "verify", "urgent", "password", "otp", "login", "reset",
    "click", "confirm", "suspended", "limited", "won", "prize"
]

SAFE_KEYWORDS = [
    "no action required",
    "we will never ask",
    "this email confirms",
    "thank you for your payment",
    "manage your subscription"
]


def highlight_keywords(text, keywords):
    text_l = text.lower()
    return [kw for kw in keywords if kw in text_l]


def predict_email(text: str):
    reasons = []
    highlights = []

    text_l = text.lower()

    # =====================
    # 1️⃣ RULE-BASED FIRST
    # =====================
    rule_label, rule_reasons = rule_check(text)

    if rule_label == "SAFE":
        return (
            "SAFE",
            0.10,
            rule_reasons,
            0.10,
            highlight_keywords(text, SAFE_KEYWORDS)
        )

    if rule_label == "PHISHING":
        return (
            "PHISHING",
            0.95,
            rule_reasons,
            0.95,
            highlight_keywords(text, DANGEROUS_KEYWORDS)
        )

    # =====================
    # 2️⃣ ML PREDICTION
    # =====================
    X = vectorizer.transform([text])
    phishing_prob = float(model.predict_proba(X)[0][1])

    # 🔥 threshold สูงขึ้น
    label = "PHISHING" if phishing_prob >= 0.75 else "SAFE"

    reasons.append("ML_MODEL")

    # =====================
    # 3️⃣ Context downgrade
    # =====================
    if (
        label == "PHISHING"
        and "http" not in text_l
        and "click" not in text_l
        and "verify" not in text_l
        and "urgent" not in text_l
    ):
        label = "SAFE"
        phishing_prob *= 0.4
        reasons.append("No action / no link downgrade")

    # =====================
    # 4️⃣ Highlight (เฉพาะคำอันตราย)
    # =====================
    highlights = highlight_keywords(text, DANGEROUS_KEYWORDS)

    return (
        label,
        phishing_prob,
        reasons,
        phishing_prob,
        highlights
    )
