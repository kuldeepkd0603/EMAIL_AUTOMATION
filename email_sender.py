import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from db import users, campaigns, stages, logs, rules
from config import SMTP_USER, SMTP_PASS, SMTP_HOST, SMTP_PORT

from datetime import datetime, timezone

from jinja2 import Template  

BASE_TEMPLATE_PATH = "templates/base.html"

def render_template(to_email, name, stage, content):
    with open(BASE_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template_content = f.read()
        template = Template(template_content)
        html = template.render(
            email=to_email or "",
            name=name or "User",
            stage=stage or "",
            content=content or ""
        )
        return html

def send_mail(to_email, name, stage, subject, content):
    html = render_template(to_email, name, stage, content)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    now = datetime.now(timezone.utc)
    logs.insert_one({
        "email": to_email,
        "stage": stage,
        "subject": subject,
        "content": content,
        "sent_at": now
    })
    return now
