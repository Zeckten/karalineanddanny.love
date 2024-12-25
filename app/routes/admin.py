from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import User, DateIdea, Coupon, db
from functools import wraps

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route("/")
@login_required
@admin_required
def admin_panel():
    users = User.query.all()
    coupons = Coupon.query.all()
    date_ideas = DateIdea.query.all()
    return render_template('admin.html', users=users, coupons=coupons, date_ideas=date_ideas)

@admin.route('/edit/user', methods=['GET', 'POST'])
@admin.route('/edit/user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id=None):
    user = User.query.get(id) if id else None
    if request.method == "POST":
        if user:
            user.username = request.form['username']
            user.email = request.form['email']
            if request.form['password']:
                user.password = generate_password_hash(request.form['password'])
            user.admin = 'admin' in request.form
        else:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            hashed_password = generate_password_hash(password)
            admin = 'admin' in request.form
            user = User(username=username, email=email, password=hashed_password, admin=admin)
            db.session.add(user)
        db.session.commit()
        flash('User saved successfully', 'success')
        return redirect(url_for('admin.admin_panel'))
    return render_template('edit_user.html', user=user)

@admin.route('/edit/coupon', methods=['GET', 'POST'])
@admin.route('/edit/coupon/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_coupon(id=None):
    coupon = Coupon.query.get(id) if id else None
    if request.method == "POST":
        if coupon:
            coupon.title = request.form['title']
            coupon.description = request.form['description']
            coupon.image = request.form['image']
            coupon.redeemed = 'redeemed' in request.form
        else:
            title = request.form['title']
            description = request.form['description']
            image = request.form['image']
            coupon = Coupon(title=title, description=description, image=image)
            db.session.add(coupon)
        db.session.commit()
        flash('Coupon saved successfully', 'success')
        return redirect(url_for('admin.admin_panel'))
    return render_template('edit_coupon.html', coupon=coupon)

@admin.route('/edit/date_idea', methods=['GET', 'POST'])
@admin.route('/edit/date_idea/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_date_idea(id=None):
    date_idea = DateIdea.query.get(id) if id else None
    if request.method == "POST":
        if date_idea:
            date_idea.title = request.form['title']
            date_idea.description = request.form['description']
            date_idea.image = request.form['image']
            date_idea.location = request.form['location']
        else:
            title = request.form['title']
            description = request.form['description']
            image = request.form['image']
            location = request.form['location']
            date_idea = DateIdea(title=title, description=description, image=image, location=location)
            db.session.add(date_idea)
        db.session.commit()
        flash('Date idea saved successfully', 'success')
        return redirect(url_for('admin.admin_panel'))
    return render_template('edit_date_idea.html', date_idea=date_idea)

@admin.route('/download/users')
@login_required
@admin_required
def download_users():
    users = User.query.all()
    users_data = [{"id": user.id, "username": user.username, "email": user.email, "admin": user.admin, "grant-id": user.nylas_grant_id} for user in users]
    return jsonify(users_data)

@admin.route('/download/coupons')
@login_required
@admin_required
def download_coupons():
    coupons = Coupon.query.all()
    coupons_data = [{"title": coupon.title, "description": coupon.description, "image": coupon.image, "redeemed": coupon.redeemed} for coupon in coupons]
    return jsonify(coupons_data)

@admin.route('/download/date_ideas')
@login_required
@admin_required
def download_date_ideas():
    date_ideas = DateIdea.query.all()
    date_ideas_data = [{"title": date_idea.title, "description": date_idea.description, "image": date_idea.image, "location": date_idea.location} for date_idea in date_ideas]
    return jsonify(date_ideas_data)
