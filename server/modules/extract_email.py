from email import policy
from email.parser import BytesParser


def extract_email_text(raw_bytes: bytes) -> str:
    msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)

    parts = []

    if msg["subject"]:
        parts.append(msg["subject"])

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                parts.append(part.get_content())
    else:
        parts.append(msg.get_content())

    return "\n".join(parts)
