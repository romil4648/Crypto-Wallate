import os
from cryptography.fernet import Fernet

# Get Fernet object using the key from environment variable

def get_fernet():
    key = os.environ['WALLET_ENCRYPTION_KEY'].encode()
    return Fernet(key)

def encrypt_private_key(private_key: str) -> str:
    f = get_fernet()
    return f.encrypt(private_key.encode()).decode()

def decrypt_private_key(token: str) -> str:
    f = get_fernet()
    return f.decrypt(token.encode()).decode()
