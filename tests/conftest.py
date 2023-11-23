import pytest
from app import create_app
from pymongo import MongoClient

@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    # with app.app_context():
    #     client = MongoClient('localhost', 27017)
    #     db = client.AeroNav
    #     orders = db.orders
    #     users = db.users
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()


# @pytest.fixture
# def client():
#     app = create_app({"TESTING": True})
#     with app.app_context():
#         client = MongoClient('localhost', 27017)
#         db = client.AeroNav
#         orders = db.orders
#         users = db.users
#     with app.test_client() as client:
#         yield client

# @pytest.fixture()
# def client(app):
#     return app.test_client()


# @pytest.fixture()
# def runner(app):
#     return app.test_cli_runner()