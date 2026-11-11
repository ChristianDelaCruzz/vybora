"""Reset the Chan user account."""
import sqlite3
import hashlib
import os
from config.settings import DATABASE_PATH

def reset_user():
    # Connect to DB
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    # Delete existing Chan (to clear the broken hash)
    cursor.execute("DELETE FROM users WHERE username = 'Chan'")
    conn.commit()

    # Create new correct hash
    username = "Chan"
    email = "chan@vybora.com"
    password = "hello123"
    role = "User" # CHANGED TO USER

    salt = os.urandom(16).hex()
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        bytes.fromhex(salt), 
        100000
    ).hex()

    # Insert the new user
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, salt, role) VALUES (?, ?, ?, ?, ?)",
        (username, email, pwd_hash, salt, role)
    )
    conn.commit()
    conn.close()
    
    print("✅ Chan account reset successfully!")
    print(f"Username: {username}")
    print(f"Password: {password}")
    print(f"Role: {role}")

if __name__ == "__main__":
    reset_user()