import pickle
from training.feature_engineering import clean_text
from server.modules.extract_email import extract_email_fields

MODEL_PATH = "model/email_phishing_model.pkl"
VECTORIZER_PATH = "model/tfidf_vectorizer.pkl"


class EmailPhishingModel:
    def __init__(self):
        with open(MODEL_PATH, "rb") as f:
            self.model = pickle.load(f)

        with open(VECTORIZER_PATH, "rb") as f:
            self.vectorizer = pickle.load(f)

    def predict(self, text: str):
        X = self.vectorizer.transform([text])
        pred = self.model.predict(X)[0]
        prob = self.model.predict_proba(X)[0][1]
        return pred, float(prob)


model = EmailPhishingModel()


def predict_email(fields: dict):
    """
    fields = { "subject": "...", "from": "...", "body": "..." }
    """
    full_text = f"{fields.get('subject','')}\n{fields.get('from','')}\n{fields.get('body','')}"
    cleaned = clean_text(full_text)

    label, prob = model.predict(cleaned)

    return {
        "prediction": label,
        "probability": round(prob, 4),
        "subject": fields.get("subject", ""),
        "from": fields.get("from", ""),
    }