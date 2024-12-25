import json
from app.models import Coupon, DateIdea

def load(db):
    def load_coupons():
        with open('app/static/coupons.json') as f:
            coupons = json.load(f)
            for coupon in coupons:
                if not Coupon.query.filter_by(title=coupon['title']).first():
                    db.session.add(Coupon(
                        title=coupon['title'],
                        description=coupon['description'],
                        image=coupon['image'],
                        redeemed=coupon['redeemed']
                    ))
            db.session.commit()

    def load_dates():
        with open('app/static/dates.json') as f:
            dates = json.load(f)
            for date in dates:
                if not DateIdea.query.filter_by(title=date['title']).first():
                    db.session.add(DateIdea(
                        title=date['title'],
                        description=date['description'],
                        image=date['image'],
                        location=date['location']
                    ))
            db.session.commit()

    load_coupons()
    load_dates()