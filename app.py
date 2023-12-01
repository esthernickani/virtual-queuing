import os
import pdb
import json
import jsonpickle

from flask import Flask, render_template, session, redirect, request, url_for, flash, g
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from models import db, connect_db, User, Unauth_Customer
from forms import OrganizationSignUpForm, StartQueueForm, CustomerLoginForm, CustomerSignUpForm, OrganizationLoginForm
from queue_functionality import generate_code, create_unauth_customer_dict, get_tag
from sqlalchemy.exc import IntegrityError
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from threading import Lock

from linkedlist import LinkedList, Node

app = Flask(__name__, template_folder = "templates")

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///virque'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'n2BxpDIorno08ai6oI47ew'
app.config['SESSION_TYPE'] = 'filesystem'

#create an instance of socket io
socketio = SocketIO(app)
#connect to db
connect_db(app)

lock=Lock()

if __name__ == '__main__':
    socketio.run(app)

app.app_context().push()

Session(app)

#FLASK login

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#save user to g
"""@app.before_request
def add_organization_to_g():
    if current_user.is_authenticated:
        g.user = current_user.get_id"""
#------------------------------------------------HOME----------------------------------------------------------------

@app.route('/')
def homepage():
    """show home page for entire app both customers and organizations"""
    return render_template('base.html')
#------------------------------------------ORGANIZATION---------------------------------------------------------------------
@app.route('/organization/landing_page')
def show_organization_landing():
    """show home page for organization to login or signup"""
    return render_template('organization/landing_page.html')

#-----------------------------SOCKET IO----------------------------------------------------------------------
@socketio.on("connect")
def handle_connect():
    """handle clients(organizations and customers) connecting to server"""
    print('Client connected')

@socketio.on("join")
def activate_queue():
    """activate queue"""
    organization = User.query.get_or_404(current_user.get_id())
    if organization:
        if organization.queue_is_active == False:
            organization.queue_is_active = True
            db.session.commit()
            room = organization.username
            join_room(room)
            print(f"{room} queue has been activated")

@socketio.on("join_queue")
def join_queue(data):
   """join queue"""
   #get room from data sent from script.js-client side
   room = data['organizationName']
   join_room(room)
   
   #get tag to best describe customer or group of customers
   tag = get_tag(data['groupSize'])

   #create customer dict and make it a node to add to list from database
   customer = create_unauth_customer_dict(data['firstName'], data['lastName'], data['contactNumber'], data['email'], tag)
   customer_node = Node(customer)
   
   organization = User.query.filter_by(username = data['organizationName']).first()
   queue = jsonpickle.decode(organization.queue)
   print(f"queue---->{queue}")
   queue.insert_at_end(customer_node)
   updated_queue = jsonpickle.encode(queue)
   organization.queue = updated_queue
   db.session.commit()

   #get all unique codes to make sure unique code is not repeated
   
   new_customer_code = generate_code()
   new_customer = Unauth_Customer(
       first_name = data['firstName'],
       last_name = data['lastName'],
       email = data['email'],
       code = new_customer_code,
       contact_number =  data['contactNumber'],
       organization_id = organization.id
   )

   db.session.add(new_customer)
   db.session.commit()

   """socket redirect customer to the page that shows queue"""
   emit('redirect_customer', {'url': url_for('show_customer_on_queue')})

@app.route('/customer/waitlist')
def show_customer_on_queue():
    return render_template('customer/in_queue.html')

@app.route('/organization/signup', methods=['GET', 'POST'])
def organization_signup():
    """Show form for organizations to sign up and if already sign"""
    form = OrganizationSignUpForm()
    if form.validate_on_submit():
        """Get form data and add to database"""
        try:
            organization = User.signup(
                username = form.username.data,
                company_name = form.company_name.data,
                email = form.email.data,
                industry = form.industry.data,
                streetaaddress= form.street_address.data, 
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

        return render_template('organization/login.html', organization = organization)
    else:
        """show form"""
        return render_template('organization/signup.html', form=form)

@app.route('/organization/login', methods=['GET', 'POST'])
def organization_login():
    """Show form for organizations to sign up and if already sign"""
    form = OrganizationLoginForm()
    if form.validate_on_submit():
        """Get form data and add to database"""
        organization = User.authenticate(
            username = form.username.data,
            password=form.password.data
        )
        
        if organization:
            login_user(organization)
        else:
            return redirect('/')
        
        return render_template('organization/home.html')
    else:
        """show form"""
        return render_template('organization/login.html', form=form)


@app.route('/organization/home', methods = ['GET', 'POST'])
def organization_home():
    """show home page for logged in organization"""
    if session['organization_id']:
        organization_id = session['organization_id']
        organization = User.query.get(organization_id)
        return render_template('organization/home.html', organization = organization)
    else:
        flash("You need to be logged in to view this page")
        return redirect('/organization/login')


#---------------------------------------------------CUSTOMER----------------------------------------------------
@app.route('/customer')
def customer_home():
    """Show home page for customers logged in"""
    #if current_user.is_authenticated:
    return render_template('customers/home.html')
    #else:
        #return redirect('/customer/landing_page')

@app.route('/customer/landing_page')
def show_customer_landing():
    """show home page for customer not logged in"""
    return render_template('customer/landing_page.html')


    
#---------------------------QUEUE---------------------------------------------------
@app.route('/organization/queue', methods=['GET', 'POST'])
@login_required
def organization_queue():
    """Show form for organizations to sign up and if already sign"""
    organization = User.query.get_or_404(current_user.get_id())
    wait_time = jsonpickle.decode(organization.queue_wait_time)
    minimum_wait_time = wait_time['min']
    maximum_wait_time = wait_time['max']
    queue = jsonpickle.decode(organization.queue)
    return render_template('organization/queue.html', organization=organization, minimum_wait_time=minimum_wait_time, maximum_wait_time=maximum_wait_time, queue = queue)
    
@app.route('/customer/view_queues', methods = ['GET', 'POST'])
def show_current_queues():
    """show current queues in the system"""
    organizations = User.query.all()

    return render_template('customer/view_queues.html', organizations=organizations)
    
@app.route('/customer/join_queue/<int:queue_id>', methods = ['GET', 'POST'])
def customer_join_queue(queue_id):
    """get queue from database"""
    pdb.set_trace()
    return

