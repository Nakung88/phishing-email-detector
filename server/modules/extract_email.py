# server/modules/extract_email.py

from email import message_from_string
from email.message import Message


def extract_email_fields(raw_text: str) -> dict:
    try:
        msg: Message = message_from_string(raw_text)

        subject = msg.get("Subject", "")
        from_field = msg.get("From", "")

        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode(
                            part.get_content_charset() or "utf-8",
                            errors="ignore"
                        )
                    except Exception:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode(
                    msg.get_content_charset() or "utf-8",
                    errors="ignore"
                )
            except Exception:
                body = str(msg.get_payload())

        return {
            "subject": subject.strip(),
            "from": from_field.strip(),
            "body": body.strip()
        }

    except Exception:
        return {
            "subject": "",
            "from": "",
            "body": raw_text
        }
