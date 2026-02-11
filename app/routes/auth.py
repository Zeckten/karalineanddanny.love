import os
from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import RegistrationForm, LoginForm
from app.models import User, db

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        access_code = form.access_code.data
        if access_code == os.getenv('ACCESS_CODE'):
            admin = False
        elif access_code == os.getenv('SUPER_ACCESS_CODE'):
            admin = True
        else:
            flash('Invalid access code', 'danger')
            return render_template('register.html', title='Register', form=form)
        
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, admin=admin)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect to bemine if not accepted, otherwise home
        if not current_user.be_my_valentine_accepted:
            return redirect(url_for('main.bemine'))
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter((User.email == form.login.data) | (User.username == form.login.data)).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # Redirect to bemine if not accepted, otherwise home
            if not user.be_my_valentine_accepted:
                return redirect(url_for('main.bemine'))
            return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check username/email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))
