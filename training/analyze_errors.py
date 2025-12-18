# training/analyze_errors.py
import os
import pandas as pd
import joblib
from sklearn.metrics import confusion_matrix, classification_report

DATA_PATH = "dataset/PROCESSED/train.csv"
MODEL_PATH = "model/email_phishing_model.pkl"
VECT_PATH = "model/tfidf_vectorizer.pkl"
OUT_DIR = "analysis"

os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)
df["text"] = df["text"].astype(str)
df["label"] = df["label"].astype(int)

X = df["text"]
y_true = df["label"]

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECT_PATH)

X_vec = vectorizer.transform(X)
y_pred = model.predict(X_vec)

print("📊 Confusion Matrix")
print(confusion_matrix(y_true, y_pred))

print("\n📋 Classification Report")
print(classification_report(y_true, y_pred, target_names=["SAFE", "PHISHING"]))

# --- Error rows only ---
errors = df[y_true != y_pred].copy()
errors["predicted"] = y_pred[y_true != y_pred]

# --- Feature analysis (ตรงนี้แหละที่คุณถาม) ---
errors["len"] = errors["text"].str.len()
errors["has_url"] = errors["text"].str.contains("http", case=False, na=False)
errors["has_brand"] = errors["text"].str.contains(
    r"paypal|bank|microsoft|google|account|verify|login",
    case=False,
    regex=True,
    na=False
)

errors.to_csv(f"{OUT_DIR}/errors.csv", index=False)

print(f"\n❌ Errors saved to analysis/errors.csv ({len(errors)} rows)")
