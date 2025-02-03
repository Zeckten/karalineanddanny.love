from flask import Blueprint, redirect, url_for, session, request, current_app, jsonify, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.models import db, Coupon, DateIdea, User
import logging

api = Blueprint('api', __name__, url_prefix='/api')

@api.route("/nylas/auth", methods=["GET"])
@login_required
def nylas_auth():
    session['next'] = request.referrer or url_for('main.home')
    nylas = current_app.nylas_client
    auth_url = nylas.auth.url_for_oauth2({
        "client_id": current_app.config["NYLAS_CLIENT_ID"],
        "redirect_uri": current_app.config["NYLAS_CALLBACK_URI"],
        "access_type": "offline"
    })
    return redirect(auth_url)

@api.route("/oauth", methods=["GET"])
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

    next_url = session.pop('next', url_for('main.home'))
    return redirect(url_for('main.home'))

@api.route("/calendars", methods=["GET"])
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

@api.route('/add-to-calendar', methods=['POST'])
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

@api.route("/coupons", methods=["GET"])
@login_required
def get_coupons():
    coupons = Coupon.query.all()
    return jsonify([coupon.to_dict() for coupon in coupons])

@api.route("/coupons/<int:id>/redeem", methods=["POST"])
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

@api.route("/dates", methods=["GET"])
@login_required
def get_date_ideas():
    date_ideas = DateIdea.query.all()
    logging.info(f"Fetched {len(date_ideas)} date ideas")
    return jsonify([date_idea.to_dict() for date_idea in date_ideas])

@api.route('/add/date-idea', methods=['GET', 'POST'])
@login_required
def add_date_idea():
    if request.method == "POST":
        title = request.json['title']
        description = request.json['description']
        image = request.json['image']
        location = request.json['location']
        creator = current_user.username  # Set creator
        new_date_idea = DateIdea(title=title, description=description, image=image, location=location, creator=creator)
        try:
            db.session.add(new_date_idea)
            db.session.commit()
            flash('Date idea added successfully', 'success')
        except Exception as e:
            logging.error(f"Error adding date idea: {e}")
            flash('Error adding date idea', 'danger')
    return redirect(request.referrer or url_for('main.home'))

@api.route('/add/coupon', methods=['GET', 'POST'])
@login_required
def add_coupon():
    if request.method == "POST":
        title = request.json['title']
        description = request.json['description']
        image = request.json['image']
        creator = current_user.username  # Set creator
        new_coupon = Coupon(title=title, description=description, image=image, creator=creator)
        try:
            db.session.add(new_coupon)
            db.session.commit()
            flash('Coupon added successfully', 'success')
        except Exception as e:
            logging.error(f"Error adding coupon: {e}")
            flash('Error adding coupon', 'danger')
    return redirect(request.referrer or url_for('main.home'))

@api.route('/add/user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == "POST":
        username = request.json['username']
        email = request.json['email']
        password = request.json['password']
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('User added successfully', 'success')
        except Exception as e:
            logging.error(f"Error adding user: {e}")
            flash('Error adding user', 'danger')
    return redirect(request.referrer or url_for('main.home'))

@api.route('/toggle_hide_slide/<string:title>', methods=['POST'])
@login_required
def toggle_hide_slide(title):
    hidden_slides = session.get('hidden_slides', [])
    hidden = request.json.get('hidden', False)
    if hidden:
        if title not in hidden_slides:
            hidden_slides.append(title)
    else:
        if title in hidden_slides:
            hidden_slides.remove(title)
    session['hidden_slides'] = hidden_slides
    return jsonify({'status': 'success', 'hidden_slides': hidden_slides})

@api.route('/clear_hidden_slides', methods=['POST'])
@login_required
def clear_hidden_slides():
    session['hidden_slides'] = []
    return jsonify({'status': 'success', 'hidden_slides': []})
