"""Unauth customer model tests

import os
from unittest import TestCase
from models import Unauth_Customer, User, db

os.environ['DATABASE_URL'] = "postgresql:///virque-test"

from app import app
db.create_all()

class UnauthCustomerModelTestCase(TestCase):
    does basic model work
    def setUp(self):
        Create test client, add sample data.
        db.drop_all()
        db.create_all()

        Unauth_Customer.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        Clean up any fouled transaction
        db.session.rollback()"""

    