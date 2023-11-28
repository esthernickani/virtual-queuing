from models import User, db

"""drop all existing tables"""
db.drop_all()
db.create_all()


#Add organizations
WestField = User.signup(
    username = 'westfield',
    company_name = 'Westfield Corporation',
    email = 'westfield@yahoo.com',
    industry = 'retail',
    street_address= '898 Casia Road NW', 
    street_address2= None,
    city = 'Edmonton',
    province_or_state='Alberta',
    contact_number = 5875873874,
    postal_code= 'T5Y6H7',
    password='helloworld'
)

MiaHealthCare = User.signup(
    username = 'miahealthcare',
    company_name = 'Mia Health Centre',
    email = 'miahc@yahoo.com',
    industry = 'health',
    street_address= '09 Casia Road NW', 
    street_address2= None,
    city = 'Edmonton',
    province_or_state='Alberta',
    contact_number = 5877873874,
    postal_code= 'T4T5H7',
    password='helloworld'
)

Kidon = User.signup(
    username = 'kidon',
    company_name = 'Kidon',
    email = 'kidon@yahoo.com',
    industry = 'telecom',
    street_address= '875 Imina Road SW', 
    street_address2= None,
    city = 'Edmonton',
    province_or_state='Alberta',
    contact_number ='7805487643',
    postal_code= 'T5M8H7',
    password='helloworld'
)

Winners = User.signup(
    username = 'winners',
    company_name = 'Winners',
    email = 'winners@yahoo.com',
    industry = 'retail',
    street_address= '12060 104 Ave NW', 
    street_address2= None,
    city = 'Edmonton',
    province_or_state='Alberta',
    contact_number = 5878765476,
    postal_code= 'T5K0G6',
    password='helloworld'
)

db.session.commit()

