from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from services.pdf_parser import extract_text_from_pdf
import models
import schemas

router = APIRouter(prefix='/resume', tags=['Resume'])


@router.post('/upload', response_model=schemas.ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Accepts a PDF resume upload.
    Creates a new session, extracts text, stores it.
    Returns the session_id — frontend stores this and sends it with every request.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, 'Only PDF files are accepted')

    file_bytes = await file.read()   # async read — doesn't block the server

    if len(file_bytes) > 5 * 1024 * 1024:   # 5MB limit
        raise HTTPException(400, 'File too large — max 5MB')

    raw_text = extract_text_from_pdf(file_bytes)

    if not raw_text.strip():
        raise HTTPException(400, 'Could not extract text. Is this a scanned PDF?')

    # Every resume upload starts a fresh session
    session = models.Session(user_id=current_user.id)
    db.add(session)
    db.commit()
    db.refresh(session)

    # Store the extracted text
    resume_data = models.ResumeData(
        session_id=session.id,
        raw_text=raw_text
    )
    db.add(resume_data)
    db.commit()

    return {
        'session_id': session.id,
        'text_length': len(raw_text),
        'message': f'Resume uploaded successfully. {len(raw_text)} characters extracted.'
    }


@router.get('/sessions', response_model=list[schemas.SessionResponse])
def get_my_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns all sessions for the logged-in user.
    This powers the Dashboard — history of all past career journeys.
    """
    sessions = db.query(models.Session).filter(
        models.Session.user_id == current_user.id
    ).order_by(models.Session.created_at.desc()).all()
    return sessions