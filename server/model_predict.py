
# server/model_predict.py

import joblib
import numpy as np
from pathlib import Path
from server.modules.extract_email import extract_email_text
from training.feature_engineering import extract_features

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "model" / "email_phishing_model.pkl"
VEC_PATH = BASE_DIR / "model" / "tfidf_vectorizer.pkl"

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VEC_PATH)


def predict_email(email_file):
    """
    รับไฟล์ .eml (UploadFile)
    คืนค่า dict:
    {
        label: "PHISHING" | "SAFE",
        risk_percent: float,
        features: dict
    }
    """

    # 1) extract text จาก .eml
    text = extract_email_text(email_file)

    if not text or len(text.strip()) < 20:
        return {
            "label": "SAFE",
            "risk_percent": 0.0,
            "features": {}
        }

    # 2) TF-IDF
    X_text = vectorizer.transform([text])

    # 3) extra features
    feats = extract_features(text)
    X_extra = np.array(list(feats.values())).reshape(1, -1)

    # 4) รวม features
    X = np.hstack([X_text.toarray(), X_extra])

    # 5) predict
    prob = model.predict_proba(X)[0]
    phishing_prob = prob[1] * 100

    label = "PHISHING" if phishing_prob >= 50 else "SAFE"

    return {
        "label": label,
        "risk_percent": round(phishing_prob, 2),
        "features": feats
    }

import joblib
import re
from pathlib import Path

# ===============================
# Load model & vectorizer
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent

model = joblib.load(BASE_DIR / "model" / "email_phishing_model.pkl")
vectorizer = joblib.load(BASE_DIR / "model" / "tfidf_vectorizer.pkl")

# ===============================
# Thresholds
# ===============================
PHISHING_THRESHOLD = 0.70
STRONG_PHISHING_THRESHOLD = 0.85  # ถ้าเกินนี้ = phishing แน่นอน

# ===============================
# Indicators
# ===============================
PHISHING_KEYWORDS = [
    "verify your account",
    "urgent",
    "suspend",
    "unusual activity",
    "confirm your identity",
    "security alert",
    "click below",
    "reset your password",
]

TRUSTED_DOMAINS = [
    "microsoft.com",
    "github.com",
    "google.com",
    "accounts.google.com",
]

# ===============================
# Helpers
# ===============================
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def has_strong_phishing_signal(text: str) -> bool:
    return any(k in text for k in PHISHING_KEYWORDS)


def trusted_domain_present(text: str) -> bool:
    return any(d in text for d in TRUSTED_DOMAINS)


# ===============================
# Main
# ===============================
def predict_email(text: str):
    if not text or len(text) < 30:
        return "safe", 0.0

    cleaned = clean_text(text)
    X = vectorizer.transform([cleaned])

    phishing_prob = model.predict_proba(X)[0][1]
    risk = phishing_prob * 100

    # 🚨 กรณี phishing ชัดมาก → ไม่สน domain
    if phishing_prob >= STRONG_PHISHING_THRESHOLD:
        return "phishing", round(risk, 2)

    # ⚖️ กรณีกลาง → ใช้ logic เสริม
    if phishing_prob >= PHISHING_THRESHOLD:
        if has_strong_phishing_signal(cleaned):
            return "phishing", round(risk, 2)

        if trusted_domain_present(cleaned):
            # ลดความเสี่ยงเล็กน้อยเท่านั้น
            return "safe", round(risk * 0.9, 2)

        return "phishing", round(risk, 2)

    # 🟢 ความเสี่ยงต่ำ
    return "safe", round(risk, 2)

