from sqlalchemy import Column, String, Integer, JSON, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class CandidateStatus(str, enum.Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Candidate(BaseModel):
    __tablename__ = "candidates"
    
    name = Column(String(255), nullable=True)  # Will be extracted from resume
    email = Column(String(255), nullable=True)
    file_url = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    status = Column(
        Enum(CandidateStatus),
        default=CandidateStatus.PROCESSING,
        nullable=False
    )
    parsed_data = Column(JSON, nullable=True)
    
    # Relationships
    scores = relationship("Score", back_populates="candidate", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="candidate", cascade="all, delete-orphan")