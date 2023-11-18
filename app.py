from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient, ReturnDocument
from bson import ObjectId

app = Flask(__name__)

# Setting up DB
client = MongoClient('localhost', 27017)
db = client.AeroNav
orders = db.orders
users = db.users

@app.route("/")
def hello_world():
    return render_template('index.html')

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

