import os
import pdb
import json
import jsonpickle

from flask import Flask, render_template, session, redirect, request, url_for, flash, g
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from models import db, connect_db, User, Unauth_Customer
from forms import OrganizationSignUpForm, StartQueueForm, CustomerLoginForm, CustomerSignUpForm, OrganizationLoginForm, EditOrganizationProfileForm
from queue_functionality import generate_code, create_unauth_customer_dict, get_tag, get_current_wait_time, get_current_time, get_position, remove_customer
from sqlalchemy.exc import IntegrityError
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from api_requests import send_dequeue_message, send_join_queue_message

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
        g.user = .get_id"""
#------------------------------------------------HOME----------------------------------------------------------------

@app.route('/')
def homepage():
    """show home page for entire app both customers and organizations"""
    return render_template('base.html')
#------------------------------------------ORGANIZATION---------------------------------------------------------------------

#-----------------------------SOCKET IO----------------------------------------------------------------------
@socketio.on("connect")
def handle_connect():
    """handle clients(organizations and customers) connecting to server"""
    print(f'Client {request.sid} connected')

@socketio.on("disconnect")
def handle_disconnect():
    """handle clients(organizations and customers) connecting to server"""
    print('Client disconnected')

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
    time_joined = get_current_time()

    #get organization and current queue and users position in queue
    organization = User.query.filter_by(username = data['organizationName']).first()
    queue = jsonpickle.decode(organization.queue)

    #create customer dict and make it a node to add to list from database
    new_customer_code = generate_code()
    customer = create_unauth_customer_dict(data['firstName'], data['lastName'], int(data['contactNumber']), data['email'], tag, time_joined, new_customer_code)
    customer_node = Node(customer)

    customer_number = int(data['contactNumber'])

    queue.insert_at_end(customer_node)
    updated_queue = jsonpickle.encode(queue)
    organization.queue = updated_queue
    db.session.commit()

    #get all unique codes to make sure unique code is not repeated

    first_name = data['firstName'],

    new_customer = Unauth_Customer(
        first_name = first_name,
        last_name = data['lastName'],
        email = data['email'],
        code = new_customer_code,
        contact_number =  int(data['contactNumber']),
        organization_id = organization.id, 
        tag = tag, 
        status = 'In Queue'
    )

    db.session.add(new_customer)
    db.session.commit()

    #send_join_queue_message(organization.username, new_customer_code, customer_number)

    #send message to customer that they have joined queue
    #send_join_queue_message(organization.username, new_customer_code, customer_number)

    """socket redirect customer to the page that shows queue"""
    emit('redirect_customer', {'url': f"/customer/{new_customer_code}/waitlist"})

    # Check if an organization is active and inform them someone joined
    
    organization = User.query.get_or_404(current_user.get_id())
    if organization and organization.queue_is_active:
        room = organization.username
        join_room()
        emit('notify organization', {'first_name': first_name}, room=room)

@app.route('/organization/<int:organization_id>/dequeue/<int:customer_code>')
def dequeue_customer(organization_id, customer_code):
    """function for organization to dequeue a customer, add customer to 'to be seated' and send SMS to the customer"""
    #add customer to be seated
    organization = User.query.get_or_404(organization_id)
    queue = jsonpickle.decode(organization.queue)
    be_seated_list = jsonpickle.decode(organization.to_be_seated)
    customer_in_db = Unauth_Customer.query.filter_by(code = customer_code).first()

    if be_seated_list.length == 5:
        flash('Check in some people waiting to be seated')
        return redirect('/organization/queue')
    else: 
        #get position of customer in queue 
        customer_position_in_queue = get_position(organization, customer_code)
        #remove customer from queue
        customer = remove_customer(customer_position_in_queue, queue)
        #update queue of organization
        updated_queue = jsonpickle.encode(queue)
        organization.queue = updated_queue
        db.session.commit()
        #add to organization updated to be seated list
        be_seated_list.insert_at_end(customer)
        customer_in_db.status = "to be seated"
        updated_be_seated_list = jsonpickle.encode(be_seated_list)
        organization.to_be_seated = updated_be_seated_list
        db.session.commit()
        #send SMS to customer that they are ready to be checked in
        #send_dequeue_message(customer_in_db.contact_number)
        
    return redirect('/organization/queue')

@app.route('/organization/<int:organization_id>/dequeue/<int:customer_code>')
def delete_customer(organization_id, customer_code):
    """function for organization to delete a customer"""
    customer = Unauth_Customer.query.filter_by(code = customer_code).first()
    
    organization = User.query.get_or_404(organization_id)
    queue = jsonpickle.decode(organization.queue)

@app.route('/customer/check_code', methods=['GET', 'POST'])
def check_customer_code():
    """check if customer is in the db and show their page"""
    code = int(request.form["code"])
    customers = Unauth_Customer.query.all()
    all_customer_code = [customer.code for customer in customers]
    print(f"all customers -->{all_customer_code}")
    if code in all_customer_code:
        return redirect(f"/customer/{code}/waitlist")
    else:
        flash('Not a valid code')
        return redirect('/')

@app.route('/customer/<int:customer_code>/waitlist')
def show_customer_on_queue(customer_code):
    customer = Unauth_Customer.query.filter_by(code = customer_code).first()
    organization = User.query.filter_by(id = customer.organization_id).first()
    #get position of customer in queue 
    customer_position_in_queue = get_position(organization, customer_code)
    #get wait time
    service_time_min, service_time_max = get_current_wait_time(organization.queue_wait_time)
    
    return render_template('customer/in_queue.html', customer = customer, service_time_min = service_time_min, service_time_max = service_time_max, position = customer_position_in_queue, organization = organization)

@app.route('/customer/<int:customer_code>/directions', methods=['POST', 'GET'])
def handle_directions(customer_code):
    """handle getting coords from javascript and rendering template to show directions"""
    data = request.get_json()
    
    pdb.set_trace()

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
                street_address= form.street_address.data, 
                street_address2= form.street_address2.data or None,
                city = form.city.data,
                province_or_state=form.province_or_state.data,
                contact_number = form.contact_number.data,
                postal_code=form.postal_code.data,
                password=form.password.data, 
                to_be_seated = jsonpickle.encode(LinkedList())
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
        
        return redirect('/organization/queue')
    else:
        """show form"""
        return render_template('organization/login.html', form=form)


@app.route('/organization/home', methods = ['GET', 'POST'])
@login_required
def organization_home():
    """show home page for logged in organization"""
    if session['organization_id']:
        organization_id = session['organization_id']
        organization = User.query.get(organization_id)
        return render_template('organization/queue.html', organization = organization)
    else:
        flash("You need to be logged in to view this page")
        return redirect('/organization/login')

@app.route('/organization/profile/overview', methods = ['GET', 'POST'])
@login_required
def organization_profile():
    """show profile page for organization and edit"""
    organization = User.query.get_or_404(current_user.get_id())
    return render_template('/organization/profile.html', organization=organization)

@app.route('/organization/profile/overview/edit', methods = ['GET', 'POST'])
@login_required
def edit_organization_profile():
    """show profile page for organization and edit"""
    organization = User.query.get(current_user.get_id())
    form = EditOrganizationProfileForm(obj=organization)

    if form.validate_on_submit(): 
        #get form data and save to database and redirect to profile overview
        organization.username = form.username.data
        organization.company_name = form.company_name.data,
        organization.street_address= form.street_address.data, 
        organization.street_address2= form.street_address2.data or None,
        organization.city = form.city.data,
        organization.province_or_state=form.province_or_state.data,
        organization.contact_number = form.contact_number.data,
        organization.postal_code=form.postal_code.data

        db.session.commit()
        return redirect('/organization/profile/overview')
    else:
        return render_template('/organization/profile-edit.html', form=form)


"""@app.route('/organization/profile/queue_preferences', methods = ['GET', 'POST'])
@login_required
def organization_profile():


@app.route('/organization/profile/security', methods = ['GET', 'POST'])
@login_required
def organization_profile():
    
@app.route('/organization/profile/security/change-email', methods = ['GET', 'POST'])
@login_required
def organization_profile():

@app.route('/organization/profile/security/change-password', methods = ['GET', 'POST'])
@login_required
def organization_profile():"""

@app.route('/customer/<int:customer_code>/general_waitlist', methods = ['GET', 'POST'])
def view_general_waitlist(customer_code):
    """function for customer to view the general waitlist"""
    current_customer = Unauth_Customer.query.filter_by(code = customer_code).first()
    organization = User.query.filter_by(id = current_customer.organization_id).first()
    #get queue 
    queue = jsonpickle.decode(organization.queue)
    #get how many minutes ago the customer joined
    current_time = get_current_time()

    return render_template('/customer/general_waitlist.html', queue = queue, current_customer = current_customer, current_time = current_time)

@app.route('/customer/<int:customer_code>/leave_waitlist', methods = ['GET', 'POST'])
def leave_waitlist(customer_code):
    """function for customer to leave waitlist"""
    
    current_customer = Unauth_Customer.query.filter_by(code = customer_code).first()
    organization = User.query.filter_by(id = current_customer.organization_id).first()
    #get queue and remove indivdual from queue
    queue = jsonpickle.decode(organization.queue)
    queue.removeAtSpecificIdx(current_customer.position_in_queue - 1)
    updated_queue = jsonpickle.encode(queue)
    organization.queue = updated_queue
    db.session.commit()
    #delete from customer db
    Unauth_Customer.query.filter_by(code = customer_code).delete()
    #commit changes
    db.session.commit()

    flash("You have been successfully removed from the queue")
    return redirect('/')


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

@app.route('/customer/view_queues', methods = ['GET', 'POST'])
def show_current_queues():
    """show current queues in the system"""
    organizations = User.query.all()
    return render_template('customer/view_queues.html', organizations=organizations)

#---------------------------QUEUE---------------------------------------------------
@app.route('/organization/queue', methods=['GET', 'POST'])
@login_required
def organization_queue():
    """Show form for organizations to sign up and if already sign"""
    organization = User.query.get_or_404(current_user.get_id())
    #get wait time parameters
    wait_time_param = jsonpickle.decode(organization.queue_wait_time)
    minimum_wait_time = wait_time_param['min']
    maximum_wait_time = wait_time_param['max']
    #get queue 
    queue = jsonpickle.decode(organization.queue)
    to_be_seated = jsonpickle.decode(organization.to_be_seated)

    return render_template('organization/queue.html', organization=organization, minimum_wait_time=minimum_wait_time, maximum_wait_time=maximum_wait_time, queue = queue, to_be_seated = to_be_seated)
    
@app.route('/organization/logout', methods = ['GET', 'POST'])
def organization_logout():
    """logout organization"""
    logout_user()
    flash("You have been logged out successfully")
    return redirect('/')


