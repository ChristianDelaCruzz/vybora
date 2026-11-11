"""Terminal script to securely provision the first Admin account."""
import sys
from database.initialization import initialize_database
from database.user_repository import create_user, UserExistsError, has_any_admin

def main():
    # 1. Ensure the database and tables exist
    initialize_database()

    # 2. Check if an admin already exists (prevent duplicate creation)
    if has_any_admin():
        print("\n⚠️  An Admin account already exists in the database.")
        print("If you need to reset it, you must delete data/vybora.db manually.")
        sys.exit(0)

    print("\n========================================")
    print("   VyBora - Secure Admin Provisioning   ")
    print("========================================")

    username = input("Enter Admin Username: ").strip()
    email = input("Enter Admin Email: ").strip()

    if not username or not email:
        print("[ERROR] Username and Email cannot be empty.")
        sys.exit(1)

    # 3. Use standard input so PyCharm Terminal registers the typing
    print("\n(Note: The password will be visible while typing in this terminal)")
    password = input("Enter Admin Password: ").strip()
    confirm = input("Confirm Admin Password: ").strip()

    if password != confirm:
        print("[ERROR] Passwords do not match.")
        sys.exit(1)

    if len(password) < 8:
        print("[ERROR] Password must be at least 8 characters.")
        sys.exit(1)

    # 4. Create the admin in the database
    try:
        # We force the role to "Admin" here
        create_user(username, email, password, role="Admin")
        print(f"\n[SUCCESS] Admin account '{username}' created securely.")
        print("You can now log in through the VyBora application.")
    except UserExistsError as e:
        print(f"\n[ERROR] {e}")
    except Exception as e:
        print(f"\n[DATABASE ERROR] {e}")

if __name__ == "__main__":
    main()