from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import models
from database import get_db

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM  = os.getenv('ALGORITHM', 'HS256')
EXPIRE_MIN = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30))

# CryptContext handles bcrypt hashing — it knows how to hash AND verify
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# This tells FastAPI: "to authenticate, the client sends a token to /auth/login"
# FastAPI uses this to show the lock icon on protected routes in Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Turn 'user pass' into '$2b$12$...' — a bcrypt hash"""
    return pwd_context.hash(plain[:72]) #error occured due to this line and this is the fixed version ["earlier: return pwd_context.hash(plain)"]

def verify_password(plain: str, hashed: str) -> bool:
    """Check if 'user input pass' matches the stored hash. Returns True or False."""
    return pwd_context.verify(plain, hashed)


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(user_id: int) -> str:
    """
    Create a signed JWT token.
    The token contains the user_id and an expiry time.
    It is signed with SECRET_KEY so only your server can verify it.
    """
    expire  = datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)
    payload = {'sub': str(user_id), 'exp': expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ── Route dependency ──────────────────────────────────────────────────────────

def get_current_user(
    token: str         = Depends(oauth2_scheme),
    db:    Session     = Depends(get_db)
) -> models.User:
    """
    This function is injected into any protected route.
    FastAPI calls it automatically before the route function runs.

    It:
    1. Extracts the JWT from the Authorization header
    2. Verifies the signature (was it signed by our SECRET_KEY?)
    3. Extracts the user_id from inside the token
    4. Fetches and returns the User from the database
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid or expired token',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get('sub')
        if user_id is None:
            raise credentials_error
    except JWTError:
        raise credentials_error

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user

"""complete flow:
# 1. request me token aata hai (Authorization header me)
# 2. us token ko decode karte hain SECRET_KEY se
# 3. usme se user_id nikaalte hain
# 4. DB me user find karte hain
# 5. user mil gaya → return
# 6. nahi mila → error"""