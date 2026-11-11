"""Delete the admin account from the database."""
import sqlite3
from config.settings import DATABASE_PATH

def delete_admin():
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM users WHERE username = 'admin'")
    deleted = cursor.rowcount
    
    cursor.execute("DELETE FROM user_settings WHERE user_id NOT IN (SELECT user_id FROM users)")
    cursor.execute("DELETE FROM media_history WHERE user_id NOT IN (SELECT user_id FROM users)")
    cursor.execute("DELETE FROM media_favorites WHERE user_id NOT IN (SELECT user_id FROM users)")
    
    conn.commit()
    conn.close()
    
    if deleted > 0:
        print(f"✅ Admin deleted successfully. ({deleted} row removed)")
    else:
        print("❌ No admin account was found.")

if __name__ == "__main__":
    delete_admin()