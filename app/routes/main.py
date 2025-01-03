from flask import Blueprint, render_template, redirect, url_for, flash, current_app, session
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.forms import ChangePasswordForm
from app.models import User, DateIdea, Coupon, db
import logging

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
    return render_template('coupons.html', title='Coupons')

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
