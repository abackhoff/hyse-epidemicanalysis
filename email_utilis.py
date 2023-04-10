from flask_mail import Mail, Message

def send_email(recipient, subject, body):
    mail = Mail()
    message = Message(subject=subject, sender='your-email-address', recipients=[recipient])
    message.body = body
    mail.send(message)

    