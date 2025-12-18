import re

SAFE_PATTERNS = [
    r"no action is required",
    r"manage your subscription in the app",
    r"we will never ask for your password",
    r"thank you for your payment",
    r"this email confirms",
]

PHISHING_PATTERNS = [
    r"you have won",
    r"claim your prize",
    r"account suspended",
    r"verify your account",
    r"urgent action required",
]

def safe_override(text: str):
    hits = []
    lower = text.lower()

    for p in SAFE_PATTERNS:
        if re.search(p, lower):
            hits.append(p)

    return hits

def rule_check(text: str):
    text_l = text.lower()
    reasons = []

    for p in SAFE_PATTERNS:
        if re.search(p, text_l):
            reasons.append(f"SAFE_RULE:{p}")
            return "SAFE", reasons

    for p in PHISHING_PATTERNS:
        if re.search(p, text_l):
            reasons.append(f"PHISH_RULE:{p}")
            return "PHISHING", reasons

    return None, []
