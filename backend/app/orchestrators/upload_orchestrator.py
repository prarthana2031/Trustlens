from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.ml_client import ml_client
from app.models.candidate import Candidate, CandidateStatus
from app.models.score import Score
from app.models.feedback import Feedback
import logging

logger = logging.getLogger(__name__)

class UploadOrchestrator:
    @staticmethod
    async def process_resume(candidate_id: str, file_url: str):
        """Process resume after upload"""
        db = SessionLocal()
        
        try:
            # Update status to processing
            candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
            if not candidate:
                logger.error(f"Candidate {candidate_id} not found")
                return
            
            candidate.status = CandidateStatus.PROCESSING
            db.commit()
            
            # Step 1: Parse resume
            logger.info(f"Parsing resume for candidate {candidate_id}")
            parsed_data = await ml_client.parse_resume(file_url)
            
            # Update candidate with parsed data
            candidate.parsed_data = parsed_data
            candidate.name = parsed_data.get("name", candidate.name)
            candidate.email = parsed_data.get("email", candidate.email)
            candidate.phone = parsed_data.get("phone", candidate.phone)
            db.commit()
            
            # Step 2: Score resume
            logger.info(f"Scoring resume for candidate {candidate_id}")
            score_data = await ml_client.score_resume(parsed_data)
            
            # Save scores
            score = Score(
                candidate_id=candidate_id,
                overall_score=score_data["overall_score"],
                skill_score=score_data["skill_score"],
                experience_score=score_data["experience_score"],
                education_score=score_data["education_score"],
                breakdown=score_data.get("breakdown", {})
            )
            db.add(score)
            
            # Step 3: Generate feedback
            logger.info(f"Generating feedback for candidate {candidate_id}")
            feedback_text = await ml_client.generate_feedback(score_data, parsed_data)
            
            feedback = Feedback(
                candidate_id=candidate_id,
                feedback_text=feedback_text,
                strengths=score_data.get("strengths"),
                improvements=score_data.get("improvements")
            )
            db.add(feedback)
            
            # Update status to completed
            candidate.status = CandidateStatus.COMPLETED
            db.commit()
            
            logger.info(f"Successfully processed candidate {candidate_id}")
            
        except Exception as e:
            logger.error(f"Failed to process candidate {candidate_id}: {str(e)}")
            if db:
                candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
                if candidate:
                    candidate.status = CandidateStatus.FAILED
                    candidate.error_message = str(e)
                    db.commit()
        finally:
            db.close()