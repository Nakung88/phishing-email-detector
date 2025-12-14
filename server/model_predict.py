import joblib
import re
import numpy as np
from pathlib import Path

# ===============================
# Load model & vectorizer
# ===============================
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "model" / "email_phishing_model.pkl"
VECTORIZER_PATH = BASE_DIR / "model" / "tfidf_vectorizer.pkl"

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

# ===============================
# Config
# ===============================
PHISHING_THRESHOLD = 0.75  # ปรับได้ (0.7–0.8 แนะนำ)

TRUSTED_DOMAINS = [
    "microsoft.com",
    "login.microsoftonline.com",
    "github.com",
    "google.com",
    "accounts.google.com",
    "facebook.com"
]

# ===============================
# Helper functions
# ===============================
def clean_text(text: str) -> str:
    """
    ทำความสะอาดข้อความก่อนส่งเข้าโมเดล
    - ลบ URL
    - ลบตัวอักษรแปลก
    """
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)   # remove URLs
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def trusted_domain_score(text: str) -> float:
    """
    ลดความเสี่ยง ถ้าเจอ domain ที่เชื่อถือได้
    """
    for domain in TRUSTED_DOMAINS:
        if domain in text:
            return -0.20   # ลด risk 20%
    return 0.0


# ===============================
# Main prediction function
# ===============================
def predict_email(text: str):
    """
    Returns:
        label: 'phishing' | 'safe'
        risk_percent: float
    """

    if not text or len(text.strip()) < 20:
        return "safe", 0.0

    cleaned_text = clean_text(text)

    # Vectorize
    X = vectorizer.transform([cleaned_text])

    # Predict probability
    phishing_prob = model.predict_proba(X)[0][1]

    # Adjust score with trusted domain
    phishing_prob += trusted_domain_score(cleaned_text)

    # Clamp value
    phishing_prob = max(0.0, min(phishing_prob, 1.0))

    risk_percent = round(phishing_prob * 100, 2)

    # Final decision
    if phishing_prob >= PHISHING_THRESHOLD:
        return "phishing", risk_percent
    else:
        return "safe", risk_percent
