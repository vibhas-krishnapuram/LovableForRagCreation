from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
import os
from fastapi import HTTPException, Depends
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not SECRET_KEY:
    raise Exception("SECRET_KEY is missing from environment variables - hgljg")

oauth2_scheme = HTTPBearer(description="Paste your JWT token ")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    # Use timezone-aware datetime
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded.get("user_id")
    except jwt.ExpiredSignatureError:
        print("Token has expired")  # Debug logging
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")  # Debug logging
        return None


def get_current_user_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    # Extract the token string from the credentials object
    token_string = credentials.credentials
    user_id = verify_token(token_string)
    if not user_id:
        # This exception detail is critical for debugging
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired token. Check server logs for details."
        )
    return user_id



# ENCRYPTION HELPER FUNCTIONS
def load_key():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    key_path = os.path.join(base_dir, "secret.key")
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"secret.key not found at: {key_path}")

    return open(key_path, "rb").read()

def encrypt_key(raw_key: str):
    key = load_key()
    f = Fernet(key)

    encoded_key = raw_key.encode()
    encrypted = f.encrypt(encoded_key)

    return encrypted

def decrypt_key(encrypted_key: str):
    key = load_key()
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_key).decode()
    return decrypted
