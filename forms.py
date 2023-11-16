import email_validator
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, BooleanField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, URL, Optional


industry_choices = [
    ('tech', 'Information Technology'),
    ('health', 'Healthcare'),
    ('finance', 'Finance'),
    ('manufacturing', 'Manufacturing'),
    ('retail', 'Retail'),
    ('education', 'Education'),
    ('hospitality', 'Hospitality'),
    ('agriculture', 'Agriculture'),
    ('entertainment', 'Entertainment'),
    ('transportation', 'Transportation'),
    ('energy', 'Energy'),
    ('telecom', 'Telecommunications'),
    ('real_estate', 'Real Estate'),
    ('automotive', 'Automotive'),
    ('media', 'Media and Publishing'),
    ('construction', 'Construction'),
    ('non_profit', 'Non-profit'),
    ('government', 'Government'),
    ('aerospace', 'Aerospace'),
    ('pharmaceuticals', 'Pharmaceuticals'),
    ('other', 'Other')
]
    

class OrganizationSignUpForm(FlaskForm):
    """Forms for companies to sign up"""
    username = StringField("Username", validators = [DataRequired()])
    company_name = StringField("Company Name", validators = [DataRequired()])
    email = StringField("Contact Email", validators = [DataRequired(), Email()])
    industry = SelectField('Industry', choices = industry_choices)
    street_address = StringField('Street Address', validators = [DataRequired()])
    street_address2 = StringField('Street Address line 2')
    city = StringField('city', validators=[DataRequired()])
    province_or_state = StringField('State, or Province', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(6)])
    contact_number = StringField('Contact Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class StartQueueForm(FlaskForm):
    """Forms to start a queue"""
    location = StringField('City', validators=[DataRequired()])
    waittime = BooleanField('Is there an average wait time included in this queue')
    average_waittime = IntegerField('Enter average wait time in minutes')
    max_capacity = IntegerField('Max Queue Capacity')

class CustomerSignUpForm(FlaskForm):
    """Form for user to sign up"""
    username = StringField("Username", validators = [DataRequired()])
    email = StringField("Contact Email", validators = [DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    organizations = SelectMultipleField('Favorite Organizations')


class OrganizationLoginForm(FlaskForm):
    """Form to login as an organization"""
    username = StringField("Username", validators = [DataRequired()])
    password = PasswordField('String', validators=[DataRequired()])

class CustomerLoginForm(FlaskForm):
    """Form to login as a user"""
    username = StringField("Username", validators = [DataRequired()])
    password = PasswordField('String', validators=[DataRequired()])
