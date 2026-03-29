import smtplib
from email.mime.text import MIMEText

recipient = "adoxop1@gmail.com"
sender = "info@thinkedgeconsultancy.com"
msg = MIMEText("This is a test email.")
msg['Subject'] = "Simple Test"
msg['From'] = sender
msg['To'] = recipient

try:
    print(f"Sending test to {recipient} via 465...")
    with smtplib.SMTP_SSL("thinkedgeconsultancy.com", 465, timeout=10) as server:
        server.login(sender, "Thinkedge@2025")
        server.sendmail(sender, [recipient], msg.as_string())
        print("Sent successfully!")
except Exception as e:
    print(f"Error: {e}")
