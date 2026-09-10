import smtplib
from email.mime.text import MIMEText

sender = "info@thinkedgeconsultancy.com"
msg = MIMEText("Internal test.")
msg['Subject'] = "Internal Test"
msg['From'] = sender
msg['To'] = sender

try:
    print(f"Sending test to {sender}...")
    with smtplib.SMTP_SSL("thinkedgeconsultancy.com", 465, timeout=10) as server:
        server.login(sender, "Thinkedge@2025")
        server.sendmail(sender, [sender], msg.as_string())
        print("Sent successfully!")
except Exception as e:
    print(f"Error: {e}")
