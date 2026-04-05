from sqlalchemy import Column, String, Float, DateTime, JSON
from app.models.base import BaseModel

class BiasMetric(BaseModel):
    __tablename__ = "bias_metrics"
    
    metric_name = Column(String(100), nullable=False)  # e.g., "demographic_parity", "equal_opportunity"
    group_type = Column(String(50), nullable=False)    # e.g., "gender", "ethnicity"
    group_name = Column(String(100), nullable=False)   # e.g., "female", "male"
    metric_value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=True)
    is_biased = Column(String(10), nullable=False)     # "yes", "no", "warning"
    details = Column(JSON, nullable=True)              # Additional context
    calculated_at = Column(DateTime(timezone=True), nullable=False)