"""
Lightweight password hashing utility.

Uses passlib when available; falls back to a PBKDF2-HMAC-SHA256 implementation
so the module works even if passlib is not installed.
"""
import os
import hashlib
import hmac
from importlib import import_module

try:
    CryptContext = import_module("passlib.context").CryptContext

    _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(password: str) -> str:
        return _pwd_context.hash(password)

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return _pwd_context.verify(plain_password, hashed_password)

except ImportError:
    # Fallback: PBKDF2-HMAC-SHA256
    _ITERATIONS = 200000
    _SALT_SIZE = 16

    def _pbkdf2_hash(password: str, salt: bytes, iterations: int) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)

    def hash_password(password: str) -> str:
        salt = os.urandom(_SALT_SIZE)
        dk = _pbkdf2_hash(password, salt, _ITERATIONS)
        # store as hex: iterations$salt_hex$dk_hex
        return f"{_ITERATIONS}${salt.hex()}${dk.hex()}"

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            parts = hashed_password.split("$")
            iterations = int(parts[0])
            salt = bytes.fromhex(parts[1])
            dk_stored = bytes.fromhex(parts[2])
        except Exception:
            return False
        dk_new = _pbkdf2_hash(plain_password, salt, iterations)
        return hmac.compare_digest(dk_new, dk_stored)