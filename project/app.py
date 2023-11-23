from GenericAlgorithm.index import findOptimizedPath, calculateDistanceForCustomer, calculateDistance

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from pymongo import MongoClient, ReturnDocument
from pymongo.server_api import ServerApi
import bcrypt
import folium
from bson import ObjectId
# from geopy.geocoders import Nominatim

app = Flask(__name__, static_folder='static')
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Setting up Cloud DB
# uri = "<MONGODB_URL>"
# client = MongoClient(uri, server_api=ServerApi('1'))
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

# Setting up Local DB
client = MongoClient('localhost', 27017)
db = client.AeroNav
orders = db.orders
users = db.users

@app.route("/", methods=['GET', 'POST'])
def sign_up():
    message = ''
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    if request.method == "POST":
        user = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        address = request.form.get('address')
        # geolocator = Nominatim(user_agent="app")
        # location = geolocator.geocode(address)
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
                    'x_cord' : 18.521428,
                    'y_cord' : 73.8544541,
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
        print(user['type'])
        if user:
            if bcrypt.checkpw(request.form['password'].encode('utf-8'), user['encrypt_pass']):
                session['_id'] = user['_id']
                print(session['_id'])
                if user['type']=='Customer':
                    return redirect('/customer/orders')
                else:
                    return redirect('/distributor/orders')
                # return render_template('index.html')
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
    customer_id = session['_id']
    if request.method == 'POST':
        order['customers'].append(ObjectId(customer_id))
        order = orders.find_one_and_replace({'_id':ObjectId(id)}, order, return_document=ReturnDocument.AFTER)
    order['created_by'] = users.find_one({'_id':order['created_by']})
    if order['is_optimized']:
        customer = users.find_one({'_id':ObjectId(customer_id)})
        order['data'] = calculateDistanceForCustomer(order['optimized_path'], customer['x_cord'], customer['y_cord'])
    return render_template('customers/order.html', order=order, _id2=session['_id'])

@app.route('/distributor/order',methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        distributor_id = session['_id']
        order = orders.insert_one({
            'title' : request.form.get('title'),
            'created_by' : distributor_id,
            'customers' : [],
            'is_optimized' : False, 
            'optimized_path' : [],
            'vehicles' : request.form.get('vehicles'),
            'velocity' : request.form.get('velocity'),
            "timestamp": datetime.utcnow()
        }) 
        return redirect('/distributor/orders/' + str(order.inserted_id))
    return render_template('distributors/create_order.html')

@app.route('/distributor/orders',methods=['GET'])
def view_my_orders():
    all_orders = orders.find({'created_by' : session['_id']})
    return render_template('distributors/orders.html', orders=all_orders)

@app.route('/distributor/orders/<id>',methods=['GET', 'POST'])
def view_my_order(id):
    order = orders.find_one({'_id':ObjectId(id)})
    order['created_by'] = users.find_one({'_id':order['created_by']})
    for i in range(0,len(order['customers'])):
        order['customers'][i] = users.find_one({'_id':ObjectId(order['customers'][i])})

    if request.method == 'POST' and request.args.get('_method') == 'DELETE':
        orders.delete_one({'_id':ObjectId(id)})
        return redirect('/distributor/orders')
    
    elif request.method == 'POST':
        optimized_path = findOptimizedPath(order['customers'],order['created_by'],order['vehicles'])
        orderCopy = orders.find_one({'_id':ObjectId(id)})
        orderCopy['optimized_path'] = optimized_path
        orderCopy['is_optimized'] = True
        orders.find_one_and_replace({'_id':ObjectId(id)}, orderCopy, return_document=ReturnDocument.AFTER)
        return redirect('/distributor/orders/'+id+'/visualize')
    
    if order['is_optimized']:
        order['data'] = calculateDistance(order['optimized_path'])
    return render_template('distributors/order.html', order=order)

@app.route('/distributor/orders/<id>/visualize',methods=['GET'])
def visualize_my_order(id):
    order= orders.find_one({'_id':ObjectId(id)})
    if not order['is_optimized']:
        return redirect('/distributor/orders/'+id)
    
    map = folium.Map(location=order['optimized_path'][0][0], zoom_start=13)
    colors = ['blue','red','green','orange','violet','black']
    map_path = 'templates/map.html'
    i=0
    for vehicleRoute in order['optimized_path']:
        route = folium.PolyLine(locations=vehicleRoute, color=colors[i])
        i += 1
        for each in vehicleRoute:
          folium.Marker(each).add_to(map)
        route.add_to(map)
    map.save(map_path)
    return render_template('map.html', map_path=map_path)

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

if __name__ == "__main__":
    app.run(debug=True)