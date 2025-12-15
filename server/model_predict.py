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
