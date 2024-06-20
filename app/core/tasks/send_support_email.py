import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings
from app.core.logs import get_logger
from app.models import Ticket

logger = get_logger()


def send_to_support(data: Ticket):
    # Sender email credentials and SMTP server details
    sender_email = settings.SMTP_EMAIL
    sender_password = settings.SMTP_PASSWORD
    smtp_server = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    support = settings.SUPPORT_EMAIL

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = support
    msg["Subject"] = f"Support ticket #{data.id}"

    # Create the email body with headers and data
    body = (
        f"Subject: {data.subject or 'N/A'}\n"
        f"Full Name: {data.full_name}\n"
        f"Company Name: {data.company_name or 'N/A'}\n"
        f"Mobile Phone: {data.mobile_phone or 'N/A'}\n"
        f"Email: {data.email}\n"
        f"Message:\n{data.message}"
    )
    msg.attach(MIMEText(body, "plain"))

    # Send the email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        logger.info("Email sent successfully!")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
