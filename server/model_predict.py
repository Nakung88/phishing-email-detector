# server/model_predict.py

import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

MODEL_PATH = "model/email_phishing_model.pkl"
VECTORIZER_PATH = "model/tfidf_vectorizer.pkl"


class EmailPhishingModel:
    def __init__(self):
        with open(MODEL_PATH, "rb") as f:
            self.model: LogisticRegression = pickle.load(f)

        with open(VECTORIZER_PATH, "rb") as f:
            self.vectorizer: TfidfVectorizer = pickle.load(f)

        self.feature_names = np.array(
            self.vectorizer.get_feature_names_out()
        )

    def predict_with_explanation(self, text: str):
        X = self.vectorizer.transform([text])

        prob = self.model.predict_proba(X)[0][1]
        label = "phishing" if prob >= 0.5 else "legitimate"

        tfidf_values = X.toarray()[0]
        weights = self.model.coef_[0]

        contribution = tfidf_values * weights
        top_idx = np.argsort(contribution)[-10:][::-1]

        keywords = [
            self.feature_names[i]
            for i in top_idx
            if contribution[i] > 0
        ]

        return {
            "label": label,
            "risk_score": round(prob * 100, 2),
            "keywords": keywords
        }


_model = EmailPhishingModel()


def predict_email(text: str):
    return _model.predict_with_explanation(text)
