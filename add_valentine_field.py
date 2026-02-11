"""
Script to add be_my_valentine_accepted field to User table
Run this on Heroku with: heroku run python add_valentine_field.py
"""
from app import create_app
from app.models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Adding be_my_valentine_accepted field to User table...")

    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE \"user\" ADD COLUMN be_my_valentine_accepted BOOLEAN DEFAULT FALSE;"))
            conn.commit()
        print("✓ Added 'be_my_valentine_accepted' column to 'user' table")
    except Exception as e:
        if "already exists" in str(e) or "duplicate column" in str(e).lower():
            print("✓ 'be_my_valentine_accepted' column already exists in 'user' table")
        else:
            print(f"✗ Error adding be_my_valentine_accepted to user: {e}")

    print("\nDatabase migration complete!")
    print("Your Valentine's Day feature is ready! 💕")
