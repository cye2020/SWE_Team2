from flask_mail import Message
from flask import url_for
from init import mail

def send_verification_email(email, token):
    subject = '이메일 인증'
    body = f'인증 링크: {url_for("verify_email", token=token, _external=True)}'
    message = Message(subject, recipients=[email], body=body)
    mail.send(message)
