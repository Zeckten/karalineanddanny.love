# karalineanddanny.love

A personalized Flask web application for a couple featuring interactive relationship tools including coupons, date idea spinner, shared calendar, and special occasion pages.

## Project Overview

This is a full-stack web application built with Flask that provides:
- User authentication system with login/registration
- Coupon creation and redemption system
- Date idea spinner with customizable slides
- Shared calendar integration (via Nylas)
- Special occasion pages (e.g., Valentine's bemine page)
- Admin panel for managing users, coupons, and date ideas

## Tech Stack

- **Backend**: Flask 3.1.0 (Python)
- **Database**: PostgreSQL with SQLAlchemy 2.0.36
- **Authentication**: Flask-Login 0.6.3
- **Forms**: Flask-WTF 1.2.2, WTForms 3.2.1
- **Email Integration**: Nylas 6.4.0
- **Database Migrations**: Flask-Migrate with Alembic 1.14.0
- **Deployment**: Waitress 3.0.2 (WSGI server)

## Project Structure

```
.
├── app/
│   ├── __init__.py           # App factory and initialization
│   ├── models.py             # Database models (User, Coupon, DateIdea)
│   ├── forms.py              # WTForms form definitions
│   ├── config.py             # Configuration settings
│   ├── load_data.py          # Data loading utilities
│   ├── clear_tables.py       # Database migration utilities
│   ├── routes/
│   │   ├── main.py          # Main routes (home, coupons, spinner, calendar)
│   │   ├── auth.py          # Authentication routes
│   │   ├── admin.py         # Admin panel routes
│   │   └── api.py           # API endpoints
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # Static assets (CSS, JS, images, JSON data)
├── run.py                   # Development server entry point
├── wsgi.py                  # Production WSGI entry point
└── requirements.txt         # Python dependencies
```

## Database Models

### User
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password`: Hashed password
- `nylas_grant_id`: Nylas integration grant ID
- `admin`: Boolean flag for admin privileges

### Coupon
- `id`: Primary key
- `title`: Coupon title
- `description`: Coupon description
- `image`: Image filename/path
- `redeemed`: Boolean redemption status
- `creator`: Username of creator

### DateIdea
- `id`: Primary key
- `title`: Unique date idea title
- `description`: Date idea description
- `image`: Image filename/path
- `location`: Location information
- `creator`: Username of creator

## Key Features

### Authentication
- User registration and login system
- Password change functionality
- Login required for all main features
- Session management with Flask-Login

### Coupons System
- Create custom coupons with title, description, and image
- Redeem/unredeeem coupons
- View all coupons with redemption status
- Admin controls for editing/deleting coupons

### Date Idea Spinner
- Interactive spinner for choosing date ideas
- Session-based hidden slides tracking
- Custom date ideas with images and locations

### Calendar Integration
- Nylas email integration
- Calendar view for shared events
- Account connection management

### Admin Panel
- User management (view, edit, delete users)
- Coupon management (view, edit, delete coupons)
- Date idea management (view, edit, delete ideas)
- Admin-only access control

## Running the Application

### Development
```bash
python run.py
```
Runs on debug mode with auto-reload.

### Production
Uses Waitress WSGI server (configured in wsgi.py/wsgi2.py).

## Configuration

Configuration is managed in `app/config.py` and requires:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask secret key for sessions
- `NYLAS_API_KEY`: Nylas API key
- `NYLAS_API_URI`: Nylas API endpoint
- Environment variables loaded via python-dotenv

## Routes Overview

### Main Routes (`/`)
- `/` - Redirects to home (login required)
- `/home` - Home page
- `/coupons` - View coupons
- `/coupons/creator` - Create new coupons
- `/spinner` - Date idea spinner
- `/calendar` - Shared calendar
- `/account` - User account settings
- `/bemine` - Special Valentine's page
- `/flower_images` - API endpoint for flower images

### Auth Routes
- `/login` - User login
- `/register` - User registration
- `/logout` - User logout

### Admin Routes
- Admin panel for managing all data

### API Routes
- RESTful endpoints for coupons and date ideas

## Development Notes

- Database tables are auto-created on app initialization
- Commented out auto-migration: `auto_migrate_database()` in `__init__.py`
- Commented out data loading: `load(db)` in `__init__.py`
- Static data stored in `app/static/` (coupons.json, dates.json)
- Custom domain configured in CNAME file

## Deployment

- Configured for Heroku (Procfile present)
- Uses PostgreSQL in production
- Static files served via Flask
- Favicon included in root directory
