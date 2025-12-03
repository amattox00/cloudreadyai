import os, asyncio, smtplib
from email.message import EmailMessage

APP_ENV=os.getenv("APP_ENV","dev")
SENDER=os.getenv("EMAIL_SENDER","no-reply@example.com")
FROM_NAME=os.getenv("EMAIL_FROM_NAME","CloudReadyAI")
HOST=os.getenv("EMAIL_SMTP_HOST",""); PORT=int(os.getenv("EMAIL_SMTP_PORT","0") or "0")
USER=os.getenv("EMAIL_SMTP_USER",""); PASS=os.getenv("EMAIL_SMTP_PASS","")

def _send_sync(to,subject,html):
    if not HOST or not PORT:
        print(f"[DEV-EMAIL] to={to} subject={subject}\n{html}")
        return
    m=EmailMessage(); m["From"]=f"{FROM_NAME} <{SENDER}>"; m["To"]=to; m["Subject"]=subject
    m.set_content("HTML version required"); m.add_alternative(html, subtype="html")
    with smtplib.SMTP(HOST, PORT) as s:
        try: s.starttls()
        except Exception: pass
        if USER and PASS: s.login(USER,PASS)
        s.send_message(m)

async def send_email(to,subject,html):
    loop=asyncio.get_event_loop()
    await loop.run_in_executor(None,_send_sync,to,subject,html)
