import re
from bs4 import BeautifulSoup
import warnings
from bs4 import MarkupResemblesLocatorWarning

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = text.lower()

    # remove html
    text = BeautifulSoup(text, "lxml").get_text(" ")

    # remove urls
    text = re.sub(r"http\S+|www\S+", " URL ", text)

    # remove emails
    text = re.sub(r"\S+@\S+", " EMAIL ", text)

    # keep words only
    text = re.sub(r"[^a-z\s]", " ", text)

    # normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text
