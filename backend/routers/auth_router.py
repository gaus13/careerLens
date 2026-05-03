from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix='/auth', tags=['Authentication'])


@router.post('/signup', response_model=schemas.TokenResponse, status_code=201)
def signup(body: schemas.SignupRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.
    Returns a JWT token immediately so the user is logged in right away.
    """
    # Check email isn't already taken
    existing = db.query(models.User).filter(
        models.User.email == body.email
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail='An account with this email already exists'
        )

    # Create the user — notice we hash before storing, NEVER store plain text
    user = models.User(
        name=body.name,
        email=body.email,
        hashed_password=hash_password(body.password)
    )
    db.add(user)       # queue the INSERT
    db.commit()        # execute it — this is when the row actually appears in DB
    db.refresh(user)   # reload from DB so user.id is populated (it's auto-generated)

    return {
        'access_token': create_access_token(user.id),
        'token_type': 'bearer'
    }


@router.post('/login', response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Log in with email + password.
    Returns a fresh JWT token on success.
    """
    user = db.query(models.User).filter(
        models.User.email == body.email
    ).first()

    # Deliberately vague error — don't tell attackers which part was wrong
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail='Incorrect email or password'
        )

    return {
        'access_token': create_access_token(user.id),
        'token_type': 'bearer'
    }


@router.get('/me', response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(get_current_user)):
    """
    Protected route — returns the logged-in user's profile.
    The get_current_user dependency handles token verification.
    If no valid token is sent, FastAPI returns 401 automatically.
    """
    return current_user