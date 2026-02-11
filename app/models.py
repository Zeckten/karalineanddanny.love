from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    nylas_grant_id = db.Column(db.String(255), unique=False, nullable=True)
    admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=False)
    redeemed = db.Column(db.Boolean, default=False)
    creator = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image': self.image,
            'redeemed': self.redeemed,
            'creator': self.creator
        }

class DateIdea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    creator = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'image': self.image,
            'location': self.location
        }