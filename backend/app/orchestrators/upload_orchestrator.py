from sqlalchemy.orm import Session
import httpx
import logging
import io
import pdfplumber
from tenacity import RetryError

# OCR imports
try:
    import pytesseract
    from pdf2image import convert_from_bytes
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning(
        "pytesseract/pdf2image not installed. OCR fallback disabled. "
        "Install with: pip install pytesseract pdf2image pillow"
    )

from app.core.database import SessionLocal
from app.services.ml_client import ml_client
from app.models.candidate import Candidate, CandidateStatus
from app.models.score import Score
from app.models.feedback import Feedback

logger = logging.getLogger(__name__)


def _unwrap_error(exc: BaseException) -> BaseException:
    if isinstance(exc, RetryError):
        fut = exc.last_attempt
        try:
            inner = fut.exception()
            if inner is not None:
                return inner
        except Exception:
            return exc
    return exc


def _format_error(exc: BaseException) -> str:
    e = _unwrap_error(exc)
    if isinstance(e, httpx.HTTPStatusError):
        body = (e.response.text or "").strip().replace("\n", " ")
        if len(body) > 400:
            body = body[:400] + "…"
        return f"HTTP {e.response.status_code} from {e.request.method} {e.request.url} — {body}"
    if isinstance(e, httpx.RequestError):
        return f"HTTP request error: {e}"
    return str(e)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract full text from PDF using pdfplumber, with OCR fallback for scanned PDFs.

    Flow:
    1. Try pdfplumber (fast, for digital PDFs)
    2. If < 50 chars extracted, try OCR with Tesseract (for scanned/image PDFs)
    3. Return whatever text was extracted
    """
    text = ""

    try:
        logger.info("🔍 Attempting text extraction with pdfplumber...")
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text

        extracted_length = len(text)
        logger.info(f"✅ pdfplumber extracted {extracted_length} characters")

        if extracted_length < 50:
            logger.warning(f"⚠️ Low text extraction ({extracted_length} chars) — attempting OCR fallback...")

            if not OCR_AVAILABLE:
                logger.error("❌ OCR not available. Install: pip install pytesseract pdf2image pillow")
                return text

            try:
                logger.info("🔄 Converting PDF to images for OCR...")
                images = convert_from_bytes(file_bytes, dpi=300)
                logger.info(f"📄 Converted to {len(images)} image(s), running Tesseract OCR...")

                ocr_text = ""
                for page_num, image in enumerate(images, 1):
                    logger.info(f"🔤 OCR on page {page_num}/{len(images)}...")
                    page_ocr_text = pytesseract.image_to_string(image, lang='eng')
                    ocr_text += page_ocr_text
                    if page_ocr_text.strip():
                        logger.info(f"   ✓ Page {page_num}: {len(page_ocr_text)} chars via OCR")

                if len(ocr_text) > extracted_length:
                    logger.info(f"✅ OCR improved extraction: {extracted_length} → {len(ocr_text)} chars")
                    text = ocr_text
                else:
                    logger.info(f"⚠️ OCR didn't improve results. Keeping pdfplumber text ({extracted_length} chars)")

            except Exception as ocr_error:
                logger.error(f"❌ OCR failed: {ocr_error}. Continuing with pdfplumber extraction...")

        logger.info(f"📊 Final extraction: {len(text)} characters")
        return text

    except Exception as e:
        logger.error(f"❌ PDF extraction failed: {e}", exc_info=True)
        return ""


class UploadOrchestrator:
    @staticmethod
    async def process_resume(
        candidate_id: str,
        file_url: str,
        job_role: str = None,
        job_description: str = None,
    ):
        """Process resume after upload.

        Pipeline:
          Step 0 — Download PDF and extract full text (fatal if fails)
          Step 1 — Parse resume via ML /parse            (fatal if fails)
          Step 2 — Score resume via ML /score            (fatal if fails)
          Step 3 — Generate feedback via /gemini/feedback (NON-FATAL — Gemini optional)

        Only Steps 0-2 can mark a candidate as failed.
        Step 3 failure is logged as a warning but candidate is still marked completed.
        """
        db = SessionLocal()

        try:
            candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
            if not candidate:
                logger.error(f"Candidate {candidate_id} not found")
                return

            file_url = candidate.file_url or file_url
            if not file_url:
                raise ValueError("Candidate has no file_url")

            candidate.status = CandidateStatus.PROCESSING
            candidate.error_message = None
            db.commit()

            # ── Step 0: Download PDF and extract full text ──────────────────
            logger.info(f"📥 Downloading PDF for candidate {candidate_id}")
            async with httpx.AsyncClient() as client:
                file_response = await client.get(file_url)
                file_response.raise_for_status()
                file_bytes = file_response.content
                logger.info(f"Downloaded PDF: {len(file_bytes)} bytes")

            full_text = extract_text_from_pdf(file_bytes)
            logger.info(f"Extracted {len(full_text)} characters from PDF")

            if len(full_text.strip()) < 50:
                logger.warning(
                    f"Very short text extracted ({len(full_text)} chars). "
                    f"PDF may be scanned or empty."
                )

            # ── Step 1: Parse resume ─────────────────────────────────────────
            logger.info(f"Parsing resume for candidate {candidate_id}")
            parsed_data = await ml_client.parse_resume(file_url)
            logger.info(f"Parse complete. Keys: {list(parsed_data.keys())}")

            # Attach full text so scorer has raw text available
            parsed_data["full_text"] = full_text

            # Update candidate record with parsed data
            candidate.parsed_data = parsed_data
            candidate.name = parsed_data.get("name", candidate.name)
            candidate.email = parsed_data.get("email", candidate.email)
            candidate.phone = parsed_data.get("phone", candidate.phone)
            db.commit()

            # ── Step 2: Score resume (pretrained model) ──────────────────────
            logger.info(f"Scoring resume for candidate {candidate_id}")
            logger.info(f"required_skills: {candidate.required_skills}")

            score_data = await ml_client.score_resume(
                parsed_data,
                required_skills=candidate.required_skills,
            )

            overall_score = score_data.get("overall_score", 0.0)
            components = score_data.get("components", {})

            score = Score(
                candidate_id=candidate_id,
                overall_score=overall_score,
                skill_score=components.get("skills", 0.0),
                experience_score=components.get("experience", 0.0),
                education_score=components.get("education", 0.0),
                breakdown={
                    **components,
                    "matched_skills": score_data.get("matched_skills", []),
                    "missing_skills": score_data.get("missing_skills", []),
                    "additional_skills": score_data.get("additional_skills", []),
                    "explanation": score_data.get("explanation", ""),
                    "fairness_applied": score_data.get("fairness_applied", False),
                    "mode": score_data.get("mode", "baseline"),
                },
            )
            db.add(score)
            db.flush()  # Save score before feedback attempt
            logger.info(f"Score saved: {overall_score}")

            # ── Step 3: Generate feedback (Gemini — NON-FATAL) ───────────────
            # If Gemini is down or the model is deprecated, we still mark the
            # candidate as completed. The score is already saved.
            feedback_text = ""
            strengths = None
            improvements = None

            try:
                logger.info(f"Generating Gemini feedback for candidate {candidate_id}")
                feedback_text = await ml_client.generate_feedback(score_data, parsed_data)
                logger.info(f"Gemini feedback generated ({len(feedback_text)} chars)")
            except Exception as feedback_err:
                logger.warning(
                    f"Gemini feedback failed for candidate {candidate_id} "
                    f"(non-fatal): {_format_error(feedback_err)}"
                )
                # Derive basic feedback from score data instead
                feedback_text = (
                    f"Score: {overall_score:.1f}/100. "
                    f"Mode: {score_data.get('mode', 'baseline')}. "
                    f"{score_data.get('explanation', '')}"
                ).strip()

            # Derive strengths/improvements from matched/missing skills
            matched = score_data.get("matched_skills") or []
            missing = score_data.get("missing_skills") or []

            if matched:
                strengths = ", ".join(str(s) for s in matched[:10])
            if missing:
                improvements = ", ".join(str(s) for s in missing[:10])

            feedback = Feedback(
                candidate_id=candidate_id,
                feedback_text=feedback_text,
                strengths=strengths,
                improvements=improvements,
            )
            db.add(feedback)

            # ── Mark completed ───────────────────────────────────────────────
            candidate.status = CandidateStatus.COMPLETED
            candidate.error_message = None
            db.commit()

            logger.info(f"Candidate {candidate_id} processing complete. Score: {overall_score}")

        except Exception as e:
            detail = _format_error(e)
            logger.error(
                "Failed to process candidate %s: %s",
                candidate_id, detail, exc_info=True
            )
            try:
                candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
                if candidate:
                    candidate.status = CandidateStatus.FAILED
                    candidate.error_message = detail
                    db.commit()
            except Exception as db_err:
                logger.error(f"Could not update candidate status to failed: {db_err}")
        finally:
            db.close()