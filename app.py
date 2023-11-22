import os
import pdb

from flask import Flask, render_template, session, redirect, request
from flask_login import LoginManager, login_user, logout_user, current_user
from models import db, connect_db, Organization, Customer, Queue
from forms import OrganizationSignUpForm, StartQueueForm, CustomerLoginForm, CustomerSignUpForm, OrganizationLoginForm
from queue_functionality import start_queue, join_queue, dequeue, dequeue_and_hold
from sqlalchemy.exc import IntegrityError
from flask_session import Session
from flask_socketio import SocketIO

app = Flask(__name__, template_folder = "templates")

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///virque'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'n2BxpDIorno08ai6oI47ew'
app.config['SESSION_TYPE'] = 'filesystem'

#connect to socket io
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
def load_organization(organization_id):
    return Organization.get(organization_id)

@login_manager.user_loader
def load_customer(customer_id):
    return Customer.get(customer_id)

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
        organization = Organization.authenticate(
            username = form.username.data,
            password=form.password.data
        )
        
        if organization:
            session['organization_id'] = organization.id
        else:
            return redirect('/')
        
        return render_template('organization/home.html')
    else:
        """show form"""
        return render_template('organization/login.html', form=form)


@app.route('/organization/home', methods = ['GET', 'POST'])
def organization_home():
    """show home page for logged in organization"""
    organization_id = session['organization_id']
    organization = Organization.query.get(organization_id)
    queues = Queue.query.filter_by(organization_id = organization_id).all()

    print(queues)

    return render_template('organization/home.html', organization = organization, queues = queues)


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
            organizations_id = request.form.getlist('organizations')
        ) 

        db.session.commit()

        return render_template('customer/home.html', customer = customer)
    else:
        """show form"""
        print (request.form.getlist('organizations'))
        print(form.username.data)
        print(form.email.data)
        print(form.password.data)
        
        return render_template('customer/signup.html', form=form)

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
        
        return render_template('customer/home.html', customer = customer)
    else:
        """show form"""
        return render_template('customer/login.html', form=form)
    
#---------------------------QUEUE---------------------------------------------------
@app.route('/organization/start_queue', methods=['GET', 'POST'])
def organization_start_queue():
    """Show form for organizations to sign up and if already sign"""
    form = StartQueueForm()
    if form.validate_on_submit():
        """Get form data and add to database"""
        location = form.location.data
        avg_wait_time = request.form.get('average_waittime', 0)
        max_capacity = request.form.get('max_capacity', 0)
        name = form.queue_name.data

        organization_id = session['organization_id']
        queue_name = start_queue(
            queue_name = name,
            organization_id = organization_id, 
            max_capacity = max_capacity, 
            avg_waittime = avg_wait_time
            )
        
        session[name] = queue_name
        
        return redirect('/organization/home')

    else:
        """show form"""
        return render_template('organization/start_queue.html', form=form)
    
@app.route('/customer/view_queues', methods = ['GET', 'POST'])
def show_current_queues():
    """show current queues in the system"""
    queues = Queue.query.all()
    return render_template('customer/view_queues.html', queues = queues)
    
@app.route('/customer/join_queue/<int:queue_id>', methods = ['GET', 'POST'])
def customer_join_queue(queue_id):
    """get queue from database"""
    queue = Queue.query.get_or_404(queue_id)
    print(session.get[f"{queue.name}"])
    pdb.set_trace()
    return