"""functions to deal with starting a queue and others, calling linked list"""
from linkedlist import LinkedList, Node
from models import User, db, Unauth_Customer
from flask import session
import jsonpickle
import random

def create_unauth_customer_dict(first_name, last_name, contact_number, email, tag):
    new_customer = {
        "first_name" : first_name,
        "last_name" : last_name,
        "contact_number": contact_number,
        "email" : email,
        "tag" : tag
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
    if group_size != 'null':
        return f"Group of {group_size}"
    else:
        return "Individual"

