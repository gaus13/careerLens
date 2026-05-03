from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from database import engine
from models import Base
from routers import auth_router, resume, careers, gaps, quiz, interview
from fastapi.security import HTTPBearer

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI(title='CareerLens', version='1.0.0',
               swagger_ui_parameters={"persistAuthorization": True})

security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
     allow_origins=[
        'http://localhost:3000',
        'https://careerlens-1-cz3s.onrender.com',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_router.router)
app.include_router(resume.router)
app.include_router(careers.router)
app.include_router(gaps.router)
app.include_router(quiz.router)
app.include_router(interview.router)

@app.get("/health")
def health_check():
    return {"status": "heartbeat ❤️ OK"}

@app.get("/")
def home():
    return {"message": "API is running"}