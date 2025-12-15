import os
from datetime import datetime

QUARANTINE_DIR = "quarantine"

os.makedirs(QUARANTINE_DIR, exist_ok=True)

def save_to_quarantine(content: str):
    filename = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    path = os.path.join(QUARANTINE_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
