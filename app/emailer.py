import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone
from .config import get_settings
from .db import get_conn

def send_ticket_email(ticket_id: int, recipient: str, ticket_number: str, category: str | None, subcategory: str | None) -> str:
    settings = get_settings()
    subject = "Your Request for the issue has been submitted."
    body = (
        f"Your IT support request {ticket_number} has been submitted successfully.\n\n"
        f"Category: {category or 'Pending'}\n"
        f"Subcategory: {subcategory or 'Pending'}\n\n"
        "The IT helpdesk will review your request."
    )
    status = "queued"
    if settings.smtp_enabled:
        msg = EmailMessage()
        msg["From"] = settings.smtp_from
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(body)
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                smtp.starttls()
                if settings.smtp_username:
                    smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(msg)
            status = "sent"
        except Exception as exc:
            status = f"failed: {exc.__class__.__name__}"
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO email_logs(ticket_id,recipient,subject,body,status,created_at) VALUES(?,?,?,?,?,?)",
            (ticket_id, recipient, subject, body, status, datetime.now(timezone.utc).isoformat())
        )
    return status
