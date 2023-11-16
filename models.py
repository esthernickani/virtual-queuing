"""SQLAlchemy models for vir-que"""
import pdb
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

class Organization_Customer(db.Model):
    """link customers to organization"""
    __tablename__ = "organization_customer"

    id = db.Column(
        db.Integer,
        primary_key = True
    )

    organization_id = db.Column(
        db.Integer,
        db.ForeignKey('organizations.id')
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey('customers.id')
    )


class Customer(UserMixin, db.Model):
    """Users or clients that are registered into the system"""
    __tablename__ = "customers"
    id = db.Column(
        db.Integer,
        primary_key = True
    )

    username = db.Column(
        db.String(200),
        nullable = False,
        unique = True
    )

    email = db.Column(
        db.String(50),
        nullable = False,
        unique = True
    )

    password = db.Column(
        db.String,
        nullable = False
    )

    directions_enabled = db.Column(
        db.Boolean
    )

    locations_enabled = db.Column(
        db.Boolean
    )

    notifications_enabled = db.Column(
        db.Boolean
    )

    current_queue_tag = db.Column(
        db.Integer
    )

    current_queueID = db.Column(
        db.Integer
    )

    @classmethod
    def signup(cls, username, email, password, organizations_id):
        """sign up user, hashes password and adds user to system"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        customer = Customer(
            username=username,
            email = email,
            password = hashed_pwd
        )

        db.session.add(customer)
        db.session.commit

        for organization_id in organizations_id:
            customer = Customer.query.filter_by(username=username).first()
            organization_customer = Organization_Customer(
                organization_id = organization_id,
                customer_id = customer.id
            )
            
            db.session.add(organization_customer)
        
        
        return customer
    
    @classmethod
    def authenticate(cls, username, password):
        """find user with username and password"""
        user = cls.query.filter_by(username = username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
            else:
                return False
            
    @classmethod
    def get(cls, customer_id):
        return cls.query.get(int(customer_id))
    

class Organization(UserMixin, db.Model):
    """Organizations in the system"""
    __tablename__ = "organizations"
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(200),
        nullable = False,
        unique = True
    )

    company_name = db.Column(
        db.String(200),
        nullable = False,
        unique = True
    )

    email = db.Column(
        db.String(50),
        nullable = False,
        unique = True
    )

    contact_number = db.Column(
        db.String(10),
        nullable = False
    )

    industry = db.Column(
        db.String(20),
        nullable = False
    )

    street_address = db.Column(
        db.String,
        nullable = False
    )

    street_address2 = db.Column(
        db.String
    )

    city = db.Column(
        db.String,
        nullable = False
    )

    province_or_state = db.Column(
        db.String,
        nullable = False
    )

    postal_code = db.Column(
        db.String,
        nullable = False
    )

    password = db.Column(
        db.String,
        nullable = False
    )

    customer = db.relationship('Customer', secondary = Organization_Customer.__table__, backref="organizations")

    @classmethod
    def signup(cls, username, company_name, email, industry, street_address, street_address2, city, province_or_state, postal_code, contact_number, password):
        """sign up user, hashes password and adds user to system"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        organization = Organization(
            username=username,
            company_name = company_name, 
            email = email,
            industry = industry,
            street_address = street_address,
            street_address2 = street_address2,
            city = city,
            province_or_state = province_or_state,
            contact_number = contact_number,
            postal_code = postal_code,
            password = hashed_pwd
        )

        db.session.add(organization)
        return organization
    
    @classmethod
    def authenticate(cls, username, password):
        """find user with username and password"""
        user = cls.query.filter_by(username = username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
            else:
                return False
    @classmethod
    def get(cls, organization_id):
        return cls.query.get(int(organization_id))



class Queue(db.Model):
    """all current operating queues"""
    __tablename__ = "queue"
    id = db.Column(
        db.Integer,
        primary_key = True
    )

    location = db.Column(
        db.String(50),
        nullable = False
    )

    organization_id = db.Column(
        db.Integer,
        db.ForeignKey('organizations.id')
    )

    maxCapacity = db.Column(
        db.Integer
    )

    averageWaitTime = db.Column(
        db.Integer
    )

    timeStarted = db.Column(
        db.DateTime,
        nullable = False,
        default = datetime.utcnow()
    )

    organization = db.relationship(
        "Organization", backref = "queue"
    )

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)


