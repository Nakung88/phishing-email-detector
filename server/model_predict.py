# server/model_predict.py
import joblib
from training.feature_engineering import clean_text

MODEL_PATH = "model/email_phishing_model.pkl"
VECTORIZER_PATH = "model/tfidf_vectorizer.pkl"

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)

def predict_email(text: str):
    text = clean_text(text)
    X = vectorizer.transform([text])

    prob = model.predict_proba(X)[0][1]   # phishing probability
    label = "phishing" if prob >= 0.5 else "safe"

    return {
        "label": label,
        "risk": round(prob * 100, 2)
    }
