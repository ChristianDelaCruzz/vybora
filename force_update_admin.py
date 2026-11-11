"""Force-reset the admin account's password and role."""
import sqlite3
import hashlib
import os
from config.settings import DATABASE_PATH

def force_update():
    print(f"📁 Database: {DATABASE_PATH}")
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()
    
    # 1. Find the admin user
    cursor.execute("SELECT user_id FROM users WHERE username = 'admin'")
    row = cursor.fetchone()
    
    if not row:
        print("❌ No 'admin' user found. You need to create it via Register.")
        conn.close()
        return
        
    user_id = row[0]
    
    # 2. Generate a brand new password hash for 'admin123'
    new_pwd = "admin123"
    salt = os.urandom(16).hex()
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        new_pwd.encode('utf-8'), 
        bytes.fromhex(salt), 
        100000
    ).hex()
    
    # 3. Force update the existing row
    try:
        cursor.execute(
            "UPDATE users SET password_hash = ?, salt = ?, role = 'Admin' WHERE user_id = ?",
            (pwd_hash, salt, user_id)
        )
        conn.commit()
        print("✅ Admin account updated successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Role:     Admin")
    except Exception as e:
        print(f"❌ Failed to update: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    force_update()