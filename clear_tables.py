import argparse
import os
import dotenv
from flask import Flask
from app.models import Coupon, DateIdea, User
from app.models import db

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

if __name__ == '__main__':
    # Create minimal Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    db.init_app(app)
    
    with app.app_context():
        parser = argparse.ArgumentParser(description='Clear or drop tables in the database.')
        parser.add_argument('tables', metavar='T', type=str, nargs='+', 
                            help='List of tables to clear or drop')
        parser.add_argument('action', choices=['clear', 'drop'], help='Action to perform on the tables')
        args = parser.parse_args()

        for table in args.tables:
            if args.action == 'clear':
                clear_table(table)
            elif args.action == 'drop':
                drop_table(table)