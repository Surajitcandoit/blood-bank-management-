from database import SessionLocal
from models import User

# Open a connection to your bloodbank.db
db = SessionLocal()

# Target the email of the user you just registered
TARGET_EMAIL = "admin@bloodbank.com"

# Find the user
user = db.query(User).filter(User.email == TARGET_EMAIL).first()

if user:
    print(f"Found user: {user.name} (Current Role: {user.role})")
    
    # Force the role change
    user.role = "admin"
    db.commit()
    
    print(f"Success! {user.email} is now an admin.")
else:
    print("User not found. Check the email address.")

db.close()