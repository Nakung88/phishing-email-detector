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

from email import message_from_string

def extract_email_fields(raw_text: str) -> dict:
    msg = message_from_string(raw_text)

    subject = msg.get("Subject", "")
    sender = msg.get("From", "")

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body += part.get_payload(decode=True).decode("utf-8", errors="ignore")
                except:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
        except:
            body = msg.get_payload()

    return {
        "subject": subject,
        "from": sender,
        "body": body,
    }

