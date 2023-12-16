"""Organization View tests."""
import os
import jsonpickle
from unittest import TestCase
from linkedlist import LinkedList
from models import Unauth_Customer, User, db

os.environ['DATABASE_URL'] = "postgresql:///virque-test"

from app import app

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class OrganizationViewTestCase(TestCase):
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

        db.session.commit()

        with self.client as c:
            resp = c.post("organization/login", data ={
                "username" : 'test',
                "password" : 'testpassword' 
            })
    
    def tearDown(self):
        """Clean up any fouled transaction"""
        db.session.rollback()

    def test_see_queuepage(self):
        """can you see home when youre logged in"""
       
        with self.client as c:
            resp = c.get('/organization/queue')
            
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Activate Queue', html)
    
    def test_see_profile(self):
        """can you see profile page"""
        with self.client as c:
            resp = c.get('/organization/profile/overview')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'{self.testorg.username}', html)

    def test_edit_profile(self):
        """can you edit an organization details from the profile page"""
        with self.client as c:
            resp = c.post('/organization/profile/overview/edit', 
                          data = {"organization.username": "changeusername"},
                          follow_redirects = True)
            
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Profile successfully edited', html)

    def test_reset_email(self):
        """can you reset email"""
        with self.client as c:
            resp = c.post('/organization/profile/security/reset-email',
                          data={"new_email" : "newemail@yahoo.com",
                                "confirm_email": "newemail@yahoo.com"},
                            follow_redirects = True)
            
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Email address successfully changed', html)

            organization = User.query.filter_by(username = 'test').first()
            self.assertEqual(organization.email, 'newemail@yahoo.com')



