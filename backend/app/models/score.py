from sqlalchemy import Column, String, Float, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Score(BaseModel):
    __tablename__ = "scores"
    
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Float, nullable=False)
    skill_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    education_score = Column(Float, nullable=False)
    breakdown = Column(JSON, nullable=False)  # Detailed breakdown of each category
    ranking_percentile = Column(Float, nullable=True)
    version = Column(Integer, default=1, nullable=False)  # For tracking re-scores
    
    # Relationships
    candidate = relationship("Candidate", back_populates="scores")