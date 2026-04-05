import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class MLClient:
    def __init__(self):
        self.timeout = 30.0
        self.client = httpx.Client(timeout=self.timeout)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def parse_resume(self, file_url: str) -> Dict[str, Any]:
        """Call ML parsing service"""
        try:
            response = self.client.post(
                f"{settings.ML_PARSING_SERVICE_URL}/parse",
                json={"file_url": file_url}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"ML parsing failed: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def score_resume(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call ML scoring service"""
        try:
            response = self.client.post(
                f"{settings.ML_SCORING_SERVICE_URL}/score",
                json=parsed_data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"ML scoring failed: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def analyze_bias(self, candidates_data: list) -> Dict[str, Any]:
        """Call ML bias analysis service"""
        try:
            response = self.client.post(
                f"{settings.ML_BIAS_SERVICE_URL}/analyze",
                json={"candidates": candidates_data}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"ML bias analysis failed: {str(e)}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_feedback(self, score_data: Dict[str, Any], parsed_data: Dict[str, Any]) -> str:
        """Call ML feedback service"""
        try:
            response = self.client.post(
                f"{settings.ML_FEEDBACK_SERVICE_URL}/generate",
                json={
                    "score_data": score_data,
                    "parsed_data": parsed_data
                }
            )
            response.raise_for_status()
            return response.json().get("feedback", "")
        except Exception as e:
            logger.error(f"ML feedback generation failed: {str(e)}")
            raise

ml_client = MLClient()