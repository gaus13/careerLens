from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from services.ai_service import get_gap_analysis
import models

router = APIRouter(prefix='/gaps', tags=['Gap Analysis'])


@router.post('/analyse/{session_id}')
def analyse_gaps(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    session = db.query(models.Session).filter_by(id=session_id).first()
    if not session or not session.target_role:
        raise HTTPException(400, 'Select a target career role first.')

    resume = db.query(models.ResumeData).filter_by(session_id=session_id).first()
    if not resume:
        raise HTTPException(404, 'No resume found for this session.')

    result = get_gap_analysis(resume.raw_text, session.target_role)

    gap = models.GapAnalysis(
        session_id=session_id,
        gaps=result,
        roadmap=result.get('roadmap', [])
    )
    db.add(gap)
    db.commit()
    return result