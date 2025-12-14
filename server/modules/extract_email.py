# server/modules/extract_email.py
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
