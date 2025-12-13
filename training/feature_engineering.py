import re

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    # lowercase
    text = text.lower()

    # remove URLs
    text = re.sub(r"http[s]?://\S+", " url ", text)

    # remove emails
    text = re.sub(r"\S+@\S+", " email ", text)

    # remove html tags (simple)
    text = re.sub(r"<.*?>", " ", text)

    # keep only letters/numbers
    text = re.sub(r"[^a-z0-9 ]", " ", text)

    # normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text