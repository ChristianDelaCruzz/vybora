"""Check all users in the database."""
import sqlite3
from config.settings import DATABASE_PATH

def check_users():
    print(f"📁 Database: {DATABASE_PATH}\n")
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, username, email, role, created_at FROM users")
    users = cursor.fetchall()
    
    if not users:
        print("❌ No users found.")
    else:
        print(f"✅ Found {len(users)} user(s):\n")
        for u in users:
            print(f"ID: {u[0]}")
            print(f"  Username: {u[1]}")
            print(f"  Email:    {u[2]}")
            print(f"  Role:     {u[3]}")
            print(f"  Joined:   {u[4]}")
            print("-" * 30)
    
    conn.close()

if __name__ == "__main__":
    check_users()