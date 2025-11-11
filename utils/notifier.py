from twilio.rest import Client
import os

def send_message(to, message):
    sid = os.getenv("TWILIO_SID")
    token = os.getenv("TWILIO_TOKEN")
    number = os.getenv("TWILIO_NUMBER")

    if not all([sid, token, number]):
        print("⚠️ Twilio not configured — message skipped.")
        return

    client = Client(sid, token)
    client.messages.create(
        body=message,
        from_=number,
        to=to
    )
    print(f"📤 Sent to {to}: {message}")
