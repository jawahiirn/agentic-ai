from dotenv import load_dotenv
import requests
import os
import smtplib
from email.message import EmailMessage
import resend
from resend.exceptions import ResendError
load_dotenv(override=True)


RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM = os.getenv("RESEND_FROM")
RESEND_TO = os.getenv("RESEND_TO")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

USE_RESEND = bool(RESEND_API_KEY and RESEND_FROM and RESEND_TO)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")


def send_email_resend(subject, text_body, html_body):
    params: resend.Emails.SendParams = {
        "from": RESEND_FROM,
        "to": [RESEND_TO],
        "subject": subject,
        "html": html_body,
        "text": text_body,
    }
    try:
        response = resend.Emails.send(params)
        print(f"Resend email sent: {response}")
        return response
    except ResendError as error:
        print(f"Resend failed: {error}")
        raise


def send_email_smtp(subject, text_body, html_body):
    if not (EMAIL_ADDRESS and EMAIL_SMTP_SERVER and EMAIL_APP_PASSWORD):
        raise RuntimeError(
            "SMTP is not configured. Set EMAIL_ADDRESS, EMAIL_SMTP_SERVER "
            "and EMAIL_APP_PASSWORD in .env, or configure Resend instead."
        )
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg["Subject"] = subject
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(EMAIL_SMTP_SERVER, 587, timeout=10) as server:
        server.ehlo()
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg)


def send_email(subject, text_body, html_body):
    if USE_RESEND:
        return send_email_resend(subject, text_body, html_body)
    return send_email_smtp(subject, text_body, html_body)


pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

def push(message):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)

