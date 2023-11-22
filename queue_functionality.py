"""functions to deal with starting a queue and others, calling linked list"""
from linkedlist import LinkedList, Node
from models import Organization, Customer, Queue, db
from flask import session
import json


def start_queue(organization_id, max_capacity, avg_waittime, queue_name):
    """function for organization to star a queue"""
    organization = Organization.query.get(organization_id)
    new_queue = Queue(
        name = queue_name,
        location = organization.city,
        organization_id = organization_id,
        max_capacity = max_capacity,
        average_waittime = avg_waittime
    )

    db.session.add(new_queue)
    db.session.commit()

    queue_name = json.dumps(LinkedList().serialize())
    
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

    