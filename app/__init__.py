from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_talisman import Talisman
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

from .mongo_setup import init_mongo, mongo

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    init_mongo(app)
    
    # Enable security headers
    talisman = Talisman(
        app,
        content_security_policy={
            'default-src': '\'self\'',
            'script-src': [
                '\'self\'',
                '\'unsafe-inline\'',
                'https://cdn.jsdelivr.net'
            ],
            'style-src': [
                '\'self\'',
                '\'unsafe-inline\'',
                'https://cdn.jsdelivr.net'
            ],
            'img-src': [
                '\'self\'',
                'data:',
                'https:'
            ],
            'font-src': [
                '\'self\'',
                'https://cdn.jsdelivr.net'
            ]
        },
        strict_transport_security=True
    )
    
    # Register blueprints
    from app.routes import main, auth, wallet
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(wallet)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
