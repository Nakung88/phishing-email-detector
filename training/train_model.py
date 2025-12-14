# training/train_model.py

import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from joblib import dump
from training.feature_engineering import clean_text

PHISHING_DIR = "dataset/PHISHING"
HAM_DIR = "dataset/HAM"

MODEL_PATH = "model/email_phishing_model.pkl"
VECTORIZER_PATH = "model/tfidf_vectorizer.pkl"

TARGET_ROWS = 120000   # ไม่ต้องเท่ากันเป๊ะ ลด false positive


def load_folder(folder):
    dfs = []
    for f in os.listdir(folder):
        if f.endswith(".csv"):
            path = os.path.join(folder, f)
            print(f"[LOAD] {path}")
            df = pd.read_csv(path, encoding="latin1")
            dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def normalize(df):
    if "text_combined" in df.columns:
        df["subject"] = ""
        df["body"] = df["text_combined"]
    df["subject"] = df.get("subject", "").astype(str)
    df["body"] = df.get("body", "").astype(str)
    df["label"] = df["label"].astype(int)
    return df[["subject", "body", "label"]]


def sample(df, n):
    return df.sample(n, random_state=42) if len(df) > n else df


def train():
    print("Loading datasets...")
    phish = normalize(load_folder(PHISHING_DIR))
    ham = normalize(load_folder(HAM_DIR))

    phish = sample(phish, TARGET_ROWS)
    ham = sample(ham, TARGET_ROWS * 1.3)  # ham เยอะกว่าเล็กน้อย

    df = pd.concat([phish, ham]).sample(frac=1).reset_index(drop=True)

    print("Cleaning...")
    df["text"] = (
        df["subject"].apply(clean_text) + " " +
        df["body"].apply(clean_text)
    )

    print("Vectorizing...")
    vectorizer = TfidfVectorizer(
        max_features=60000,
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.9,
        sublinear_tf=True,
        stop_words="english"
    )
    X = vectorizer.fit_transform(df["text"])
    y = df["label"]

    print("Training Logistic Regression...")
    model = LogisticRegression(
        max_iter=3000,
        class_weight="balanced",
        C=2.0,
        solver="liblinear"
    )
    model.fit(X, y)

    os.makedirs("model", exist_ok=True)
    dump(model, MODEL_PATH)
    dump(vectorizer, VECTORIZER_PATH)

    print("✅ Training finished")
    print("Model saved:", MODEL_PATH)
    print("Vectorizer saved:", VECTORIZER_PATH)


if __name__ == "__main__":
    train()
