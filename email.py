import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(to, subject, body):
    # Email configuration details
    email_address = 'your_email@example.com'
    email_password = 'your_email_password'
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = email_address
    msg['To'] = to

    # Create the body of the message (a plain-text and an HTML version).
    text = f"Hi!\n\n{body}"
    html = f"""\
    <html>
      <body>
        <p>Hi!</p>
        <p>{body}</p>
      </body>
    </html>
    """

    # Attach both plain-text and HTML versions of the message
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via SMTP server.
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(email_address, email_password)
        server.sendmail(email_address, to, msg.as_string())


        