import imaplib
import email
from email.header import decode_header
import os
import smtplib
from email.message import EmailMessage

# Environment variables
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
OWNER_EMAIL = os.getenv("OWNER_EMAIL")

def send_reply_with_file(to_email, subject, body, filename):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = GMAIL_USER
    msg['To'] = to_email
    msg.set_content(body)

    with open(filename, 'rb') as f:
        file_data = f.read()
        file_name = f.name

    msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_PASS)
        smtp.send_message(msg)

def check_and_reply_email():
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(GMAIL_USER, GMAIL_PASS)
    imap.select("inbox")

    status, messages = imap.search(None, 'UNSEEN')
    messages = messages[0].split()

    for mail in messages[-1:]:
        _, msg_data = imap.fetch(mail, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()

                if msg.is_multipart():
                    for part in msg.walk():
                        content_disposition = str(part.get("Content-Disposition"))
                        if "attachment" in content_disposition:
                            filename = part.get_filename()
                            if filename:
                                filepath = f"./downloads/{filename}"
                                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                                with open(filepath, "wb") as f:
                                    f.write(part.get_payload(decode=True))

                                # 🎯 Here you can process the file (e.g., generate clone, video, etc.)
                                send_reply_with_file(OWNER_EMAIL, f"Zyra: Your processed file", "Here's your result as you requested.", filepath)

    imap.logout()

if __name__ == "__main__":
    check_and_reply_email()
