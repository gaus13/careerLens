from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime


# ── Auth validation ke liye──────────────────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    name:     str
    email:    EmailStr   # pydantic validates if it's a real email format
    password: str

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = 'bearer'   # default value — always 'bearer' for JWT

class UserResponse(BaseModel):
    id:    int
    name:  str
    email: str

    class Config:
        from_attributes = True  # allows creating this from a SQLAlchemy object (magic line: learn more of it)


# ── Session ───────────────────────────────────────────────────────────────────

class SessionResponse(BaseModel):
    id:          int
    target_role: Optional[str]
    status:      str
    created_at:  datetime

    class Config:
        from_attributes = True


# ── Resume ────────────────────────────────────────────────────────────────────

class ResumeUploadResponse(BaseModel):
    session_id:  int
    text_length: int
    message:     str


# ── Career ────────────────────────────────────────────────────────────────────

class CareerSelectRequest(BaseModel):
    session_id:  int
    target_role: str   # the role the user clicked on


# ── Quiz ──────────────────────────────────────────────────────────────────────

class QuizSubmitRequest(BaseModel):
    answers: dict   # {"1": "A", "2": "C", ...}  question_id → chosen option


# ── Interview ─────────────────────────────────────────────────────────────────

class EvaluateRequest(BaseModel):
    question:   str
    answer:     str
    session_id: int