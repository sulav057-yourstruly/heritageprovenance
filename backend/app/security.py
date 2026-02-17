"""
Password hashing utilities.
"""
import base64
import bcrypt

# We store hashes as: b64(salt)$b64(hash)
# This avoids passlib/bcrypt backend compatibility issues on some Windows/Python combos.

def hash_password(password: str) -> str:
    """Hash a password."""
    if not isinstance(password, str):
        raise TypeError("password must be a str")
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return f"{base64.b64encode(salt).decode('ascii')}${base64.b64encode(hashed).decode('ascii')}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    try:
        if not isinstance(plain_password, str) or not isinstance(hashed_password, str):
            return False
        parts = hashed_password.split("$", 1)
        if len(parts) != 2:
            return False
        _salt_b64, hash_b64 = parts
        expected = base64.b64decode(hash_b64.encode("ascii"))
        return bcrypt.checkpw(plain_password.encode("utf-8"), expected)
    except Exception:
        return False
