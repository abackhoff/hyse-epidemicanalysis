from flask_mail import Mail, Message

def send_email(recipient, subject, body):
    mail = Mail()
    message = Message(subject=subject, sender='your-email-address', recipients=['albertobackhoff@gmail.com'])
    message.body = body
    mail.send(message)

    
