import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from joblib import dump

from training.feature_engineering import clean_text

PHISHING_DIR = "dataset/PHISHING"
HAM_DIR = "dataset/HAM"

MODEL_PATH = "model/email_phishing_model.pkl"
VECTORIZER_PATH = "model/tfidf_vectorizer.pkl"

TARGET_ROWS_PER_CLASS = 150000   # ใช้ RAM ใหม่ให้คุ้ม 😄


def normalize_dataframe(df):
    cols = df.columns

    if "text_combined" in cols:
        return pd.DataFrame({
            "text": df["text_combined"].astype(str),
            "label": df["label"].astype(int)
        })

    subject = df["subject"].astype(str) if "subject" in cols else ""
    body = df["body"].astype(str) if "body" in cols else ""

    return pd.DataFrame({
        "text": subject + " " + body,
        "label": df["label"].astype(int)
    })


def load_folder(folder):
    dfs = []
    for f in os.listdir(folder):
        if f.endswith(".csv"):
            path = os.path.join(folder, f)
            print(f"[LOAD] {path}")
            df = pd.read_csv(path, encoding="latin1")
            dfs.append(normalize_dataframe(df))
    return dfs


def balanced_sample(df, target):
    return df.sample(target, random_state=42) if len(df) > target else df


def train_model():
    print("\n[1] Loading datasets...")

    phishing = pd.concat(load_folder(PHISHING_DIR), ignore_index=True)
    ham = pd.concat(load_folder(HAM_DIR), ignore_index=True)

    phishing = balanced_sample(phishing, TARGET_ROWS_PER_CLASS)
    ham = balanced_sample(ham, TARGET_ROWS_PER_CLASS)

    df = pd.concat([phishing, ham], ignore_index=True)
    df = df.sample(frac=1, random_state=42)  # shuffle

    print(f"[INFO] Total rows = {len(df):,}")

    print("\n[2] Cleaning text...")
    df["text"] = df["text"].apply(clean_text)

    print("\n[3] TF-IDF Vectorizing...")
    vectorizer = TfidfVectorizer(
        max_features=80000,
        ngram_range=(1, 2),
        stop_words="english",
        min_df=3,
        max_df=0.95,
        sublinear_tf=True
    )

    X = vectorizer.fit_transform(df["text"])
    y = df["label"]

    print(f"[INFO] Vector shape = {X.shape}")

    print("\n[4] Train / Test split...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\n[5] Training Logistic Regression...")
    model = LogisticRegression(
        max_iter=3000,
        solver="saga",
        class_weight="balanced",
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    print("\n[6] Evaluation:")
    preds = model.predict(X_test)
    print(classification_report(y_test, preds))

    print("\n[7] Saving model...")
    dump(model, MODEL_PATH)
    dump(vectorizer, VECTORIZER_PATH)

    print("\n🎉 Training completed (HIGH ACCURACY MODE)")


if __name__ == "__main__":
    train_model()
