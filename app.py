import os
import pdb

from flask import Flask, render_template, session, redirect, request
from flask_login import LoginManager, login_user, logout_user, current_user
from models import db, connect_db, Organization, Customer, Queue
from forms import OrganizationSignUpForm, StartQueueForm, CustomerLoginForm, CustomerSignUpForm, OrganizationLoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__, template_folder = "templates")

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///virque'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.app_context().push()

app.secret_key = 'ca149690e36dabf401815d5a6f4cc138e191eed6be52b608193000f59cd4209a'
connect_db(app)

#FLASK login

login_manager = LoginManager(app)

@login_manager.user_loader
def load_organization(organization_id):
    return Organization.get(organization_id)

@login_manager.user_loader
def load_customer(customer_id):
    return Customer.get(customer_id)

#------------------------------------------------HOME----------------------------------------------------------------

@app.route('/')
def homepage():
    """show home page for app"""
    return render_template('base.html')

#------------------------------------------ORGANIZATION---------------------------------------------------------------------
@app.route('/organization/signup', methods=['GET', 'POST'])
def organization_signup():
    """Show form for organizations to sign up and if already sign"""
    form = OrganizationSignUpForm()
    if form.validate_on_submit():
        """Get form data and add to database"""
        try:
            organization = Organization.signup(
                username = form.username.data,
                company_name = form.company_name.data,
                email = form.email.data,
                industry = form.industry.data,
                street_address= form.street_address.data, 
                street_address2= form.street_address2.data or None,
                city = form.city.data,
                province_or_state=form.province_or_state.data,
                contact_number = form.contact_number.data,
                postal_code=form.postal_code.data,
                password=form.password.data
            )
            db.session.commit()
            
        except IntegrityError as err:
            print(err.args.Key)
            pdb.set_trace()

        return render_template('organizations/home.html', organization = organization)
    else:
        """show form"""
        return render_template('organizations/signup.html', form=form)

@app.route('/organization/login', methods=['GET', 'POST'])
def organization_login():
    """Show form for organizations to sign up and if already sign"""
    form = OrganizationLoginForm()
    if form.validate_on_submit():
        """Get form data and add to database"""
        organization = Organization.authenticate(
            username = form.username.data,
            password=form.password.data
        )
        
        if organization:
            login_user(organization)
        else:
            return redirect('/')
        
        return render_template('organizations/home.html')
    else:
        """show form"""
        return render_template('organizations/login.html', form=form)

@app.route('/organization/start_queue', methods=['GET', 'POST'])
def organization_start_queue():
    """Show form for organizations to sign up and if already sign"""
    form = StartQueueForm()
    if form.validate_on_submit():
        """Get form data and add to database"""
        return 'a'
    else:
        """show form"""
        return render_template('organizations/start_queue.html', form=form)


#---------------------------------------------------CUSTOMER----------------------------------------------------
@app.route('/customer')
def customer_home():
    """Show home page for customers not logged in"""
    return render_template('customers/home.html')

@app.route('/customer/signup', methods=['GET', 'POST'])
def customer_signup():
    """Show form for organizations to sign up and if already sign"""
    #get organizations in db
    organization_choices = [(organization.id, organization.company_name) for organization in Organization.query.all()]

    form = CustomerSignUpForm()
    form.organizations.choices = organization_choices
    if form.validate_on_submit():
        """Get form data and add to database"""

        customer = Customer.signup(
            username = form.username.data,
            email = form.email.data,
            password=form.password.data,
            organizationsID = request.form.getlist('organizations')
        ) 

        db.session.commit()

        return render_template('customers/home.html', customer = customer)
    else:
        """show form"""
        print (request.form.getlist('organizations'))
        
        return render_template('customers/signup.html', form=form)

@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    """Show form for organizations to sign up and if already sign"""
    form = CustomerLoginForm()
    if form.validate_on_submit():
        """Get form data and add to database and login user"""
        customer = Customer.authenticate(
            username=form.username.data,
            password=form.password.data
        )

        print(customer)
        
        if customer:
            login_user(customer)
        else:
            return redirect('/')
        
        return render_template('customers/home.html', customer = customer)
    else:
        """show form"""
        return render_template('customers/login.html', form=form)
