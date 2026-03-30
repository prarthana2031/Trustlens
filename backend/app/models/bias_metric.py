from sqlalchemy import Column, String, Float, Boolean, Integer
from app.models.base import BaseModel

class BiasMetric(BaseModel):
    __tablename__ = "bias_metrics"
    
    analysis_id = Column(String(100), nullable=False, index=True)
    group_name = Column(String(100), nullable=False)
    group_value = Column(String(100), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    is_fair = Column(Boolean, default=True)
    sample_size = Column(Integer, nullable=True)