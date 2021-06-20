import os
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# from boto.s3.connection import S3Connection
# s3 = S3Connection(os.environ['S3_KEY'], os.environ['S3_SECRET'])

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
RECEIVING_EMAILS = os.environ.get("RECEIVING_EMAILS")


class MailService():

    def __init__(self):
        self.receiving_emails = json.loads(RECEIVING_EMAILS)
        self.gmail_app_password = GMAIL_APP_PASSWORD
        self.sender_email = SENDER_EMAIL
        pass

    def send_emails(self, text, html, tokens):
        for email in self.receiving_emails:
            self.__send_email(email, text, html, tokens)

    def __send_email(self, receiver_email, text, html, tokens):
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Medical Notification for tokens: {tokens}."
        message["From"] = self.sender_email
        message["To"] = receiver_email

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(self.sender_email, self.gmail_app_password)
            server.sendmail(
                self.sender_email, receiver_email, message.as_string()
            )
