from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def load_user(user_id):
    return User.query.get(int(user_id))

def recreate_changed_tables(app, db):
    with app.app_context():
        # Get existing tables
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        for table_name in existing_tables:
            existing_columns = {column['name'] for column in inspector.get_columns(table_name)}
            if table_name in db.metadata.tables:
                model_columns = {c.name for c in db.metadata.tables[table_name].columns}
                
                # If columns don't match, recreate table
                if existing_columns != model_columns:
                    db.metadata.tables[table_name].drop(db.engine)
                    db.create_all()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    nylas_grant_id = db.Column(db.String(255), unique=True, nullable=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    redeemed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image': self.image,
            'redeemed': self.redeemed
        }

class DateIdea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'image': self.image,
            'location': self.location
        }