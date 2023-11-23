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

def test_customerViewOrders(client, app):
    test_registration.test_signUpGet(client)
    test_registration.test_signUpFormPostCustomer(client, app)
    test_registration.test_signInGet(client)
    test_registration.test_signInFormPostCustomer(client, app)
    response = client.get("/customer/orders")
    assert b"<title>Orders</title>" in response.data

# def test_customerViewOrdersId(client, app):
#     test_customerViewOrders(client, app)
#     order = orders.find_one({'title' : 'My Fav Order'})
#     response = client.get("/customer/orders/"+str(order['_id']))
#     assert b"<title>Order</title>" in response.data