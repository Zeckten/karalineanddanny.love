import argparse
import os
import sys
import dotenv
from flask import Flask
from flask_migrate import upgrade, migrate, init, current, stamp

# Add the project directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import *

def clear_table(table_name):
    if table_name == 'coupons':
        db.session.query(Coupon).delete()
    elif table_name == 'dates':
        db.session.query(DateIdea).delete()
    elif table_name == 'users':
        db.session.query(User).delete()
    else:
        print(f"Unknown table: {table_name}")
        return
    db.session.commit()
    print(f"Cleared table: {table_name}")

def drop_table(table_name):
    if table_name == 'coupons':
        Coupon.__table__.drop(db.engine)
    elif table_name == 'dates':
        DateIdea.__table__.drop(db.engine)
    elif table_name == 'users':
        User.__table__.drop(db.engine)
    else:
        print(f"Unknown table: {table_name}")
        return
    print(f"Dropped table: {table_name}")

def reset_table(table_name):
    drop_table(table_name)
    db.create_all()  # Automatically migrate database schema if differences are detected
    print(f"Reset table: {table_name}")

def auto_migrate_database(app, db):
    from flask_migrate import Migrate, upgrade
    
    migrate = Migrate(app, db)
    with app.app_context():
        if not os.path.exists('migrations'):
            os.system('flask db init')
        os.system('flask db migrate')
        os.system('flask db upgrade')

if __name__ == '__main__':
    # Create minimal Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    db.init_app(app)
    
    with app.app_context():
        parser = argparse.ArgumentParser(description='Clear or drop tables in the database.')
        parser.add_argument('tables', metavar='T', type=str, nargs='+', 
                            help='List of tables to clear or drop')
        parser.add_argument('action', choices=['clear', 'drop', 'reset'], help='Action to perform on the tables')
        args = parser.parse_args()

        for table in args.tables:
            if args.action == 'clear':
                clear_table(table)
            elif args.action == 'drop':
                drop_table(table)
            elif args.action == 'reset':
                reset_table(table)