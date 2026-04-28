from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.candidate import Candidate
from app.models.score import Score

router = APIRouter()

@router.get("/candidate/{candidate_id}")
async def get_candidate_scores(
    candidate_id: str,
    version: Optional[Literal["original", "enhanced"]] = Query("original", description="Score version: 'original' or 'enhanced'"),
    db: Session = Depends(get_db)
):
    """
    Get scores for a candidate.

    Args:
        candidate_id: The candidate ID
        version: 'original' (default) or 'enhanced' for Gemini-enhanced scores

    Returns:
        Score data. For version='enhanced', returns enhanced data if exists, else 404.
    """
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

    # Return enhanced version if requested and available
    if version == "enhanced":
        if score.enhanced_score is None:
            raise HTTPException(
                status_code=404,
                detail="Enhanced score not found. Run enhancement first via POST /candidates/{id}/enhance"
            )

        # Extract components from enhanced_breakdown
        enhanced_breakdown = score.enhanced_breakdown or {}
        score_breakdown = enhanced_breakdown.get("score_breakdown", {})
        
        return {
            "success": True,
            "data": {
                "id": score.id,
                "candidate_id": score.candidate_id,
                "overall_score": score.enhanced_score,
                "skill_score": score_breakdown.get("skills", 0.0),
                "experience_score": score_breakdown.get("experience", 0.0),
                "education_score": score_breakdown.get("education", 0.0),
                "breakdown": {
                    "skills": score_breakdown.get("skills", {}),
                    "experience": score_breakdown.get("experience", 0.0),
                    "education": score_breakdown.get("education", 0.0),
                    "projects": score_breakdown.get("projects", 0.0),
                    "soft_skills": score_breakdown.get("soft_skills", []),
                    "matched_skills": enhanced_breakdown.get("matched_skills", []),
                    "missing_skills": enhanced_breakdown.get("missing_skills", []),
                    "additional_skills": enhanced_breakdown.get("additional_skills", []),
                },
                "ranking_percentile": score.ranking_percentile,
                "version": "enhanced",
                "enhanced_at": score.enhanced_at.isoformat() if score.enhanced_at else None,
                "enhanced_by_model": score.enhanced_by_model,
                "explanation": score.enhancement_explanation,
                "bias_correction_applied": score.bias_correction_applied,
                "created_at": score.created_at.isoformat() if score.created_at else None
            }
        }

    # Return original version (default)
    breakdown = score.breakdown or {}
    
    # Ensure breakdown has proper structure
    formatted_breakdown = {
        "skills": {},
        "experience": breakdown.get("experience", 0.0),
        "education": breakdown.get("education", 0.0),
        "projects": breakdown.get("projects", 0.0),
        "soft_skills": breakdown.get("soft_skills", []),
    }
    
    # Convert skills array to key-value object if needed
    raw_skills = breakdown.get("skills", [])
    if isinstance(raw_skills, list):
        # Convert list of skill dicts to key-value format
        for skill in raw_skills:
            if isinstance(skill, dict):
                skill_name = skill.get("name", "unknown")
                skill_score = skill.get("score", 0.0)
                formatted_breakdown["skills"][skill_name] = skill_score
    elif isinstance(raw_skills, dict):
        formatted_breakdown["skills"] = raw_skills
    
    # Add metadata fields from breakdown
    if "matched_skills" in breakdown:
        formatted_breakdown["matched_skills"] = breakdown["matched_skills"]
    if "missing_skills" in breakdown:
        formatted_breakdown["missing_skills"] = breakdown["missing_skills"]
    if "additional_skills" in breakdown:
        formatted_breakdown["additional_skills"] = breakdown["additional_skills"]
    
    return {
        "success": True,
        "data": {
            "id": score.id,
            "candidate_id": score.candidate_id,
            "overall_score": score.overall_score,
            "skill_score": score.skill_score,
            "experience_score": score.experience_score,
            "education_score": score.education_score,
            "breakdown": formatted_breakdown,
            "ranking_percentile": score.ranking_percentile,
            "version": "original",
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