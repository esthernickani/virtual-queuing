"""Organization View tests."""
import os
import pdb
import jsonpickle
from unittest import TestCase
from linkedlist import LinkedList
from models import Unauth_Customer, User, db
from flask_socketio import SocketIOTestClient

os.environ['DATABASE_URL'] = "postgresql:///virque-test"

from app import app, socketio

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class QueueTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        User.query.delete()
        Unauth_Customer.query.delete()

        self.client = app.test_client()

        self.testorg = User.signup(
            username = 'test',
            company_name = 'test',
            email = 'test@yahoo.com',
            industry = 'retail',
            street_address= '123 test road', 
            street_address2= None,
            city = 'Edmonton',
            province_or_state='Alberta',
            contact_number = 5875873874,
            postal_code= 'T12345',
            password='testpassword',
            to_be_seated = jsonpickle.encode(LinkedList())
        )

        self.testorg.queue_is_active = True

        db.session.commit()
    
    def tearDown(self):
        """Clean up any fouled transaction"""
        db.session.rollback()

    def test_join_queue(self):
        """test a client joining queue"""
        data = {'firstName': 'testfirstname', 
                'lastName': 'testlastname',
                'email': 'testcustomer@yahoo.com', 
                'contactNumber': '+1111111111', 
                'organizationName': 'test', 
                'groupSize': None}
        
        with self.socketio_client:
            self.socketio_client.emit('join_queue', data)
            response = self.socketio_client.get_received()
            
            print(response)
            pdb.set_trace()
