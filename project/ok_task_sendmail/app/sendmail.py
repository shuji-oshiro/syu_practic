import os
from datetime import datetime
from aiosmtplib import send
from email.message import EmailMessage

# async def send_email(to, subject, content):
#     message = EmailMessage()
#     message["From"] = "youraddress@example.com"
#     message["To"] = to
#     message["Subject"] = subject
#     message.set_content(content)

#     await send(
#         message,
#         hostname="smtp.example.com",
#         port=587,
#         username="youraddress@example.com",
#         password="yourpassword",
#         start_tls=True,
#     )

async def send_email(to, subject, content):
    print(f"[DEBUG] send_email {datetime.now()}")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    with open(os.path.join(log_dir, "emails.log"), "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] TO: {to}\nSUBJECT: {subject}\n{content}\n\n")