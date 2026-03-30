from sqlalchemy import Column, String, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel

class Feedback(BaseModel):
    __tablename__ = "feedback"
    
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    score_id = Column(String(36), ForeignKey("scores.id", ondelete="SET NULL"), nullable=True)
    strengths = Column(ARRAY(String), nullable=True)
    improvements = Column(ARRAY(String), nullable=True)
    summary = Column(Text, nullable=True)
    detailed_analysis = Column(Text, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="feedbacks")
    score = relationship("Score", back_populates="feedback")