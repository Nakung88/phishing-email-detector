import re

SUSPICIOUS_WORDS = [
    "verify", "account", "password", "urgent", "click",
    "login", "confirm", "update", "security", "suspended",
    "limited", "reset", "prize", "winner"
]

def extract_features(text: str) -> dict:
    text = text.lower()

    return {
        "url_count": len(re.findall(r"https?://", text)),
        "suspicious_word_count": sum(word in text for word in SUSPICIOUS_WORDS),
        "has_html": int("<html" in text or "<a " in text),
        "excessive_caps": sum(1 for c in text if c.isupper()) > 20,
        "length": len(text),
    }
