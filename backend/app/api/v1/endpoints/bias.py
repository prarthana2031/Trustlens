from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.models.bias_metric import BiasMetric

router = APIRouter()

@router.get("/metrics")
async def get_bias_metrics(
    group_type: Optional[str] = Query(None, description="Filter by group type (gender, ethnicity, etc.)"),
    db: Session = Depends(get_db)
):
    """Get bias metrics"""
    query = db.query(BiasMetric)
    if group_type:
        query = query.filter(BiasMetric.group_type == group_type)
    
    metrics = query.order_by(BiasMetric.calculated_at.desc()).all()
    
    return {
        "success": True,
        "data": [
            {
                "id": m.id,
                "metric_name": m.metric_name,
                "group_type": m.group_type,
                "group_name": m.group_name,
                "metric_value": m.metric_value,
                "threshold": m.threshold,
                "is_biased": m.is_biased,
                "details": m.details,
                "calculated_at": m.calculated_at.isoformat() if m.calculated_at else None
            }
            for m in metrics
        ]
    }

@router.get("/summary")
async def get_bias_summary(
    db: Session = Depends(get_db)
):
    """Get summary of bias analysis"""
    # Get latest metrics for each type
    from sqlalchemy import distinct
    metric_types = db.query(distinct(BiasMetric.metric_name)).all()
    
    summary = []
    for (metric_name,) in metric_types:
        latest = db.query(BiasMetric).filter(BiasMetric.metric_name == metric_name).order_by(BiasMetric.calculated_at.desc()).first()
        if latest:
            summary.append({
                "metric_name": metric_name,
                "latest_value": latest.metric_value,
                "is_biased": latest.is_biased,
                "calculated_at": latest.calculated_at.isoformat() if latest.calculated_at else None
            })
    
    return {
        "success": True,
        "data": summary
    }