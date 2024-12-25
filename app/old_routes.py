import os
import logging
from functools import wraps
from flask import render_template, url_for, flash, redirect, current_app, session, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import RegistrationForm, LoginForm, ChangePasswordForm
from app.models import User, db, DateIdea, Coupon

# Configure logging
logging.basicConfig(level=logging.ERROR)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def register_routes(app):
    @app.route("/register", methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data)
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
        return render_template('login.html', title='Login', form=form)

    @app.route("/logout")
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route("/")
    @login_required
    def index():
        return redirect(url_for('home'))

    @app.route("/home")
    @login_required
    def home():
        return render_template('home.html', title='Home')

    @app.route("/coupons")
    @login_required
    def coupons():
        return render_template('coupons.html', title='Coupons')

    @app.route("/spinner")
    @login_required
    def spinner():
        return render_template('spinner.html', title='Spinner')

    @app.route("/calendar")
    @login_required
    def calendar():
        return render_template('calendar.html', title='Calendar')

    @app.route("/nylas/auth", methods=["GET"])
    @login_required
    def nylas_auth():
        session['next'] = request.referrer or url_for('home')
        nylas = current_app.nylas_client
        auth_url = nylas.auth.url_for_oauth2({
            "client_id": current_app.config["NYLAS_CLIENT_ID"],
            "redirect_uri": current_app.config["NYLAS_CALLBACK_URI"],
            "access_type": "offline"
        })
        return redirect(auth_url)
    
    @app.route("/oauth/exchange", methods=["GET"])
    @login_required
    def nylas_callback():
        nylas = current_app.nylas_client
        code = request.args.get('code')

        if not code:
            return "No authorization code returned from Nylas", 400

        exchange = nylas.auth.exchange_code_for_token(
            request = {
                'client_id': current_app.config["NYLAS_CLIENT_ID"],
                'code': code,
                'redirect_uri': current_app.config["NYLAS_CALLBACK_URI"],
            }
        )
        
        grant_id = exchange.grant_id
        current_user.nylas_grant_id = grant_id
        db.session.commit()

        next_url = session.pop('next', url_for('home'))
        return redirect(next_url)

    @app.route("/account", methods=['GET', 'POST'])
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
                return redirect(url_for('account'))
            else:
                flash('Current password is incorrect.', 'danger')

        return render_template('account.html', title='Account', user=current_user, nylas_email=nylas_email, form=form)

    @app.route("/api/calendars", methods=["GET"])
    @login_required
    def get_calendars_and_events():
        nylas = current_app.nylas_client
        grant_id = current_user.nylas_grant_id

        if not grant_id:
            return {"error": "No Nylas grant ID found for the user"}, 400

        try:
            calendars, request_id, next_cursor = nylas.calendars.list(grant_id)
            calendars_with_events = []
            
            for calendar in calendars:
                events, events_request_id, events_cursor = nylas.events.list(
                    grant_id,
                    query_params={
                        "calendar_id": calendar.id
                    }
                )
                
                calendar_data = {
                    "id": calendar.id,
                    "name": calendar.name,
                    "description": getattr(calendar, 'description', ''),
                    "location": getattr(calendar, 'location', ''),
                    "timezone": getattr(calendar, 'timezone', 'UTC'),
                    "is_primary": getattr(calendar, 'is_primary', False),
                    "events": []
                }
                
                for event in events:
                    event_data = {
                        "id": event.id,
                        "title": event.title,
                        "start_time": event.when.start_time if hasattr(event.when, 'start_time') else None,
                        "end_time": event.when.end_time if hasattr(event.when, 'end_time') else None,
                        "location": getattr(event, 'location', ''),
                        "description": getattr(event, 'description', ''),
                        "status": getattr(event, 'status', ''),
                        "busy": getattr(event, 'busy', True),
                        "participants": []
                    }
                    
                    if hasattr(event, 'participants') and event.participants:
                        event_data["participants"] = [
                            {
                                "email": getattr(p, 'email', ''),
                                "name": getattr(p, 'name', ''),
                                "status": getattr(p, 'status', '')
                            } for p in event.participants
                        ]
                    
                    calendar_data["events"].append(event_data)
                
                calendars_with_events.append(calendar_data)
            
            return {
                "calendars": calendars_with_events,
                "request_id": request_id
            }, 200

        except Exception as e:
            if hasattr(e, 'status_code'):
                if e.status_code == 429:
                    return {"error": "Rate limit exceeded. Please try again later."}, 429
                return {"error": str(e)}, e.status_code
            return {"error": str(e)}, 500

    @app.route('/add-to-calendar', methods=['POST'])
    @login_required
    def add_to_calendar():
        data = request.json
        title = data.get('title')
        description = data.get('description')
        location = data.get('location')
        start_time = data.get('startTime')
        end_time = data.get('endTime')
        calendar_id = data.get('calendarId')

        nylas = current_app.nylas_client
        grant_id = current_user.nylas_grant_id

        if not grant_id:
            return jsonify({'error': 'No Nylas grant ID found for the user'}), 400

        event_data = {
            "title": title,
            "description": description,
            "location": location,
            "when": {
                "start_time": start_time,
                "end_time": end_time
            }
        }

        query_params = {
            "calendar_id": calendar_id,
            "notify_participants": True
        }

        try:
            event = nylas.events.create(
                identifier=grant_id,
                request_body=event_data,
                query_params=query_params
            )
            logging.info(f"Event created: {event}")
            return jsonify({'message': 'Event added to calendar', 'event_id': event.data.id}), 200
        except Exception as e:
            logging.error(f"Error adding event to calendar: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/add/date_idea', methods=['GET', 'POST'])
    @login_required
    def add_date_idea():
        if request.method == "POST":
            title = request.form['title']
            description = request.form['description']
            image = request.form['image']
            location = request.form['location']
            new_date_idea = DateIdea(title=title, description=description, image=image, location=location)
            try:
                db.session.add(new_date_idea)
                db.session.commit()
                flash('Date idea added successfully', 'success')
            except Exception as e:
                logging.error(f"Error adding date idea: {e}")
                flash('Error adding date idea', 'danger')
        return redirect(request.referrer or url_for('date_ideas'))

    @app.route('/add/coupon', methods=['GET', 'POST'])
    @login_required
    def add_coupon():
        if request.method == "POST":
            title = request.form['title']
            description = request.form['description']
            image = request.form['image']
            new_coupon = Coupon(title=title, description=description, image=image)
            try:
                db.session.add(new_coupon)
                db.session.commit()
                flash('Coupon added successfully', 'success')
            except Exception as e:
                logging.error(f"Error adding coupon: {e}")
                flash('Error adding coupon', 'danger')
        return redirect(request.referrer or url_for('coupons'))

    @app.route('/add/user', methods=['GET', 'POST'])
    @login_required
    def add_user():
        if request.method == "POST":
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password=hashed_password)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('User added successfully', 'success')
            except Exception as e:
                logging.error(f"Error adding user: {e}")
                flash('Error adding user', 'danger')
        return redirect(request.referrer or url_for('home'))

    @app.route("/api/coupons", methods=["GET"])
    @login_required
    def get_coupons():
        coupons = Coupon.query.all()
        return jsonify([coupon.to_dict() for coupon in coupons])

    @app.route("/api/coupons/<int:id>/redeem", methods=["POST"])
    @login_required
    def redeem_coupon(id):
        coupon = Coupon.query.get_or_404(id)
        if coupon.redeemed:
            return jsonify({'message': 'Coupon already redeemed'}), 400

        coupon.redeemed = True
        db.session.commit()

        # Send email to all users using Nylas
        users = User.query.all()
        nylas = current_app.nylas_client
        for user in users:
            try:
                email_data = {
                    "to": [{"email": user.email}],
                    "subject": "Coupon Redeemed",
                    "body": f'"{current_user.username}" has redeemed the coupon: "{coupon.title}".'
                }
                draft = nylas.drafts.create()
                draft.update(email_data)
                draft.send()
            except Exception as e:
                logging.error(f"Error sending email to {user.email}: {e}")

        return jsonify({'message': 'Coupon redeemed successfully'})

    @app.route("/admin")
    @login_required
    @admin_required
    def admin_panel():
        users = User.query.all()
        coupons = Coupon.query.all()
        date_ideas = DateIdea.query.all()
        return render_template('admin.html', users=users, coupons=coupons, date_ideas=date_ideas)

    @app.route('/admin/edit/user', methods=['GET', 'POST'])
    @app.route('/admin/edit/user/<int:id>', methods=['GET', 'POST'])
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
            return redirect(url_for('admin_panel'))
        return render_template('edit_user.html', user=user)

    @app.route('/admin/edit/coupon', methods=['GET', 'POST'])
    @app.route('/admin/edit/coupon/<int:id>', methods=['GET', 'POST'])
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
            return redirect(url_for('admin_panel'))
        return render_template('edit_coupon.html', coupon=coupon)

    @app.route('/admin/edit/date_idea', methods=['GET', 'POST'])
    @app.route('/admin/edit/date_idea/<int:id>', methods=['GET', 'POST'])
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
            return redirect(url_for('admin_panel'))
        return render_template('edit_date_idea.html', date_idea=date_idea)

    @app.route("/api/dates", methods=["GET"])
    @login_required
    def get_date_ideas():
        date_ideas = DateIdea.query.all()
        return jsonify([date_idea.to_dict() for date_idea in date_ideas])

