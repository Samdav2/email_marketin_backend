import requests
import json

def test_send_custom_email():
    url = "http://localhost:8000/email/send-custom"

    payload = {
        "recipient": "info@thinkedgeconsultancy.com",
        "subject": "Custom Template Integration Test",
        "title": "Welcome to Our New Feature!",
        "name": "Valued Partner",
        "content": "<p>We are excited to announce our <strong>new custom email endpoint</strong>.</p><p>This allows you to send fully branded emails with custom content while maintaining our professional aesthetic.</p>",
        "button_text": "Explore Features",
        "button_url": "https://thinkedgeconsultancy.com"
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=30)

        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200 and response.json().get("success"):
            print("\nSUCCESS: Custom email endpoint is working correctly!")
        else:
            print("\nFAILED: Endpoint returned an error.")

    except Exception as e:
        print(f"\nERROR: Could not connect to the server. Make sure uvicorn is running.\n{str(e)}")

if __name__ == "__main__":
    test_send_custom_email()
