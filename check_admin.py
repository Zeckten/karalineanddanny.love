"""
Script to check and set admin status for users
"""
from app import create_app
from app.models import User, db

app = create_app()

with app.app_context():
    # List all users
    users = User.query.all()
    print("\n=== Current Users ===")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Admin: {user.admin}")

    print("\n=== Setting Admin Status ===")
    # Get username input
    username = input("\nEnter username to make admin (or press Enter to skip): ").strip()

    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            user.admin = True
            db.session.commit()
            print(f"✓ {username} is now an admin!")
        else:
            print(f"✗ User '{username}' not found.")
    else:
        print("Skipped setting admin status.")

    # Show final state
    print("\n=== Final User State ===")
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Admin: {user.admin}")
