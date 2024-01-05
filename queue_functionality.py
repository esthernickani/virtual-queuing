"""functions to deal with starting a queue and others, calling linked list"""
from linkedlist import LinkedList, Node
from models import User, db, Unauth_Customer
from flask import session
from datetime import datetime, timedelta
from num2words import num2words
from geopy.geocoders import Nominatim
import pdb
import random
import jsonpickle

def create_unauth_customer_dict(first_name, last_name, contact_number, email, tag, time_joined, new_customer_code):
    new_customer = {
        "first_name" : first_name,
        "last_name" : last_name,
        "contact_number": contact_number,
        "email" : email,
        "tag" : tag,
        "time_joined" : time_joined, 
        "code" : new_customer_code
    }
    return new_customer

def generate_code():
    """generate code for users to have as their unique code per queue"""
    #get current codes
    all_customers = Unauth_Customer.query.all()
    current_customer_codes = [customer.code for customer in all_customers]
    while True:
        code = random.randrange(1000, 100000)
        if code not in current_customer_codes:
            return code
        
def get_tag(group_size):
    """function to get the tag that best describes customer or customers joining the queue"""
    if group_size != None:
        return f"Group of {group_size}"
    else:
        return "Individual"

def get_current_time():
    """get current time"""
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    return current_time

def get_wait_time(wait_time):
    """get wait time values from db"""
    wait_time_param = jsonpickle.decode(wait_time)
    min_wait_time = wait_time_param['min']
    max_wait_time = wait_time_param['max']

    return (min_wait_time, max_wait_time)

def get_current_wait_time(wait_time):
    """break waittime into dict to be accessible and get the time they would be attended to approximately"""
    wait_time_param = jsonpickle.decode(wait_time)
    now = datetime.now().replace(second=0, microsecond=0)
    current_time = now.strftime("%H:%M")
    min_wait_time = timedelta(minutes = wait_time_param['min'])
    max_wait_time = timedelta(minutes = wait_time_param['max'])

    new_time_min = now + min_wait_time
    new_time_max = now + max_wait_time
    return (new_time_min, new_time_max)

def get_position(queue, customer_code):
    """using linked list function get customers position in queue"""
    position = 0
    for item in queue:
        if item.data['code'] == customer_code:
            print(item)
            position = queue.get_position(item)
    return position

def get_position_ordinal(organization, customer_code):
    """using linked list function get customers position in queue"""
    position = 0
    queue = jsonpickle.decode(organization.queue)
    for item in organization.queue:
        print(item)
    for item in queue:
        if item.data['code'] == customer_code:
            position = queue.get_position(item)
    return num2words(position + 1, to='ordinal')

def remove_customer(customer_position_in_queue, queue):
        if customer_position_in_queue == 0:
            customer = queue.remove_first_node()
            return customer
        else:
            customer = queue.removeAtSpecificIdx(customer_position_in_queue)
            return customer

def create_wait_time_for_db(min_waittime, max_waittime):
    #function to get wait time
    approx_wait_time = {
        #appromimate wait time range in minutes
        'min' : min_waittime,
        'max' : max_waittime
    }

    return jsonpickle.encode(approx_wait_time)

def get_coords(organization, data_from_js):
    """get coords of organization and customer"""
    geolocator = Nominatim(user_agent="virque")
    organization_location = geolocator.geocode(organization.street_address)
    if organization_location == None:
        return None
    else:
        customer_coords = (data_from_js['latitude'], data_from_js['longitude'])
        organization_coords = (organization_location.latitude, organization_location.longitude)
    return (customer_coords, organization_coords)

def remove_from_queue(action, organization, queue, customer_code):
    """function to remove a customer from a queue"""
    queue = jsonpickle.decode(queue)
    customer_position_in_queue = get_position(queue, customer_code)
    customer_in_db = Unauth_Customer.query.filter_by(code = customer_code).first()
    #remove customer from queue
    customer = remove_customer(customer_position_in_queue, queue)
    #update queue of organization
    updated_queue = jsonpickle.encode(queue)
    if action == 'dequeue':
        organization.queue = updated_queue
        db.session.commit()
        #add customer to organization updated to be seated list
        add_to_be_seated(organization.to_be_seated, customer, customer_in_db, organization)

    if action == 'check-in':
        be_seated_list = jsonpickle.decode(organization.to_be_seated)
        #get position of customer in beseatedlist 
        organization.to_be_seated = updated_queue
        db.session.commit()
        #remove customer from unauth customer db
        Unauth_Customer.query.filter_by(code = customer_code).delete()
        db.session.commit()
    
    if action == 'delete':
        if customer_in_db.status == 'In Queue':
            organization.queue = updated_queue
        elif customer_in_db.status == "to be seated":
            organization.to_be_seated = updated_queue
        Unauth_Customer.query.filter_by(code = customer_code).delete()
        db.session.commit()
    return 

def add_to_be_seated(be_seated_list, customer, customer_in_db, organization):
    """add to be seated list"""
    be_seated_list = jsonpickle.decode(be_seated_list)
    be_seated_list.insert_at_end(customer)
    customer_in_db.status = "to be seated"
    updated_be_seated_list = jsonpickle.encode(be_seated_list)
    organization.to_be_seated = updated_be_seated_list
    db.session.commit()
    return