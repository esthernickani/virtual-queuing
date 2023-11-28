"""functions to deal with starting a queue and others, calling linked list"""
from linkedlist import LinkedList, Node
from models import User, db
from flask import session
import jsonpickle

def create_unauth_customer_dict(first_name, last_name, contact_number, email):
    new_customer = {
        "First name" : first_name,
        "Last name" : last_name,
        "Contact Number": contact_number,
        "email" : email
    }
    return new_customer

def start_queue(organization_id, max_capacity, avg_waittime, queue_name):
    """function for organization to star a queue"""
    organization = User.query.get(organization_id)

    db.session.commit()
    queue = jsonpickle.encode(LinkedList())

    session['queue'] = queue
    
    return queue_name

def join_queue(queue_id, customer_id):
    """function for a customer to join a queue"""
    new_node = Node(customer_id)
    f"queue{queue_id}".insert_at_end(new_node)
    return

def dequeue(queue_id):
    """function to remove the customer at beginning of the queue"""
    f"queue{queue_id}.remove_first_node"
    return

def dequeue_and_hold(queue_id, customer_id):
    """function to remove the customer at the beginning of the queue if the customer is not there yet"""

    