from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.candidate import Candidate
from app.models.score import Score

router = APIRouter()

@router.get("/candidate/{candidate_id}")
async def get_candidate_scores(
    candidate_id: str,
    db: Session = Depends(get_db)
):
    """Get latest scores for a candidate"""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    score = db.query(Score).filter(Score.candidate_id == candidate_id).order_by(Score.created_at.desc()).first()
    if not score:
        return {
            "success": True,
            "data": None,
            "message": "No scores available for this candidate"
        }
    
    return {
        "success": True,
        "data": {
            "id": score.id,
            "candidate_id": score.candidate_id,
            "overall_score": score.overall_score,
            "skill_score": score.skill_score,
            "experience_score": score.experience_score,
            "education_score": score.education_score,
            "breakdown": score.breakdown,
            "ranking_percentile": score.ranking_percentile,
            "version": score.version,
            "created_at": score.created_at.isoformat() if score.created_at else None
        }
    }

@router.get("/candidate/{candidate_id}/history")
async def get_score_history(
    candidate_id: str,
    db: Session = Depends(get_db)
):
    """Get all score versions for a candidate"""
    scores = db.query(Score).filter(Score.candidate_id == candidate_id).order_by(Score.created_at.desc()).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": s.id,
                "overall_score": s.overall_score,
                "version": s.version,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in scores
        ]
    }