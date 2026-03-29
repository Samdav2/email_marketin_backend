import smtplib
try:
    print("Testing Port 587...")
    with smtplib.SMTP("thinkedgeconsultancy.com", 587, timeout=10) as server:
        print("Connected to 587!")
        server.starttls()
        print("TLS started!")
        server.login("info@thinkedgeconsultancy.com", "Thinkedge@2025")
        print("Logged in!")
except Exception as e:
    print(f"Error on 587: {e}")

try:
    print("\nTesting Port 465...")
    with smtplib.SMTP_SSL("thinkedgeconsultancy.com", 465, timeout=10) as server:
        print("Connected to 465!")
        server.login("info@thinkedgeconsultancy.com", "Thinkedge@2025")
        print("Logged in!")
except Exception as e:
    print(f"Error on 465: {e}")
