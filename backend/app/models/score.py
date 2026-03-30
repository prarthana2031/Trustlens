from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel

class Score(BaseModel):
    __tablename__ = "scores"
    
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Float, nullable=True)
    skill_score = Column(Float, nullable=True)
    experience_score = Column(Float, nullable=True)
    education_score = Column(Float, nullable=True)
    breakdown_json = Column(JSON, nullable=True)
    explanation_json = Column(JSON, nullable=True)
    scored_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="scores")
    feedback = relationship("Feedback", back_populates="score", uselist=False)