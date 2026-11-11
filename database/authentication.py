"""Secure password hashing using PBKDF2-HMAC-SHA256."""
import hashlib
import hmac
import os
import base64

# Configurable iteration count (600,000 is recommended for 2024+)
ITERATIONS = 600_000 

def generate_salt() -> str:
    """Generate a cryptographically secure 16-byte salt."""
    salt_bytes = os.urandom(16)
    return base64.b64encode(salt_bytes).decode('utf-8')

def hash_password(password: str, salt: str) -> str:
    """Derive a secure password hash using PBKDF2-HMAC-SHA256."""
    salt_bytes = base64.b64decode(salt)
    pwd_bytes = password.encode('utf-8')
    
    # Derive a 32-byte hash
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha256', 
        pwd_bytes, 
        salt_bytes, 
        ITERATIONS
    )
    return base64.b64encode(hash_bytes).decode('utf-8')

def verify_password(password: str, salt: str, stored_hash: str) -> bool:
    """Securely verify a password against the stored hash."""
    calculated_hash = hash_password(password, salt)
    # Use compare_digest to prevent timing attacks
    return hmac.compare_digest(calculated_hash, stored_hash)