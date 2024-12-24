import os
import logging
from flask import render_template, url_for, flash, redirect, current_app, session, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import RegistrationForm, LoginForm
from app.models import User, db, DateIdea

# Configure logging
logging.basicConfig(level=logging.ERROR)

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

        return redirect(url_for('home'))

    @app.route("/account")
    @login_required
    def account():
        return render_template('account.html', title='Account', user=current_user)

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

    @app.route('/add-date-idea', methods=['POST'])
    @login_required
    def add_date_idea():
        data = request.json
        title = data.get('title')
        description = data.get('description')
        image = data.get('image')
        location = data.get('location')

        new_date_idea = DateIdea(
            title=title,
            description=description,
            image=image,
            location=location
        )

        try:
            db.session.add(new_date_idea)
            db.session.commit()
            return jsonify({'message': 'Date idea added successfully'}), 200
        except Exception as e:
            logging.error(f"Error adding date idea: {e}")
            return jsonify({'error': str(e)}), 500

