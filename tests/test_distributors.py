from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from pymongo import MongoClient, ReturnDocument
import test_registration
from bson import ObjectId

client = MongoClient('localhost', 27017)
db = client.AeroNav
orders = db.orders
users = db.users

def test_addOrderToDb(client, app):
    test_registration.test_signUpGet(client)
    test_registration.test_signUpFormPostDistributor(client, app)
    test_registration.test_signInGet(client)
    test_registration.test_signInFormPostDistributor(client, app)
    user = users.find_one({"username": "Mia"})
    # print(user)
    client.post("/distributor/order", data={
            'title' : 'My Fav Order',
            'created_by' : user['_id'],
            'customers' : [],
            'is_optimized' : False, 
            'optimized_path' : [],
            'vehicles' : 0,
            "timestamp": datetime.utcnow()
        })

    with app.app_context():
        assert orders.find_one({'title' : 'My Fav Order'})

# def test_distributorViewOrders(client, app):
#     test_addOrderToDb(client, app)
#     response = client.get("/distributor/orders")
#     assert b"<title>Distributors Orders</title>" in response.data