from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from services.ai_service import generate_quiz
import models

router = APIRouter(prefix='/quiz', tags=['Quiz'])


@router.post('/generate/{session_id}')
def generate_quiz_questions(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    gap = db.query(models.GapAnalysis).filter_by(session_id=session_id).first()
    session = db.query(models.Session).filter_by(id=session_id).first()

    if not gap:
        raise HTTPException(400, 'Complete gap analysis first.')

    questions_data = generate_quiz(gap.gaps, session.target_role)

    quiz = models.QuizAttempt(
        session_id=session_id,
        questions=questions_data['questions'],
        answers={},
        score=0
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    # Return questions WITHOUT correct answers — never expose answers to frontend
    safe_questions = [
        {'id': q['id'], 'question': q['question'], 'options': q['options']}
        for q in questions_data['questions']
    ]
    return {'quiz_id': quiz.id, 'questions': safe_questions}


@router.post('/submit/{quiz_id}')
def submit_quiz(
    quiz_id: int,
    body: dict,   # {"answers": {"1": "B", "2": "A", ...}}
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    quiz = db.query(models.QuizAttempt).filter_by(id=quiz_id).first()
    if not quiz:
        raise HTTPException(404, 'Quiz not found.')

    submitted = body.get('answers', {})

    # Score by comparing submitted answers against stored correct answers
    correct_count = sum(
        1 for q in quiz.questions
        if submitted.get(str(q['id'])) == q['correct']
    )

    quiz.answers = submitted
    quiz.score   = correct_count
    db.commit()

    return {
        'score':   correct_count,
        'total':   10,
        'passed':  correct_count >= 6,   # 6/10 unlocks the interview
        'results': [
            {
                'id':          q['id'],
                'correct':     q['correct'],
                'explanation': q['explanation'],
                'your_answer': submitted.get(str(q['id']))
            }
            for q in quiz.questions
        ]
    }