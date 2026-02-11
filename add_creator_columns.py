"""
Script to add the missing 'creator' columns to Heroku database
Run this on Heroku with: heroku run python add_creator_columns.py
"""
from app import create_app
from app.models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Checking database schema...")

    # Add creator column to coupon table if it doesn't exist
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE coupon ADD COLUMN creator VARCHAR(100);"))
            conn.commit()
        print("✓ Added 'creator' column to 'coupon' table")
    except Exception as e:
        if "already exists" in str(e) or "duplicate column" in str(e).lower():
            print("✓ 'creator' column already exists in 'coupon' table")
        else:
            print(f"✗ Error adding creator to coupon: {e}")

    # Add creator column to date_idea table if it doesn't exist
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE date_idea ADD COLUMN creator VARCHAR(100);"))
            conn.commit()
        print("✓ Added 'creator' column to 'date_idea' table")
    except Exception as e:
        if "already exists" in str(e) or "duplicate column" in str(e).lower():
            print("✓ 'creator' column already exists in 'date_idea' table")
        else:
            print(f"✗ Error adding creator to date_idea: {e}")

    print("\nDatabase migration complete!")
    print("Your admin panel should now work!")
