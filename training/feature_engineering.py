import re
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = [
    "verify", "login", "urgent", "suspend", "confirm",
    "password", "bank", "account", "security", "click"
]

TRUSTED_DOMAINS = [
    "google.com",
    "microsoft.com",
    "github.com",
    "apple.com",
    "amazon.com"
]


def extract_features(text: str) -> dict:
    text_lower = text.lower()

    # URLs
    urls = re.findall(r'https?://[^\s]+', text_lower)

    url_domains = []
    for u in urls:
        try:
            d = urlparse(u).netloc
            if d:
                url_domains.append(d)
        except Exception:
            pass

    suspicious_words = sum(1 for k in SUSPICIOUS_KEYWORDS if k in text_lower)

    has_http = any(u.startswith("http://") for u in urls)
    many_links = len(urls) >= 2

    trusted_link = any(
        any(td in d for td in TRUSTED_DOMAINS)
        for d in url_domains
    )

    return {
        "num_links": len(urls),
        "has_http": int(has_http),
        "many_links": int(many_links),
        "suspicious_words": suspicious_words,
        "trusted_link": int(trusted_link),
    }
