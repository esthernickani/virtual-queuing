"""Unauth customer model tests"""

import os
import jsonpickle
from unittest import TestCase
from linkedlist import LinkedList
from models import Unauth_Customer, User, db


os.environ['DATABASE_URL'] = "postgresql:///virque-test"

from app import app

class UnauthCustomerModelTestCase(TestCase):
    """does basic model work"""
    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        Unauth_Customer.query.delete()
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

        customer = Unauth_Customer(
            first_name = 'Ima',
            last_name = 'Test',
            email = 'ima@yahoo.com',
            code = 12345,
            contact_number = 7898765432,
            organization_id = f"{User.query.filter_by(username = 'test').first().id}",
            tag = 'Individual',
            status = 'In queue'
        )

        db.session.add(customer)

        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up any fouled transaction"""
        db.session.rollback()
    
    def test_customer_repr(self):
        """does repr work"""

        test_customer = Unauth_Customer.query.filter_by(first_name = 'Ima').first()

        expectedRepr = f"<Unauth_Customer #1: Ima, Test, ima@yahoo.com, 12345, 7898765432, {User.query.filter_by(username = 'test').first().id}, Individual, In queue>"
        self.assertEqual(repr(test_customer), expectedRepr)
    
    def test_customer_model(self):
        """does basic model work"""
        customer = Unauth_Customer.query.filter_by(first_name = 'Ima').first()
        test_org = User.query.filter_by(username = 'test').first()

        self.assertEqual(customer.code, 12345)
        self.assertEqual(customer.organization_id, test_org.id)