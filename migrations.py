from app import create_app, db
from app.models import User, Wallet, Transaction, CryptoBalance

def migrate_database():
    app = create_app()
    with app.app_context():
        # Drop existing tables
        db.drop_all()
        
        # Create tables with new schema
        db.create_all()
        
        print("Database migration completed successfully!")

if __name__ == '__main__':
    migrate_database() 