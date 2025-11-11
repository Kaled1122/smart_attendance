import os

def send_message(phone, message):
    """
    Safe Twilio notifier:
    - If credentials exist -> sends real SMS via Twilio.
    - If missing -> prints to console (mock mode).
    """
    try:
        TWILIO_SID = os.getenv("TWILIO_SID")
        TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
        TWILIO_NUMBER = os.getenv("TWILIO_NUMBER")

        # If Twilio is not configured, just log instead of sending
        if not all([TWILIO_SID, TWILIO_TOKEN, TWILIO_NUMBER]):
            print(f"[MockSMS] To {phone}: {message}")
            return

        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(
            to=phone,
            from_=TWILIO_NUMBER,
            body=message
        )
        print(f"[SMS SENT] To {phone}: {message}")

    except Exception as e:
        # Never crash — always log instead
        print(f"[Notifier Error] Could not send message to {phone}. Error: {e}")
