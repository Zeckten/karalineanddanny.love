"""
Diagnostic script to test admin panel functionality
Run this to see what's causing the 500 error
"""
import os
import sys

print("=== Environment Check ===")
env_vars = ['SECRET_KEY', 'SQLALCHEMY_DATABASE_URI', 'NYLAS_API_KEY', 'NYLAS_API_URI', 'NYLAS_CLIENT_ID', 'NYLAS_CALLBACK_URI']
for var in env_vars:
    value = os.getenv(var)
    if value:
        # Mask sensitive data
        if len(value) > 10:
            masked = value[:4] + '...' + value[-4:]
        else:
            masked = '***'
        print(f"✓ {var}: {masked}")
    else:
        print(f"✗ {var}: NOT SET")

print("\n=== Testing App Creation ===")
try:
    from app import create_app
    app = create_app()
    print("✓ App created successfully")
except Exception as e:
    print(f"✗ Error creating app: {e}")
    sys.exit(1)

print("\n=== Testing Database Connection ===")
try:
    from app.models import User, Coupon, DateIdea, db
    with app.app_context():
        # Test users query
        users = User.query.all()
        print(f"✓ Users table accessible: {len(users)} users found")
        for user in users:
            print(f"  - {user.username} (admin: {user.admin})")

        # Test coupons query
        coupons = Coupon.query.all()
        print(f"✓ Coupons table accessible: {len(coupons)} coupons found")

        # Test date ideas query
        date_ideas = DateIdea.query.all()
        print(f"✓ Date ideas table accessible: {len(date_ideas)} date ideas found")

except Exception as e:
    print(f"✗ Database error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n=== Testing Admin Route ===")
try:
    with app.test_client() as client:
        # Try to access admin panel (will redirect to login)
        response = client.get('/admin/')
        print(f"Admin route status code: {response.status_code}")
        if response.status_code == 302:
            print("✓ Admin route accessible (redirects to login as expected)")
        elif response.status_code == 500:
            print("✗ Admin route returns 500 error")
            print(f"Response: {response.data.decode('utf-8')[:500]}")
        else:
            print(f"? Unexpected status code: {response.status_code}")
except Exception as e:
    print(f"✗ Error testing admin route: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Domain Configuration ===")
print(f"CNAME file domain: lineydanny.us")
nylas_callback = os.getenv('NYLAS_CALLBACK_URI')
if nylas_callback:
    if 'karalineanddanny.love' in nylas_callback:
        print(f"⚠ WARNING: NYLAS_CALLBACK_URI still uses old domain: {nylas_callback}")
        print(f"  Update to: {nylas_callback.replace('karalineanddanny.love', 'lineydanny.us')}")
    elif 'lineydanny.us' in nylas_callback:
        print(f"✓ NYLAS_CALLBACK_URI uses new domain")
    else:
        print(f"? NYLAS_CALLBACK_URI: {nylas_callback}")

print("\n=== Summary ===")
print("If you see errors above, that's likely causing your 500 error.")
print("If everything passed, the issue might be in your production environment.")
