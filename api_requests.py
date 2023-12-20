from api_secrets import mapbox_api_secret_key, twilio_auth_token, twilio_account_sid
import os
import twilio
import pdb
import requests
from twilio.rest import Client

def get_distance_traveltime(travel_mode, customer_org_coords):
    """get directions from mapbox api"""
    #get coords
    customer_lat = customer_org_coords[0][0]
    customer_long = customer_org_coords[0][1]
    organization_lat = customer_org_coords[1][0]
    organization_long = customer_org_coords[1][1]

    mode = travel_mode
    
    url = f"https://api.mapbox.com/directions/v5/mapbox/{mode}/{customer_long},{customer_lat};{organization_long},{organization_lat}?geometries=geojson&access_token={mapbox_api_secret_key}"

    response = requests.get(url)
    print(response)
    data = response.json()
    print(data)
    
    distance = (data["routes"][0]["distance"])/1000
    duration = (data["routes"][0]["duration"])/60
    return (f"{round(distance, 1)} km", f"{round(duration)} mins")

    

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

def send_delete_message(customer_number):
    """send sms using twilio api to notify customer they have been dequeued"""
    account_sid = twilio_account_sid
    auth_token = twilio_auth_token
    client = Client(account_sid, auth_token)

    message = client.messages.create(
    from_='+18646184414',
    body="You have been removed from the queue, please contact the organization for more details if needed.",
    to=f'+{customer_number}'
    )