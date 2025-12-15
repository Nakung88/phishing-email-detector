# server/modules/extract_email.py

from email import policy
from email.parser import BytesParser


def extract_email_text(upload_file):
    """
    รับ UploadFile (.eml)
    คืน string text ทั้งหมดของ email
    """

    raw_bytes = upload_file.file.read()

    msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)

    parts = []

    # subject
    if msg["subject"]:
        parts.append(msg["subject"])

    # body
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    parts.append(part.get_content())
                except Exception:
                    pass
    else:
        try:
            parts.append(msg.get_content())
        except Exception:
            pass

    text = "\n".join(parts)
    return text
