from api_secret_codes import mapbox_api_secret_key, twilio_auth_token, twilio_account_sid
import os
import twilio
from twilio.rest import Client

def get_directions():
    """get directions from mapbox api"""
    url = f"https://api.mapbox.com/directions/v5/"

def send_join_queue_message(organization, customer_code, customer_number):
    """send sms using twilio api to notify customer they have joined queue"""
    
    account_sid = twilio_account_sid
    auth_token = twilio_auth_token
    client = Client(account_sid, auth_token)

    message = client.messages.create(
    from_='+18646184414',
    body=f"Congratulations! You've successfully joined the {organization} queue, and your code is {customer_code}. Utilize it to check your status on the VIR-QUE website. You'll receive an SMS notification when it's your turn in the queue. Enjoy the wait! :D",
    to=f'+{customer_number}'
    )

def send_dequeue_message(customer_number):
    """send sms using twilio api to notify customer they have been dequeued"""
    account_sid = twilio_account_sid
    auth_token = twilio_auth_token
    client = Client(account_sid, auth_token)

    message = client.messages.create(
    from_='+18646184414',
    body="It's time for your turn in the queue. Please approach the host to complete the check-in process",
    to=f'+{customer_number}'
    )