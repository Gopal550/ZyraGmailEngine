import imaplib, email, time, os, smtplib
from email.message import EmailMessage

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
OWNER_EMAIL = os.getenv("OWNER_EMAIL")

def check_mail():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(GMAIL_USER, GMAIL_PASS)
    mail.select("inbox")

    result, data = mail.search(None, "UNSEEN")
    mail_ids = data[0].split()

    for i in mail_ids:
        result, msg_data = mail.fetch(i, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        subject = msg["subject"]
        from_ = msg["from"]

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    print("📩 Email received with body:", body)
                    send_response(subject, body)
        else:
            body = msg.get_payload(decode=True).decode()
            send_response(subject, body)

        mail.store(i, "+FLAGS", "\\Seen")

def send_response(subject, body):
    msg = EmailMessage()
    msg["Subject"] = f"Zyra Reply: {subject}"
    msg["From"] = GMAIL_USER
    msg["To"] = OWNER_EMAIL
    msg.set_content(f"Zyra received your command:\n\n{body}\n\n✅ Processed.")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_PASS)
        smtp.send_message(msg)
        print("📤 Response sent!")

while True:
    check_mail()
    time.sleep(60)
