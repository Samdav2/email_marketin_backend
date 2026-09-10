import requests
import json

def test_send_custom_bulk_email():
    url = "http://localhost:8000/email/send-custom-bulk"

    # Test with explicit list of emails
    payload = {
        "emails": ["info@thinkedgeconsultancy.com", "test@example.com"],
        "subject": "Bulk Custom Template Test",
        "title": "Big Updates for Our Community!",
        "content": "<p>We've just launched <strong>Bulk Sending</strong> for custom emails!</p><p>Now you can reach your entire audience with personalized, professional designs in seconds.</p>",
        "button_text": "See What's New",
        "button_url": "https://thinkedgeconsultancy.com"
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=60)

        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200 and response.json().get("success"):
            print("\nSUCCESS: Bulk custom email endpoint is working correctly!")
        else:
            print("\nFAILED: Endpoint returned an error.")

    except Exception as e:
        print(f"\nERROR: Could not connect to the server or request timed out.\n{str(e)}")

if __name__ == "__main__":
    test_send_custom_bulk_email()
