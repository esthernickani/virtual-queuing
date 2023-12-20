import os
import pdb
import json
import jsonpickle

from flask import Flask, render_template, session, redirect, request, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from models import db, connect_db, User, Unauth_Customer
from forms import OrganizationSignUpForm, StartQueueForm, CustomerLoginForm, CustomerSignUpForm, OrganizationLoginForm, EditOrganizationProfileForm
from queue_functionality import generate_code, create_unauth_customer_dict, get_tag, get_current_wait_time, get_current_time, get_position, remove_customer, create_wait_time_for_db, get_position_ordinal, get_coords, get_wait_time
from sqlalchemy import exc
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from api_requests import send_dequeue_message, send_join_queue_message, send_delete_message, get_distance_traveltime
from flask_mail import Mail, Message
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from os import environ, path
from dotenv import load_dotenv
from config import Configuration


from linkedlist import LinkedList, Node

app = Flask(__name__, template_folder = "templates")



mail = Mail(app)

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

app.config['SECRET_KEY'] = environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///virque'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['SESSION_TYPE'] = 'filesystem'

app.config['MAIL_PORT'] = 587
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_USERNAME'] = 'virque45@gmail.com'
app.config['MAIL_PASSWORD'] = environ.get("PASSWORD")
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USE_TLS'] = True

#create an instance of socket io
socketio = SocketIO(app)
#connect to db
connect_db(app)

if __name__ == '__main__':
    socketio.run(app)

app.app_context().push()

mail = Mail(app)

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
def send_email(user):
    """function to send email to user to reset password"""
    token = user.get_reset_token()

    msg = Message()
    msg.subject = "VIRQUE Password Reset"
    msg.sender = mail.username
    msg.recipients = [user.email]
    reset_url = url_for('reset_verified', user=user, token=token, _external=True)
    msg.html = render_template('organization/email-template-flask.html', reset_url=reset_url)

    mail.send(msg)

@app.route('/')
def homepage():
    """show home page for entire app both customers and organizations"""
    return render_template('base.html')
#------------------------------------------ORGANIZATION---------------------------------------------------------------------
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
                password=form.init_password.data, 
                to_be_seated = jsonpickle.encode(LinkedList())
            )
            if organization: 
                db.session.commit()
            
        except exc.IntegrityError as e:
            if 'organizations_company_name_key' in str(e):
                flash("Company name already taken", 'error')
            elif 'organizations_email_key' in str(e):
                flash("Email address already taken", 'error')
            elif 'organizations_username_key' in str(e):
                flash("Username already taken", 'error')
            
            return render_template('organization/signup.html', form=form)
        
        return redirect('organization/login')
    else:
        """show form"""
        return render_template('organization/signup.html', form=form)
    


@app.route('/organization/login', methods=['GET', 'POST'])
def organization_login():
    """Show form for organizations to login """
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
            flash('Invalid username or password', 'error')
            return redirect('/')
        
        return redirect('/organization/queue')
    else:
        """show form"""
        return render_template('organization/login.html', form=form)
    

@app.route('/organization/logout', methods = ['GET', 'POST'])
def organization_logout():
    """logout organization"""
    logout_user()
    flash("You have been logged out successfully")
    return redirect('/')


#ORGANIZATION QUEUE FUNCTIONALITIES
@app.route('/organization/queue', methods=['GET', 'POST'])
@login_required
def organization_queue():
    """Show page for organization queue"""
    organization = User.query.get_or_404(current_user.get_id())
    #get wait time parameters
    wait_time_param = jsonpickle.decode(organization.queue_wait_time)
    minimum_wait_time = wait_time_param['min']
    maximum_wait_time = wait_time_param['max']
    #get queue 
    queue = jsonpickle.decode(organization.queue)
    to_be_seated = jsonpickle.decode(organization.to_be_seated)

    return render_template('organization/queue.html', organization=organization, minimum_wait_time=minimum_wait_time, maximum_wait_time=maximum_wait_time, queue = queue, to_be_seated = to_be_seated)

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

    emit('refresh_organization', {'url': f"/organization/queue"})


@app.route('/organization/<int:organization_id>/dequeue/<int:customer_code>')
def dequeue_customer(organization_id, customer_code):
    """function for organization to dequeue a customer, add customer to 'to be seated' and send SMS to the customer"""
    #add customer to be seated
    organization = User.query.get_or_404(organization_id)
    queue = jsonpickle.decode(organization.queue)
    be_seated_list = jsonpickle.decode(organization.to_be_seated)
    customer_in_db = Unauth_Customer.query.filter_by(code = customer_code).first()
    
    try:
        if be_seated_list.length == 5:
            flash('Check in some people waiting to be seated')
            return redirect('/organization/queue')
        else: 
            #get position of customer in queue 
            queue = jsonpickle.decode(organization.queue)
            customer_position_in_queue = get_position(queue, customer_code)
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
    except:
        flash('Request could not be completed, please try again or contact support', 'error')
        return redirect('/organization/queue')

@app.route('/organization/<int:organization_id>/check-in/<int:customer_code>')
def checkin_customer(organization_id, customer_code):
    """function for organization to check-in a customer, add customer to 'to be seated' and send SMS to the customer"""
    try:
        organization = User.query.get_or_404(organization_id)
        be_seated_list = jsonpickle.decode(organization.to_be_seated)
        #get position of customer in beseatedlist 
        customer_position_in_queue = get_position(be_seated_list, customer_code)
        #remove customer from queue
        customer = remove_customer(customer_position_in_queue, be_seated_list)
        updated_be_seated_list = jsonpickle.encode(be_seated_list)
        organization.to_be_seated = updated_be_seated_list
        db.session.commit()
        #remove customer from unauth customer db
        Unauth_Customer.query.filter_by(code = customer_code).delete()
        db.session.commit()

        flash(f"Customer {customer_code} has been checked in")
        return redirect('/organization/queue')
    except:
        flash('Request could not be completed, please try again or contact support', 'error')
        return redirect('/organization/queue')


@app.route('/organization/<int:organization_id>/delete/<int:customer_code>')
def delete_customer(organization_id, customer_code):
    """function for organization to delete a customer"""
    try:
        customer_in_db = Unauth_Customer.query.filter_by(code = customer_code).first()
        
        organization = User.query.get_or_404(organization_id)
        queue = jsonpickle.decode(organization.queue)
        #remove from the queue 
        #get position of customer in queue 
        customer_position_in_queue = get_position(organization, customer_code)
        #remove customer from queue
        customer = remove_customer(customer_position_in_queue, queue)
        #update queue of organization
        updated_queue = jsonpickle.encode(queue)
        organization.queue = updated_queue
        db.session.commit()
        #send SMS to customer that they have been removed from the queue
        #send_delete_message(customer_in_db.contact_number)
        #delete them from db
        flash(f"Customer {customer_code} has been successfully removed from the queue")
        Unauth_Customer.query.filter_by(code = customer_code).delete()
        db.session.commit()

        return redirect('/organization/queue')
    except:
        flash('Request could not be completed, please try again or contact support', 'error')
        return redirect('/organization/queue')
    
#ORGANIZATION PROFILE, HOME, SECURITY
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
        flash('Profile successfully edited', 'success')
        return redirect('/organization/profile/overview')
    else:
        return render_template('/organization/profile-edit.html', form=form)

@app.route('/organization/security/forgot-password', methods = ['GET', 'POST'])
def forgot_password():
    """"""
    if request.method == 'GET':
        return render_template('organization/reset-password.html')
    
    if request.method == 'POST':
        email = request.form['email']
        user = User.verify_email(email)
        print(user)
        send_email(user)
        return redirect('/organization/login')
    
@app.route('/organization/security/reset-password/<token>', methods = ['GET', 'POST'])
def reset_verified(token):
    """"""

    if request.method == 'POST':
        user = User.verify_reset_token(token)
        print(user)
        pdb.set_trace()
        if user:
            password = request.form.get('password')
            password_confirm = request.form.get('password_confirm')

            if password != password_confirm:
                flash('Password do not match', 'error')
            else:
                user.set_password(password, commit = True)
                flash('Password successfully reset', 'success')
            return redirect('/organization/login')
        

    return render_template("organization/reset-password-new.html")


@app.route('/organization/profile/queue_preferences/edit', methods = ['GET', 'POST'])
@login_required
def edit_wait_time():
    """edit wait time for queue"""
    organization = User.query.get(current_user.get_id())

    if request.method == 'GET':
        return render_template('/organization/edit_wait_time.html')
    
    if request.method == 'POST':
        min_waittime = request.form['low-range']
        max_waittime = request.form['high-range']
        
        wait_time = create_wait_time_for_db(int(min_waittime), int(max_waittime))

        organization.queue_wait_time = wait_time
        db.session.commit()

        flash("You have successfully edited your wait time")
        return redirect('/organization/queue')
    


@app.route('/organization/profile/security', methods = ['GET', 'POST'])
@login_required
def show_email_password():
    """function to show email and password"""
    organization = User.query.get_or_404(current_user.get_id())

    return render_template('/organization/security.html', organization = organization)
    
@app.route('/organization/profile/security/reset-email', methods = ['GET', 'POST'])
@login_required
def reset_email():
    """route for organization to reset email"""
    organization = User.query.get_or_404(current_user.get_id())

    if request.method == 'GET':
        return render_template('/organization/reset-email.html', organization = organization)

    if request.method == 'POST':
        new_email = request.form['email-address']
        confirm_email = request.form['email-address-confirm']

        if new_email != confirm_email:
            flash('Email addresses must match')
            
        else:
            organization.email = new_email
            db.session.commit()
            flash("Email address successfully changed")

        return redirect('/organization/profile/security')
    

@app.route('/organization/profile/security/reset-password', methods = ['GET', 'POST'])
@login_required
def reset_password():
    """route for organization to reset password"""
    if request.method == 'GET':
        #show form
        return render_template('/organization/reset-password-from-acc.html')
    
    if request.method == 'POST':
        organization = User.query.get_or_404(current_user.get_id())
        username = organization.username
        password = request.form['old-password']

        check_organization = User.authenticate(username, password)

        if check_organization:
            new_password = request.form['password']
            confirm_password = request.form['password_confirm']

            if new_password != confirm_password:
                flash('Passwords must match')
                return redirect('/organization/profile/security')
            
            check_organization.set_password(new_password, commit=True)
            flash("Password successfully changed")
        else: 
            flash("Old password is incorrect")
    
        return redirect('/organization/profile/security')

@app.route('/organization/deactivate_queue', methods = ['GET', 'POST'])
@login_required
def deactivate_queue():
    """deactivate queue, get form data, check queue .length as organization cannot deactivate a full queue"""
    if request.method == 'POST':
        if request.form.get('deactivate') == 'on':
            organization = User.query.get_or_404(current_user.get_id())
            queue = jsonpickle.decode(organization.queue)
            if queue.length != 0:
                flash('Empty queue before deactivating', 'error')
                return redirect('/organization/queue')
            else:
                organization.queue_is_active = False
                db.session.commit()
                flash('Queue successfully deactivated', "success")
                return redirect('/organization/queue')
    return



#CUSTOMER----------------------------------------------------------------------
@socketio.on("join_queue")
def join_queue(data):
    """join queue"""
    #get room from data sent from script.js-client side
    try:
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
    except Exception as error:
        print(error)
        flash('Request could not be completed, please try again or contact support', 'error')
        return redirect('/')



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
        flash('Not a valid code', 'error')
        return redirect('/')

@app.route('/customer/<int:customer_code>/waitlist')
def show_customer_on_queue(customer_code):
    customer = Unauth_Customer.query.filter_by(code = customer_code).first()
    if customer.status == 'In Queue':
        organization = User.query.filter_by(id = customer.organization_id).first()
        #get position of customer in queue 
        customer_position_in_queue = get_position_ordinal(organization, customer_code)
        #get wait time
        service_time_min, service_time_max = get_current_wait_time(organization.queue_wait_time)
        print(customer)
        return render_template('customer/in_queue.html', customer = customer, service_time_min = service_time_min, service_time_max = service_time_max, position = customer_position_in_queue, organization = organization)
    elif customer.status == "to be seated":
        return render_template('customer/check_in.html', customer=customer)
    else:
        flash("Invalid code or You are currently not in any queues")
        return redirect('/')

@app.route('/customer/<int:customer_code>/directions', methods=['POST', 'GET'])
def handle_directions(customer_code):
    """handle getting coords from javascript and rendering template to show directions"""
    #get organization location
    customer = Unauth_Customer.query.filter_by(code = customer_code).first()
    organization_id = customer.organization_id
    organization = User.query.get_or_404(organization_id)
    data = request.get_json()
    customer_org_coords = get_coords(organization, data)
    dist_time_response = get_distance_traveltime(data['travel_mode'], customer_org_coords)
    print(dist_time_response)

    distance_time = {
        'distance': dist_time_response[0],
        'time' : dist_time_response[1]
    }

    print (jsonify(distance_time))
    return jsonify(distance_time)

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
    if current_customer.status == 'In Queue':
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
    elif current_customer.status == "to be seated":
        
        flash("You have been successfully removed from the queue")
        return redirect('/')
        flash('Request could not be completed at this time, please try again or contact support', 'error')
        return redirect('/')


@app.route('/customer/view_queues', methods = ['GET', 'POST'])
def show_current_queues():
    """show current queues in the system"""
    try:
        organizations = User.query.all()
        organization_card_detail = [
            {"name" : organization.username, 
            "address" : organization.street_address,
        "length_of_queue" : jsonpickle.decode(organization.queue).length,
        "wait_time": (get_wait_time(organization.queue_wait_time)[0] * jsonpickle.decode(organization.queue).length, get_wait_time(organization.queue_wait_time)[1] * jsonpickle.decode(organization.queue).length)
        } for organization in organizations if organization.queue_is_active]
        
        return render_template('customer/view_queues.html', organization_card_detail=organization_card_detail)
    except Exception as error:
        print(error)
        flash('Request could not be completed, please try again or contact support', 'error')
        return redirect('/')

@app.route('/customer/join_queue', methods = ['GET', 'POST'])
def show_join_queue():
    """show view to join queue"""
    return render_template('/customer/join_queue.html')
#-----------------------------SOCKET IO----------------------------------------------------------------------
@socketio.on("connect")
def handle_connect():
    """handle clients(organizations and customers) connecting to server"""
    print(f'Client {request.sid} connected')

@socketio.on("disconnect")
def handle_disconnect():
    """handle clients(organizations and customers) connecting to server"""
    print('Client disconnected')

#OTHER

@login_manager.unauthorized_handler
def handle_unauthorized():
    """show unauthorized page"""
    return render_template('/organization/unauthorised.html')

