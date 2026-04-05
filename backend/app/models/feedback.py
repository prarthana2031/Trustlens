from sqlalchemy import Column, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Feedback(BaseModel):
    __tablename__ = "feedback"
    
    candidate_id = Column(String(36), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    feedback_text = Column(Text, nullable=False)
    strengths = Column(Text, nullable=True)
    improvements = Column(Text, nullable=True)
    is_regenerated = Column(Boolean, default=False)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="feedback")