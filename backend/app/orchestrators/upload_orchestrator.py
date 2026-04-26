from sqlalchemy.orm import Session
import httpx
import logging
import io
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
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


def _calculate_duration_years(start_date: str, end_date: str) -> float:
    """Calculate years between two dates in MM/YYYY or YYYY format.
    
    Args:
        start_date: Date in "MM/YYYY", "YYYY", or date string format
        end_date: Date in same format, or "Present"/"Current"/"Now" for current date
    
    Returns:
        Duration in years as a float (e.g., 2.5 for 2 years 6 months), or 0.0 if invalid
    """
    def parse_date_str(date_str):
        if not date_str:
            return None
        if isinstance(date_str, str) and date_str.lower() in ["present", "current", "now"]:
            return datetime.now()
        
        # Try MM/YYYY format
        match = re.match(r'(\d{1,2})/(\d{4})', str(date_str))
        if match:
            month, year = int(match.group(1)), int(match.group(2))
            if 1 <= month <= 12:
                return datetime(year, month, 1)
        
        # Try YYYY format (assume January)
        match = re.match(r'^(\d{4})$', str(date_str))
        if match:
            year = int(match.group(1))
            if 1900 <= year <= 2100:
                return datetime(year, 1, 1)
        
        return None
    
    start = parse_date_str(start_date)
    end = parse_date_str(end_date)
    
    if not start or not end:
        return 0.0
    
    if start > end:
        return 0.0
    
    try:
        delta = relativedelta(end, start)
        years = delta.years + (delta.months / 12.0)
        return round(years, 1)
    except Exception:
        return 0.0


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

            # Unwrap double nesting if present (ML service wraps as {"parsed_data": {...}})
            inner_data = parsed_data.get("parsed_data", parsed_data)
            
            # Attach full text so scorer has raw text available
            inner_data["full_text"] = full_text
            
            # Normalize skills - split comma-separated entries
            raw_skills = inner_data.get("skills", [])
            normalized_skills = []
            for skill in raw_skills:
                if isinstance(skill, dict):
                    name = skill.get("name", "")
                    # Split comma-separated skill names
                    if "," in name:
                        for part in name.split(","):
                            part = part.strip().lower()
                            if part:
                                normalized_skills.append({
                                    "name": part,
                                    "category": skill.get("category", "other"),
                                    "proficiency": skill.get("proficiency", "intermediate")
                                })
                    else:
                        normalized_skills.append({
                            "name": name.lower() if name else "",
                            "category": skill.get("category", "other"),
                            "proficiency": skill.get("proficiency", "intermediate")
                        })
                elif isinstance(skill, str):
                    for part in skill.split(","):
                        part = part.strip().lower()
                        if part:
                            normalized_skills.append({
                                "name": part,
                                "category": "other",
                                "proficiency": "intermediate"
                            })
            # Deduplicate skills by name
            seen_skills = set()
            deduped_skills = []
            for skill in normalized_skills:
                name = skill.get("name", "").lower().strip()
                if name and name not in seen_skills:
                    seen_skills.add(name)
                    deduped_skills.append(skill)
            
            inner_data["skills"] = deduped_skills
            inner_data["skill_count"] = len(deduped_skills)
            
            # Normalize experience entries - fix ML parsing issues
            raw_experience = inner_data.get("experience", [])
            normalized_exp = []
            for exp in raw_experience:
                if not isinstance(exp, dict):
                    continue
                
                title = (exp.get("title") or "").strip()
                company = (exp.get("company") or "").strip()
                description = (exp.get("description") or "").strip()
                start_date = exp.get("start_date")
                end_date = exp.get("end_date")
                
                # Fix 1: Swap if company looks like a title and title looks like a company/date
                # Pattern: title="RapidTech Solutions 03/2023", company="Present"
                if company.lower() in ["present", "current", "now"] and re.search(r'\d{2}/\d{4}|\d{4}', title):
                    # Swap them
                    title, company = company, title
                
                # Fix 2: Extract date from title if present
                # Pattern: "RapidTech Solutions 03/2023" -> company="RapidTech Solutions", start_date="03/2023"
                date_match = re.search(r'(\d{2}/\d{4}|\d{4})\s*-\s*(\d{2}/\d{4}|\d{4}|Present|Current|Now)', title, re.IGNORECASE)
                if date_match:
                    start_date = date_match.group(1)
                    end_date_str = date_match.group(2)
                    if end_date_str.lower() in ["present", "current", "now"]:
                        end_date = "Present"
                    else:
                        end_date = end_date_str
                    # Remove date from title
                    title = re.sub(r'\s*(\d{2}/\d{4}|\d{4})\s*-\s*(\d{2}/\d{4}|\d{4}|Present|Current|Now)\s*', ' ', title, flags=re.IGNORECASE).strip()
                else:
                    # Single date pattern: "03/2023" or "2023"
                    single_date = re.search(r'(\d{2}/\d{4}|\d{4})$', title)
                    if single_date:
                        if not start_date:
                            start_date = single_date.group(1)
                        title = title[:single_date.start()].strip()
                
                # Fix 3: Split location from title
                # Pattern: "Senior Software TesterAustin, Texas" or "Senior Software Tester Austin, Texas"
                location = None
                location_match = re.search(r'([A-Za-z\s]+,\s*[A-Za-z\s]+)$', title)
                if location_match:
                    potential_location = location_match.group(1).strip()
                    # Verify it looks like a location (contains comma and reasonable length)
                    if "," in potential_location and len(potential_location) < 50:
                        location = potential_location
                        title = title[:location_match.start()].strip()
                
                # Fix 4: If description contains job title (e.g., "QA EngineerRemote/Onsite...")
                if description and not title:
                    desc_title_match = re.match(r'^([A-Za-z\s/]+?)(Remote|Onsite|Hybrid|$)', description)
                    if desc_title_match:
                        title = desc_title_match.group(1).strip()
                
                # Fix 5: Clean up empty entries
                if not title and not company and not description:
                    continue
                
                # Fix 6: If title contains company name (bullet points getting parsed as titles)
                # Skip entries that are clearly bullet points (start with action verbs)
                bullet_starts = ["successfully", "utilized", "collaborated", "improved", 
                                "conducted", "led", "developed", "monitored", "executed",
                                "identified", "worked", "configured"]
                if any(title.lower().startswith(word) for word in bullet_starts):
                    # This is an achievement, not a job entry - skip or add to previous description
                    if normalized_exp and description:
                        normalized_exp[-1]["description"] += " " + title + " " + description
                    continue
                
                # Calculate duration from extracted dates (not from broken parser value)
                calculated_duration = _calculate_duration_years(start_date, end_date)
                
                # Build normalized entry
                norm_exp = {
                    "title": title,
                    "company": company,
                    "start_date": start_date,
                    "end_date": end_date,
                    "duration_years": calculated_duration,  # ✅ Calculated, not from parser
                    "description": description,
                }
                if location:
                    norm_exp["location"] = location
                
                normalized_exp.append(norm_exp)
            
            inner_data["experience"] = normalized_exp
            
            # Update candidate record with parsed data
            candidate.parsed_data = inner_data
            db.commit()

            # Extract contact info from nested structure with fallback to full_text
            contact = inner_data.get("contact_info", {})
            full_text = inner_data.get("full_text", "")
            
            # Try ML-extracted values first
            name = contact.get("name") or inner_data.get("name")
            email = contact.get("email") or inner_data.get("email") 
            phone = contact.get("phone") or inner_data.get("phone")
            
            # Fallback: extract from full_text if still missing
            if not name and full_text:
                # Look for name at start of resume (usually first line or two)
                lines = full_text.strip().split('\n')[:3]
                for line in lines:
                    line = line.strip()
                    # Skip lines that look like email, phone, or URLs
                    if line and '@' not in line and not line.startswith('http'):
                        # Check if it looks like a name (2-3 words, title case)
                        words = line.split()
                        if 1 <= len(words) <= 4:
                            # Check if it contains digits (likely not a name)
                            if not any(char.isdigit() for char in line):
                                name = line
                                break
            
            if not email and full_text:
                email_match = re.search(r'[\w.-]+@[\w.-]+\.\w+', full_text)
                if email_match:
                    email = email_match.group(0)
            
            if not phone and full_text:
                # Match phone patterns like +1-(234)-555-1234, (234) 555-1234, 234-555-1234
                phone_patterns = [
                    r'\+?\d{1,2}[\s\-\.]?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}',
                    r'\(\d{3}\)\s*\d{3}[\s\-]?\d{4}',
                ]
                for pattern in phone_patterns:
                    phone_match = re.search(pattern, full_text)
                    if phone_match:
                        phone = phone_match.group(0)
                        break
            
            # Update contact_info with extracted values
            if name or email or phone:
                inner_data["contact_info"] = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "location": contact.get("location"),
                    "linkedin": contact.get("linkedin"),
                    "github": contact.get("github"),
                }
            
            candidate.name = name or candidate.name
            candidate.email = email or candidate.email
            candidate.phone = phone or candidate.phone
            db.commit()

            # ── Step 2: Score resume (pretrained model) ──────────────────────
            logger.info(f"Scoring resume for candidate {candidate_id}")
            logger.info(f"required_skills: {candidate.required_skills}")

            score_data = await ml_client.score_resume(
                inner_data,
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
                feedback_text = await ml_client.generate_feedback(score_data, inner_data)
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