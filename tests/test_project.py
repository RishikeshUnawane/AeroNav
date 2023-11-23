from GenericAlgorithm.index import findOptimizedPath
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from pymongo import MongoClient, ReturnDocument
from pymongo.server_api import ServerApi
from app import create_app

client = MongoClient('localhost', 27017)
db = client.AeroNav
orders = db.orders
users = db.users


def test_signUpGet(client):
    response = client.get("/")
    assert b"<title> Registration Form </title>" in response.data
    assert b"<label for=\"Username\" class=\"details\">Username</label>" in response.data
    assert b"<label for=\"InputPassword\" class=\"details\">Password</label>" in response.data
    assert b"<label for=\"User\" class=\"details\">Type of user</label>" in response.data
    assert b"<label for=\"Address\" class=\"details\">Address</label>" in response.data
    assert b"<input type=\"submit\" value=\"Register\">" in response.data

def test_signUpFormPost(client, app):
    response = client.post("/", data={
            'username' : 'Jhon',
            'encrypt_pass' : 'hello@1$',
            'type' : 'customer',
            'location' : 'Pune',
            'x_cord' : 18.5204,
            'y_cord' : 73.8567,
            "timestamp": datetime.utcnow()
    })

    with app.app_context():
        assert users.find_one({"username": "Jhon"})

def test_signUpFormError(client, app):
    test_signUpFormPost(client, app)
    if users.find_one({"username": "user"}):
        response = client.get("/")
        assert b"<p>There already is a user by that name</p>" in response.data

def test_signInGet(client):
    response = client.get("/login")
    assert b"<div class=\"title\">Login</div>" in response.data
    assert b"<label for=\"Username\" class=\"details\">Username</label>" in response.data
    assert b"<label for=\"InputPassword\" class=\"details\">Password</label>" in response.data
    assert b"<input type=\"submit\" value=\"Login\">" in response.data

def test_signInFormPost(client, app):
    response = client.post("/login", data={
        'username' : 'Jhon',
        'encrypt_pass' : 'hello@1$'
    })

    with app.app_context():
        assert users.find_one({"username": "Jhon"})

def test_signInFormError(client, app):
    test_signInGet(client)
    test_signInFormPost(client, app)
    user = users.find_one({"username": "Jhon"})
    if user:
        response = client.get("/")
        if user['encrypt_pass']=='123':
            assert b"<p>Invalid username/password combination</p>" in response.data
    test_signInGet(client)
    if users.find_one({"username": "user"}):
        assert b"<p>User not found!</p>" in response.data
