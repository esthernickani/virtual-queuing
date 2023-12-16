"""organization model tests"""

import os
import jsonpickle
from unittest import TestCase
from linkedlist import LinkedList
from models import Unauth_Customer, User, db


os.environ['DATABASE_URL'] = "postgresql:///virque-test"

from app import app
db.create_all()

class OrganizationModelTestCase(TestCase):
    """does basic model work"""
    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        Unauth_Customer.query.delete()
        User.query.delete()

        test_org = User.signup(
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


        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transaction"""
        db.session.rollback()

    def test_user_model(self):
        """does basic model work"""
        db.session.commit()

        test_org = User.query.filter_by(username = 'test').first()

        self.assertEqual(test_org.industry, 'retail')
        self.assertEqual(test_org.city, 'Edmonton')

    def test_user_create_authenticate(self):
        """Test if user.create successfully creates a new user and authenticate"""
        test_org = User.query.filter_by(username = 'test').first()

        self.assertEqual(
            User.authenticate(
                username = 'test',
                password='testpassword'
             ), test_org)
        
        self.assertEqual(
            User.authenticate(
                username = 'test2',
                password='testpassword'
             ), None)


    def test_user_queue(self):
        """test the linked list in db"""

        test_org = User.query.filter_by(username = 'test').first()
        queue = jsonpickle.decode(test_org.queue)

        self.assertEqual(queue.length, 0)












    