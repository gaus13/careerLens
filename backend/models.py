from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = 'users'
    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String, nullable=False)
    email           = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at      = Column(DateTime, server_default=func.now())

    # one user → many sessions
    sessions = relationship('Session', back_populates='user')


class Session(Base):
    __tablename__ = 'sessions'
    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey('users.id'), nullable=False)
    target_role = Column(String, nullable=True)   # set after career selection
    status      = Column(String, default='in_progress')  # or 'completed'
    created_at  = Column(DateTime, server_default=func.now())

    user        = relationship('User', back_populates='sessions')
    resume      = relationship('ResumeData', back_populates='session', uselist=False)
    career_rec  = relationship('CareerRecommendation', back_populates='session', uselist=False)
    gap         = relationship('GapAnalysis', back_populates='session', uselist=False)
    quiz        = relationship('QuizAttempt', back_populates='session', uselist=False)
    interviews  = relationship('InterviewQuestion', back_populates='session')
    report      = relationship('FinalReport', back_populates='session', uselist=False)


class ResumeData(Base):
    __tablename__ = 'resume_data'
    id               = Column(Integer, primary_key=True, index=True)
    session_id       = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    raw_text         = Column(String)
    extracted_skills = Column(JSON)   # AI will fill this later
    created_at       = Column(DateTime, server_default=func.now())

    session = relationship('Session', back_populates='resume')


class CareerRecommendation(Base):
    __tablename__ = 'career_recommendations'
    id              = Column(Integer, primary_key=True, index=True)
    session_id      = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    recommendations = Column(JSON)   # the full AI JSON response
    created_at      = Column(DateTime, server_default=func.now())

    session = relationship('Session', back_populates='career_rec')


class GapAnalysis(Base):
    __tablename__ = 'gap_analysis'
    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    gaps       = Column(JSON)     # matched skills, missing skills
    roadmap    = Column(JSON)     # week-by-week learning plan
    created_at = Column(DateTime, server_default=func.now())

    session = relationship('Session', back_populates='gap')


class QuizAttempt(Base):
    __tablename__ = 'quiz_attempts'
    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    questions  = Column(JSON)   # 10 MCQ questions WITH correct answers (stored safely)
    answers    = Column(JSON)   # what the user submitted
    score      = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

    session = relationship('Session', back_populates='quiz')


class InterviewQuestion(Base):
    __tablename__ = 'interview_questions'
    id          = Column(Integer, primary_key=True, index=True)
    session_id  = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    question    = Column(String, nullable=False)
    user_answer = Column(String, nullable=True)
    ai_feedback = Column(JSON, nullable=True)   # score, strengths, improvements
    score       = Column(Float, nullable=True)
    created_at  = Column(DateTime, server_default=func.now())

    session = relationship('Session', back_populates='interviews')


class FinalReport(Base):
    __tablename__ = 'final_reports'
    id              = Column(Integer, primary_key=True, index=True)
    session_id      = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    readiness_score = Column(Float)
    strengths       = Column(JSON)
    improvements    = Column(JSON)
    next_steps      = Column(JSON)
    created_at      = Column(DateTime, server_default=func.now())

    session = relationship('Session', back_populates='report')