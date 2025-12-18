import os
import pandas as pd

RAW = "dataset/RAW"
OUT = "dataset/PROCESSED/train.csv"

rows = []

def load_folder(path, label):
    for file in os.listdir(path):
        if not file.endswith(".csv"):
            continue
        df = pd.read_csv(os.path.join(path, file), encoding="latin1")

        for col in df.columns:
            if col.lower() in ["text", "body", "content"]:
                texts = df[col].dropna().astype(str)
                for t in texts:
                    t = t.strip()
                    if len(t) < 30:
                        continue
                    rows.append({
                        "text": t,
                        "label": label
                    })
                break

print("📥 Loading HAM...")
load_folder(f"{RAW}/HAM", 0)

print("📥 Loading PHISHING...")
load_folder(f"{RAW}/PHISHING", 1)

out = pd.DataFrame(rows)

if out.empty:
    print("❌ Dataset EMPTY")
    exit()

out = out.sample(frac=1, random_state=42)  # shuffle
out.to_csv(OUT, index=False)

print("✅ Dataset saved:", OUT)
print(out["label"].value_counts())
