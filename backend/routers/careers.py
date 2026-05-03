from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from services.ai_service import get_career_recommendations
import models

router = APIRouter(prefix='/careers', tags=['Careers'])


@router.post('/recommend/{session_id}')
def recommend_careers(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    resume = db.query(models.ResumeData).filter(
        models.ResumeData.session_id == session_id
    ).first()
    if not resume:
        raise HTTPException(404, 'No resume found. Upload your resume first.')

    result = get_career_recommendations(resume.raw_text)

    rec = models.CareerRecommendation(session_id=session_id, recommendations=result)
    db.add(rec)
    db.commit()
    return result


@router.post('/select/{session_id}')
def select_career(
    session_id: int,
    body: dict,   # {"target_role": "Backend Developer"}
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """User clicked a career card — save their choice to the session."""
    session = db.query(models.Session).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(404, 'Session not found')

    session.target_role = body.get('target_role')
    db.commit()
    return {'message': f"Target role set to: {session.target_role}"}