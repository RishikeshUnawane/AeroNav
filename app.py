from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from pymongo import MongoClient, ReturnDocument
import bcrypt
from bson import ObjectId
from geopy.geocoders import Nominatim

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Setting up DB
client = MongoClient('localhost', 27017)
db = client.AeroNav
orders = db.orders
users = db.users

@app.route("/", methods=['GET', 'POST'])
def sign_up():
    message = ''
    if request.method == "POST":
        user = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        address = request.form.get('address')
        geolocator = Nominatim(user_agent="app")
        location = geolocator.geocode(address)
        user_found = users.find_one({"username": user})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('users/index.html', message=message)
        else:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user_input = {
                    'username': user,
                    'encrypt_pass': hashed, 
                    'type': user_type, 
                    'location' : address,
                    'x_cord' : location.latitude,
                    'y_cord' : location.longitude,
                    "timestamp": datetime.utcnow()
                    }
            x = users.insert_one(user_input)
            print(x)
            return redirect('/login')
    return render_template('users/index.html')

# Signin route
@app.route('/login', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        user = users.find_one({'username': request.form['username']})
        if user:
            if bcrypt.checkpw(request.form['password'].encode('utf-8'), user['encrypt_pass']):
                session['_id'] = user['_id']
                print(session['_id'])
                return render_template('index.html')
            return render_template('users/login.html', message='Invalid username/password combination')
        return render_template('users/login.html', message='User not found!')
    return render_template('users/login.html')

@app.route('/customer/orders',methods=['GET'])
def view_orders():
    all_orders = orders.find()
    return render_template('customers/orders.html', orders=all_orders)

@app.route('/customer/orders/<id>',methods=['GET', 'POST'])
def view_order(id):
    order = orders.find_one({'_id':ObjectId(id)})
    if request.method == 'POST':
        customer_id = 'addAnyExistingCustomerID'                      #TODO: take user ID from session or middle after adding authendication
        order['customers'].append(ObjectId(customer_id))
        order = orders.find_one_and_replace({'_id':ObjectId(id)}, order, return_document=ReturnDocument.AFTER)
    return render_template('customers/order.html', order=order)

#Adds sample data to DB
@app.route('/populateDB', methods=["GET"])
def populateDB():
    users.insert_one({
        'username' : 'Jhon',
        'encrypt_pass' : 'hello@1$',
        'type' : 'customer',
        'location' : 'Pune',
        'x_cord' : 18.5204,
        'y_cord' : 73.8567,
        "timestamp": datetime.utcnow()
    })
    user = users.insert_one({
        'username' : 'Mia',
        'encrypt_pass' : 'hello@1$',
        'type' : 'distributor',
        'location' : 'Pune',
        'x_cord' : 18.5204,
        'y_cord' : 73.8567,
        "timestamp": datetime.utcnow()
    })
    orders.insert_one({
        'title' : 'My Fav Order',
        'created_by' : user.inserted_id,
        'customers' : [],
        'is_optimized' : False, 
        'optimized_path' : [],
        'vehicles' : 0,
        "timestamp": datetime.utcnow()
    })  
    return "DB updated with sample data!"

