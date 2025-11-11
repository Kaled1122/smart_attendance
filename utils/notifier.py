from twilio.rest import Client
import os

def send_message(phone, message):
    client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))
    client.messages.create(
        to=phone,
        from_=os.getenv("TWILIO_NUMBER"),
        body=message
    )