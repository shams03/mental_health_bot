from database import db

def init_db():
    # Create test user
    user_id = db.create_user(
        email='test@example.com',
        password='test123',
        name='Test User',
        is_premium=False
    )
    
    if user_id:
        print("Test user created successfully!")
    else:
        print("Test user already exists!")

if __name__ == '__main__':
    init_db() 