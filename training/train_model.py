import os
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from training.feature_engineering import clean_text

# ===============================
#  CONFIG
# ===============================
PH_DIR = "dataset/PHISHING"
HAM_DIR = "dataset/HAM"

MODEL_PATH = "model/email_phishing_model.pkl"
VEC_PATH = "model/tfidf_vectorizer.pkl"

MAX_FEATURES = 20000     # ultra-low-RAM TF-IDF


def load_csv_safe(path):
    """Try to load a CSV safely."""
    try:
        print(f"[LOAD] {path}")
        df = pd.read_csv(path)
        return df
    except Exception as e:
        print(f"[ERROR] Failed {path}: {e}")
        return None


def load_all():
    phishing_df_list = []
    ham_df_list = []

    # PHISHING
    for file in os.listdir(PH_DIR):
        fpath = os.path.join(PH_DIR, file)
        df = load_csv_safe(fpath)
        if df is not None:
            phishing_df_list.append(df)

    # HAM
    for file in os.listdir(HAM_DIR):
        fpath = os.path.join(HAM_DIR, file)
        df = load_csv_safe(fpath)
        if df is not None:
            ham_df_list.append(df)

    phishing = pd.concat(phishing_df_list, ignore_index=True)
    ham = pd.concat(ham_df_list, ignore_index=True)

    # unify columns
    def unify(df):
        # Try to get subject+body
        if "text_combined" in df:
            df["text"] = df["text_combined"]
        else:
            subj = df["subject"] if "subject" in df else ""
            body = df["body"] if "body" in df else ""
            df["text"] = subj.astype(str) + " " + body.astype(str)

        df["label"] = df["label"].astype(int)
        return df[["text", "label"]]

    return unify(phishing), unify(ham)


def train_model():
    print("\n==============================")
    print("  [1] Loading datasets...")
    print("==============================")

    phishing, ham = load_all()

    print(f"[INFO] PHISH rows = {len(phishing)}")
    print(f"[INFO] HAM rows   = {len(ham)}")

    # ==============================
    # [2] Balance dataset (RAM-safe)
    # ==============================
    print("\n==============================")
    print("  [2] Balancing...")
    print("==============================")

    # sample HAM to match phishing count *0.5 (more stable)
    HAM_TARGET = min(len(ham), len(phishing) // 2)
    ham_bal = ham.sample(HAM_TARGET, random_state=42)

    df = pd.concat([phishing, ham_bal], ignore_index=True)
    print(f"[INFO] Final rows = {len(df)}")

    # ==============================
    # [3] Clean text (Light mode)
    # ==============================
    print("\n==============================")
    print("  [3] Cleaning text...")
    print("==============================")

    df["text"] = df["text"].astype(str).apply(clean_text)

    # ==============================
    # [4] TF-IDF
    # ==============================
    print("\n==============================")
    print("  [4] TF-IDF Vectorizing...")
    print("==============================")

    vectorizer = TfidfVectorizer(
        max_features=MAX_FEATURES,
        ngram_range=(1,2),
        sublinear_tf=True
    )

    X = vectorizer.fit_transform(df["text"])
    y = df["label"]

    print(f"[INFO] Vector shape = {X.shape}")

    # ==============================
    # [5] Train Logistic Regression
    # ==============================
    print("\n==============================")
    print("  [5] Training Logistic Regression...")
    print("==============================")

    model = LogisticRegression(max_iter=1500)
    model.fit(X, y)

    # ==============================
    # [6] Save files
    # ==============================
    print("\n==============================")
    print("  [6] Saving model & vectorizer...")
    print("==============================")

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    with open(VEC_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    print(f"[OK] Saved model: {MODEL_PATH}")
    print(f"[OK] Saved vectorizer: {VEC_PATH}")


if __name__ == "__main__":
    train_model()