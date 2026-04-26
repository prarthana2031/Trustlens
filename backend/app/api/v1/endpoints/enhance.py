"""Enhancement endpoint — pretrained baseline + Gemini AI full report."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.candidate import Candidate
from app.models.score import Score
from app.models.bias_metric import BiasMetric
from app.services.ml_client import ml_client

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{candidate_id}/enhance", response_model=Dict[str, Any])
async def enhance_candidate_score(
    candidate_id: str,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)  # Re-enable when auth is ready
):
    """
    Enhance a candidate's score using Gemini AI.

    Flow:
      1. Load candidate + their original pretrained score
      2. Call ML /candidate-report  → full Gemini report
         (overall_score, verdict, matched/missing skills, recommendations,
          score_breakdown, experience_years, education_level, soft_skills)
      3. Store Gemini results in the enhanced_* fields on the Score row
      4. Re-run bias analysis with the enhanced score (non-fatal)
      5. Return original_score + enhanced_score + full report

    The pretrained score (original_score) is NEVER modified.
    """
    logger.info(f"Enhancement request for candidate: {candidate_id}")

    # ── Load candidate ───────────────────────────────────────────────────────
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    if not candidate.parsed_data:
        raise HTTPException(
            status_code=400,
            detail="Candidate has no parsed data. Please wait for processing to complete."
        )

    # ── Load original score ──────────────────────────────────────────────────
    score_row = (
        db.query(Score)
        .filter(Score.candidate_id == candidate_id)
        .order_by(Score.version.desc(), Score.created_at.desc())
        .first()
    )
    if not score_row:
        raise HTTPException(
            status_code=404,
            detail="No original score found. Please process the candidate first."
        )

    required_skills = candidate.required_skills or []
    job_role = candidate.job_role or "Not specified"

    # ── Step 1: Call /candidate-report (pretrained + Gemini) ─────────────────
    try:
        logger.info(
            f"📋 Calling /candidate-report for candidate {candidate_id} | "
            f"role={job_role} | skills={len(required_skills)}"
        )

        report = await ml_client.candidate_report(
            parsed_data=candidate.parsed_data,
            required_skills=required_skills,
            job_role=job_role,
            mode="enhanced",
            fairness_mode="balanced",
        )

        logger.info(
            f"/candidate-report success. "
            f"Score={report.get('overall_score')} verdict={report.get('verdict')}"
        )

    except Exception as e:
        logger.error(f"/candidate-report failed for candidate {candidate_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Gemini enhancement failed: {str(e)}"
        )

    # ── Step 2: Store enhanced results on the Score row ──────────────────────
    enhanced_score_value = float(report.get("overall_score", score_row.overall_score))

    enhanced_breakdown = {
        "verdict": report.get("verdict", ""),
        "score_breakdown": report.get("score_breakdown", {}),
        "matched_skills": report.get("matched_skills", []),
        "missing_skills": report.get("missing_skills", []),
        "additional_skills": report.get("additional_skills", []),
        "experience_years": report.get("experience_years", 0.0),
        "education_level": report.get("education_level", ""),
        "soft_skills": report.get("soft_skills", []),
        "project_count": report.get("project_count", 0),
        "certification_count": report.get("certification_count", 0),
        "recommendations": report.get("recommendations", []),
        "weights_used": report.get("weights_used", {}),
        "skill_match_percentage": report.get("skill_match_percentage", 0.0),
        "experience_level": report.get("experience_level", ""),
    }

    score_row.enhanced_score = enhanced_score_value
    score_row.enhanced_breakdown = enhanced_breakdown
    score_row.enhanced_at = datetime.now(timezone.utc)
    score_row.enhanced_by_model = "gemini-2.0-flash"
    score_row.enhancement_explanation = report.get("explanation", "")
    score_row.bias_correction_applied = "Gemini AI fairness (balanced)"

    # ── Step 3: Re-run bias analysis (non-fatal) ─────────────────────────────
    enhanced_bias_metrics = None
    try:
        candidates_data = [{
            "id": candidate_id,
            "score": str(enhanced_score_value),
        }]

        bias_result = await ml_client.analyze_bias(
            candidates_data=candidates_data,
            scores=[enhanced_score_value],
        )

        if bias_result and isinstance(bias_result, dict):
            enhanced_bias_metrics = bias_result
            calculated_at = datetime.now(timezone.utc)

            for metric in bias_result.get("groups", []):
                db.add(BiasMetric(
                    metric_name="enhanced_bias_analysis",
                    group_type=metric.get("group_type", "unknown"),
                    group_name=metric.get("group_name", "unknown"),
                    metric_value=metric.get("selection_rate", 0.0),
                    threshold=None,
                    is_biased="yes" if bias_result.get("summary", {}).get("is_biased", False) else "no",
                    details=metric,
                    calculated_at=calculated_at,
                    candidate_id=candidate_id,
                    is_enhanced="yes",
                    enhanced_bias_metrics=bias_result,
                    bias_enhanced_at=calculated_at,
                ))

        logger.info(f"Bias analysis complete for candidate {candidate_id}")

    except Exception as bias_err:
        logger.warning(
            f" Enhanced bias analysis failed for candidate {candidate_id} "
            f"(non-fatal): {bias_err}"
        )
        enhanced_bias_metrics = None

    # ── Commit everything ────────────────────────────────────────────────────
    try:
        db.commit()
    except Exception as db_err:
        db.rollback()
        logger.error(f"DB commit failed for candidate {candidate_id}: {db_err}")
        raise HTTPException(status_code=500, detail=f"Failed to save enhanced results: {db_err}")

    logger.info(
        f"Enhancement complete for candidate {candidate_id}. "
        f"Score: {score_row.overall_score} → {enhanced_score_value}"
    )

    # ── Return response ──────────────────────────────────────────────────────
    return {
        "success": True,
        "candidate_id": candidate_id,
        "name": candidate.name,
        "job_role": job_role,
        "original_score": score_row.overall_score,
        "enhanced_score": enhanced_score_value,
        "score_delta": round(enhanced_score_value - score_row.overall_score, 2),
        "verdict": report.get("verdict", ""),
        "matched_skills": report.get("matched_skills", []),
        "missing_skills": report.get("missing_skills", []),
        "additional_skills": report.get("additional_skills", []),
        "recommendations": report.get("recommendations", []),
        "explanation": report.get("explanation", ""),
        "skill_match_percentage": report.get("skill_match_percentage", 0.0),
        "experience_level": report.get("experience_level", ""),
        "experience_years": report.get("experience_years", 0.0),
        "education_level": report.get("education_level", ""),
        "soft_skills": report.get("soft_skills", []),
        "score_breakdown": report.get("score_breakdown", {}),
        "bias_metrics": enhanced_bias_metrics,
        "enhanced_at": score_row.enhanced_at.isoformat(),
        "enhanced_by_model": score_row.enhanced_by_model,
    }