"""SQLAlchemy models for vir-que"""
import pdb
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from linkedlist import LinkedList, Node
from time import time
import jsonpickle
import os
import jwt
from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()

def get_wait_time():
    #function to get wait time
    approx_wait_time = {
        #appromimate wait time range in minutes
        'min' : 20,
        'max' : 30
    }

    return jsonpickle.encode(approx_wait_time)

wait_time = get_wait_time()

def create_queue():
    #function to create queue
    linked_list = LinkedList()
    #convert queue to JSON so it can be stored in database
    queue = jsonpickle.encode(linked_list)
    return queue

queue = create_queue()

class User(UserMixin, db.Model):
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

    queue = db.Column(
        db.String,
        default = queue
    )

    queue_is_active = db.Column(
        db.Boolean, 
        default = False
    )

    queue_wait_time = db.Column(
        db.String,
        default = wait_time
    )

    to_be_seated = db.Column(
        db.String
    )
    
    @classmethod
    def signup(cls, username, company_name, email, industry, street_address, street_address2, city, province_or_state, postal_code, contact_number, password, to_be_seated):
        """sign up user, hashes password and adds user to system"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        organization = User(
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
            password = hashed_pwd,
            to_be_seated = to_be_seated
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
            
    customer = db.relationship('Unauth_Customer', backref="organization", cascade="all, delete-orphan")

    def set_password(self, password, commit = False):
        """set new password in the event the user is updating password"""
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        self.password = hashed_pwd

        if commit:
            db.session.commit()

    def get_reset_token(self, expires=500):
        """get token to reset"""
        print(os.getenv('SECRET_KEY'))
        return jwt.encode({'reset_password': self.username, 'exp':time() + expires},
                          key=environ.get("SECRET_KEY"), algorithm="HS256")

    @staticmethod
    def verify_reset_token(token):
        try:
            username = jwt.decode(token, key=environ.get("SECRET_KEY"), algorithms=["HS256"])['reset_password']
            print(username)
        except Exception as e:
            print(e)
            return
        return User.query.filter_by(username = username).first()
    
    @staticmethod
    def verify_email(email):
        user = User.query.filter_by(email = email).first()
        return user
            

class Unauth_Customer(db.Model):
    """customer to join queue that are not authenticated"""
    __tablename__ = "unauth_customer"
    id = db.Column(
        db.Integer,
        primary_key = True
    )

    first_name = db.Column(
        db.String(50),
        nullable = False
    )

    last_name = db.Column(
        db.String(50),
        nullable = False
    )

    email = db.Column(
        db.String(100),
        nullable = False,
        unique = True
    )

    code = db.Column(
        db.Integer,
        nullable = False
    )

    contact_number = db.Column(
        db.BIGINT(), 
        nullable = False,
        unique = True
    )

    organization_id = db.Column(
        db.Integer,
        db.ForeignKey('organizations.id')
    )

    tag = db.Column(
        db.String,
        nullable = False
    )

    status = db.Column(
        db.String,
        nullable = False
    )


    def __repr__(self):
        return f"<Unauth_Customer #{self.id}: {self.first_name}, {self.last_name}, {self.email}, {self.code}, {self.contact_number}, {self.organization_id}, {self.tag}, {self.status}>"


def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)


