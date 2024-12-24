
from flask import Blueprint, jsonify
from app import db
from app.models import Coupon, DateIdea

api = Blueprint('api', __name__)

@api.route('/api/coupons', methods=['GET'])
def get_coupons():
    coupons = Coupon.query.all()
    return jsonify([coupon.to_dict() for coupon in coupons])

@api.route('/api/dates', methods=['GET'])
def get_dates():
    dates = DateIdea.query.all()
    return jsonify([date.to_dict() for date in dates])