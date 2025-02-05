from flask import Blueprint, render_template, redirect, url_for, flash, current_app, session, jsonify
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.forms import ChangePasswordForm
from app.models import User, DateIdea, Coupon, db
import logging
import os

main = Blueprint('main', __name__, url_prefix='/')

@main.route("/")
@login_required
def index():
    return redirect(url_for('main.home'))

@main.route("/home")
@login_required
def home():
    return render_template('home.html', title='Home')

@main.route("/coupons")
@login_required
def coupons():
    return render_template('coupons.html', title='Your Coupons')

@main.route("/coupons/creator")
@login_required
def coupon_creator():
    return render_template('coupon_creator.html', title='Coupons')

@main.route("/spinner")
@login_required
def spinner():
    hidden_slides = session.get('hidden_slides', [])
    return render_template('spinner.html', title='Spinner', hidden_slides=hidden_slides)

@main.route("/calendar")
@login_required
def calendar():
    return render_template('calendar.html', title='Calendar')

@main.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    nylas_email = None
    if current_user.nylas_grant_id:
        nylas = current_app.nylas_client
        try:
            account_info = nylas.grants.find(current_user.nylas_grant_id)
            nylas_email = account_info.data.email
        except Exception as e:
            logging.error(f"Error fetching Nylas account info: {e}")

    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.current_password.data):
            hashed_password = generate_password_hash(form.new_password.data)
            current_user.password = hashed_password
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('main.account_details'))
        else:
            flash('Current password is incorrect.', 'danger')

    return render_template('account.html', title='Account', user=current_user, nylas_email=nylas_email, form=form)

@main.route("/bemine")
def bemine():
    return render_template('bemine.html')

@main.route("/flower_images")
def flower_images():
    flower_folder = os.path.join(current_app.static_folder, 'images/Pixel Art Flower Pack')
    flower_images = []
    for root, dirs, files in os.walk(flower_folder):
        for file in files:
            if file.endswith(('png', 'jpg', 'jpeg', 'gif')):
                flower_images.append(os.path.join(root, file).replace(current_app.static_folder, ''))
    return jsonify(flower_images)
