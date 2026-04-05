from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.candidate import Candidate
from app.models.feedback import Feedback

router = APIRouter()

@router.get("/candidate/{candidate_id}")
async def get_feedback(
    candidate_id: str,
    db: Session = Depends(get_db)
):
    """Get feedback for a candidate"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    feedback = db.query(Feedback).filter(Feedback.candidate_id == candidate_id).order_by(Feedback.created_at.desc()).first()
    if not feedback:
        return {
            "success": True,
            "data": None,
            "message": "No feedback available for this candidate"
        }
    
    return {
        "success": True,
        "data": {
            "id": feedback.id,
            "candidate_id": feedback.candidate_id,
            "feedback_text": feedback.feedback_text,
            "strengths": feedback.strengths,
            "improvements": feedback.improvements,
            "is_regenerated": feedback.is_regenerated,
            "created_at": feedback.created_at.isoformat() if feedback.created_at else None
        }
    }