from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

from bson.objectid import ObjectId
from app.mongo_user import MongoUser

@login_manager.user_loader
def load_user(user_id):
    # Load user from MongoDB by ObjectId string
    from app.mongo_setup import mongo
    user_doc = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if user_doc:
        return MongoUser(user_doc)
    return None

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    wallets = db.relationship('Wallet', backref='owner', lazy='dynamic')
    crypto_balances = db.relationship('CryptoBalance', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    blockchain_type = db.Column(db.String(32), nullable=False)
    address = db.Column(db.String(128), unique=True, nullable=False)
    private_key = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transactions = db.relationship('Transaction', backref='wallet', lazy='dynamic')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    from_address = db.Column(db.String(100), nullable=False)
    to_address = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    fee = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class CryptoBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crypto_type = db.Column(db.String(32), nullable=False)  # e.g., 'BTC', 'ETH'
    amount = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<CryptoBalance {self.crypto_type}: {self.amount}>'
