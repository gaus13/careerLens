from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from services.ai_service import evaluate_interview_answer, generate_final_report
import models

router = APIRouter(prefix='/interview', tags=['Interview'])


class EvaluateRequest(BaseModel):
    question:   str
    answer:     str
    session_id: int


@router.post('/evaluate')
def evaluate_answer(
    body: EvaluateRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    session = db.query(models.Session).filter_by(id=body.session_id).first()
    if not session:
        raise HTTPException(404, 'Session not found.')

    feedback = evaluate_interview_answer(body.question, body.answer, session.target_role)

    # Persist each question + answer + feedback to DB
    iq = models.InterviewQuestion(
        session_id=body.session_id,
        question=body.question,
        user_answer=body.answer,
        ai_feedback=feedback,
        score=feedback.get('score')
    )
    db.add(iq)
    db.commit()
    return feedback


@router.get('/report/{session_id}')
def get_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    session     = db.query(models.Session).filter_by(id=session_id).first()
    quiz        = db.query(models.QuizAttempt).filter_by(session_id=session_id).first()
    interviews  = db.query(models.InterviewQuestion).filter_by(session_id=session_id).all()

    quiz_score  = (quiz.score / 10 * 100) if quiz else 0
    interview_avg = (
        sum(i.score for i in interviews if i.score) / len(interviews)
        if interviews else 0
    )
    # Weighted: 40% quiz, 60% interview average (scaled to 100)
    readiness = round((quiz_score * 0.4) + ((interview_avg / 10 * 100) * 0.6))

    # Generate AI-powered strengths/improvements/next steps
    session_data = {
        'target_role':    session.target_role,
        'quiz_score':     quiz_score,
        'interview_avg':  interview_avg,
        'questions_count': len(interviews)
    }
    ai_report = generate_final_report(session_data)

    # Save the report
    report = models.FinalReport(
        session_id=session_id,
        readiness_score=readiness,
        strengths=ai_report.get('strengths', []),
        improvements=ai_report.get('improvements', []),
        next_steps=ai_report.get('next_steps', [])
    )
    db.add(report)
    session.status = 'completed'
    db.commit()

    return {
        'readiness_score': readiness,
        'quiz_score':      quiz_score,
        'interview_avg':   round(interview_avg, 1),
        'target_role':     session.target_role,
        'strengths':       ai_report.get('strengths', []),
        'improvements':    ai_report.get('improvements', []),
        'next_steps':      ai_report.get('next_steps', [])
    }