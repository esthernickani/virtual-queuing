"""functions to deal with starting a queue and others, calling linked list"""
from linkedlist import LinkedList, Node
from models import User, db, Unauth_Customer
from flask import session
from datetime import datetime, timedelta
from num2words import num2words
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

def get_current_wait_time(wait_time):
    """break waittime into dict to be accessible"""
    wait_time_param = jsonpickle.decode(wait_time)
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    min_wait_time = timedelta(minutes = wait_time_param['min'])
    max_wait_time = timedelta(minutes = wait_time_param['max'])

    new_time_min = now + min_wait_time
    new_time_max = now + max_wait_time

    return (new_time_min, new_time_max)

def get_position(organization, customer_code):
    """using linked list function get customers position in queue"""
    position = 0
    queue = jsonpickle.decode(organization.queue)
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