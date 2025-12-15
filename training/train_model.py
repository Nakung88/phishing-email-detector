import pandas as pd
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
MODEL_DIR = BASE_DIR / "model"
MODEL_DIR.mkdir(exist_ok=True)


def load_folder(folder, label):
    rows = []
    for csv in (DATASET_DIR / folder).glob("*.csv"):
        df = pd.read_csv(csv, header=None, encoding="latin1")
        for col in df.columns:
            texts = df[col].dropna().astype(str)
            for t in texts:
                rows.append({"text": t, "label": label})
    return pd.DataFrame(rows)


print("📥 Loading datasets...")
phish = load_folder("PHISHING", 1)
ham = load_folder("HAM", 0)

data = pd.concat([phish, ham]).sample(frac=1).reset_index(drop=True)

X = data["text"].astype(str)
y = data["label"]

print("🧠 TF-IDF...")
vectorizer = TfidfVectorizer(
    max_features=50000,
    ngram_range=(1, 2),
    stop_words="english"
)
X_vec = vectorizer.fit_transform(X)

print("🤖 Training model...")
model = LogisticRegression(max_iter=2000)
model.fit(X_vec, y)

print("💾 Saving model + vectorizer...")
joblib.dump(model, MODEL_DIR / "email_phishing_model.pkl")
joblib.dump(vectorizer, MODEL_DIR / "tfidf_vectorizer.pkl")

print("✅ DONE")
print("Features:", X_vec.shape[1])
