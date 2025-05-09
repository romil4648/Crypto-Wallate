# WARNING: Do not commit real secrets or credentials to public repos.
from flask_pymongo import PyMongo
from flask import Flask
import os

# You can import this mongo object in your app
mongo = PyMongo()

def init_mongo(app: Flask):
    app.config['MONGO_URI'] = os.environ.get(
        'MONGO_URI',
        'your_mongodb_connection_string_here'  # <-- Insert your MongoDB URI here or use environment variable
    )
    # Initialize MongoDB connection
    mongo.init_app(app)
    return mongo
