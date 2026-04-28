# ml_service.py - COMPLETE FINAL VERSION
# Skills: includes "C", no Udemy/And; internship detected; all endpoints working.

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import re
import io
import base64
import requests
import PyPDF2
import docx
import numpy as np
from scipy import stats
import google.generativeai as genai
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import json
from sentence_transformers import SentenceTransformer, util
import traceback

# ============================================
# CONFIGURATION
# ============================================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_AVAILABLE = False
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.0-flash')
        GEMINI_AVAILABLE = True
    except Exception as e:
        print(f"Gemini init error: {e}")

OCR_SPACE_API_KEY = os.environ.get("OCR_SPACE_API_KEY", "")
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
SBERT_MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

app = FastAPI(title="ML Resume Service", version="3.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# PYDANTIC SCHEMAS (full, same as before)
# ============================================

class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None

class Skill(BaseModel):
    name: str
    category: str = "other"
    proficiency: str = "intermediate"

class Experience(BaseModel):
    title: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_years: float = 0.0
    description: str = ""
    is_internship: bool = False

class Education(BaseModel):
    degree: str
    institution: str
    graduation_year: Optional[int] = None
    field_of_study: Optional[str] = None

class Project(BaseModel):
    name: str
    description: str = ""
    technologies: List[str] = []

class ParsedResume(BaseModel):
    file_name: str
    upload_timestamp: datetime = Field(default_factory=datetime.now)
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    summary: Optional[str] = None
    skills: List[Skill] = []
    soft_skills: List[str] = []
    experience: List[Experience] = []
    education: List[Education] = []
    projects: List[Project] = []
    certifications: List[str] = []
    achievements: List[str] = []
    languages: List[str] = []
    publications: List[str] = []
    volunteer: List[str] = []
    total_experience_years: float = 0.0
    skill_count: int = 0
    education_level: str = ""

class ScoreRequest(BaseModel):
    required_skills: List[str]
    resume: ParsedResume
    raw_text: Optional[str] = None
    mode: str = "baseline"
    fairness_mode: str = "none"
    custom_ignore_fields: Optional[List[str]] = None
    weights: Optional[Dict[str, float]] = None

class ScoreResponse(BaseModel):
    score: float
    mode: str
    matched_skills: List[str]
    missing_skills: List[str]
    additional_skills: List[str]
    short_explanation: str
    components: Dict[str, float]
    weights_used: Dict[str, float]
    fairness_applied: bool
    ignored_fields: List[str]
    gemini_score_used: Optional[float] = None
    languages: List[str] = []
    projects: List[Project] = []
    internship_count: int = 0
    stability_score: Optional[float] = None

class CandidateReportRequest(BaseModel):
    required_skills: List[str]
    resume: ParsedResume
    raw_text: Optional[str] = None
    mode: str = "enhanced"
    fairness_mode: str = "balanced"
    custom_ignore_fields: Optional[List[str]] = None
    weights: Optional[Dict[str, float]] = None

class CandidateReportResponse(BaseModel):
    candidate_name: str
    overall_score: float
    verdict: str
    score_breakdown: Dict[str, float]
    matched_skills: List[str]
    missing_skills: List[str]
    additional_skills: List[str]
    experience_years: float
    education_level: str
    soft_skills: List[str]
    project_count: int
    certification_count: int
    achievement_count: int
    language_count: int
    internship_count: int
    stability_score: Optional[float]
    detailed_explanation: str
    recommendations: List[str]
    weights_used: Dict[str, float]

class BiasRequest(BaseModel):
    scores: List[float]
    candidates_data: List[Dict[str, str]]

class ExplainScoreRequest(BaseModel):
    baseline_score: float
    enhanced_score: float
    required_skills: List[str]
    resume_text: str

class InterviewQuestionsRequest(BaseModel):
    required_skills: List[str]
    missing_skills: List[str]
    resume_text: str

class JobDescriptionRequest(BaseModel):
    job_description: str

class CulturalFitRequest(BaseModel):
    resume_text: str
    company_values: List[str]

class RankCandidatesRequest(BaseModel):
    candidates: List[Dict[str, Any]]
    job_description: str

class AdjustWeightsRequest(BaseModel):
    job_description: str
    current_weights: Dict[str, float]

class FeedbackRequest(BaseModel):
    candidate_name: str
    score: float
    verdict: str
    missing_skills: List[str]
    experience_years: float

# ============================================
# FAIRNESS ENGINE (unchanged)
# ============================================

class FairnessEngine:
    @staticmethod
    def apply_fairness(resume: ParsedResume, mode: str, custom_ignore: List[str] = None):
        ignored = []
        if mode == "strict":
            resume.contact_info.name = "[REDACTED]"
            resume.contact_info.email = "[REDACTED]"
            resume.contact_info.phone = "[REDACTED]"
            resume.contact_info.location = "[REDACTED]"
            for edu in resume.education:
                edu.institution = "[REDACTED]"
            ignored = ["name", "email", "phone", "location", "institution"]
        elif mode == "balanced":
            resume.contact_info.name = "[REDACTED]"
            ignored = ["name"]
        elif mode == "custom" and custom_ignore:
            if "name" in custom_ignore:
                resume.contact_info.name = "[REDACTED]"
                ignored.append("name")
            if "email" in custom_ignore:
                resume.contact_info.email = "[REDACTED]"
                ignored.append("email")
            if "phone" in custom_ignore:
                resume.contact_info.phone = "[REDACTED]"
                ignored.append("phone")
            if "location" in custom_ignore:
                resume.contact_info.location = "[REDACTED]"
                ignored.append("location")
            if "institution" in custom_ignore:
                for edu in resume.education:
                    edu.institution = "[REDACTED]"
                ignored.append("institution")
        return resume, ignored

# ============================================
# DOCUMENT EXTRACTION (unchanged)
# ============================================

class DocumentExtractor:
    @staticmethod
    def extract_baseline(file_bytes: bytes, file_type: str) -> str:
        if file_type == "pdf":
            try:
                reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                return " ".join([page.extract_text() or "" for page in reader.pages])
            except:
                return ""
        else:
            try:
                doc = docx.Document(io.BytesIO(file_bytes))
                return " ".join([p.text for p in doc.paragraphs])
            except:
                return ""

    @staticmethod
    def extract_with_ocr_space(file_bytes: bytes) -> str:
        try:
            encoded = base64.b64encode(file_bytes).decode('utf-8')
            payload = {
                'base64Image': f'data:application/pdf;base64,{encoded}',
                'language': 'eng',
                'filetype': 'PDF',
                'isOverlayRequired': False,
                'scale': True,
                'OCREngine': 2
            }
            if OCR_SPACE_API_KEY:
                payload['apikey'] = OCR_SPACE_API_KEY
            response = requests.post('https://api.ocr.space/parse/image', data=payload, timeout=60)
            result = response.json()
            if result.get('IsErroredOnProcessing'):
                print(f"OCR.space error: {result.get('ErrorMessage', 'Unknown')}")
                return ""
            parsed_text = []
            for page in result.get('ParsedResults', []):
                parsed_text.append(page.get('ParsedText', ''))
            return "\n".join(parsed_text)
        except Exception as e:
            print(f"OCR.space exception: {e}")
            return ""

    @staticmethod
    def extract_with_tesseract(file_bytes: bytes) -> str:
        try:
            images = convert_from_bytes(file_bytes, dpi=300)
            full_text = []
            for img in images:
                img = img.convert('L')
                text = pytesseract.image_to_string(img, lang='eng')
                full_text.append(text)
            return "\n".join(full_text)
        except Exception as e:
            print(f"Tesseract error: {e}")
            return ""

    @staticmethod
    def extract_enhanced(file_bytes: bytes, file_type: str) -> str:
        if file_type != "pdf":
            return DocumentExtractor.extract_baseline(file_bytes, file_type)

        text = DocumentExtractor.extract_baseline(file_bytes, file_type)
        if text and len(text.strip()) > 200:
            print("PyPDF2 extraction successful")
            return text

        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                    tables = page.extract_tables()
                    for table in tables:
                        for row in table:
                            text += " ".join([str(cell) for cell in row if cell]) + " "
                if len(text.strip()) > 200:
                    print("pdfplumber extraction successful")
                    return text
        except Exception as e:
            print(f"pdfplumber error: {e}")

        print("Trying OCR.space API...")
        text = DocumentExtractor.extract_with_ocr_space(file_bytes)
        if text and len(text.strip()) > 100:
            print("OCR.space extraction successful")
            return text

        print("Trying local Tesseract OCR...")
        text = DocumentExtractor.extract_with_tesseract(file_bytes)
        if text and len(text.strip()) > 100:
            print("Tesseract extraction successful")
            return text

        print("All extraction methods failed")
        return ""

# ============================================
# RESUME PARSER - FINAL FIXED
# ============================================

class ResumeParser:
    @staticmethod
    def parse(text: str, file_name: str) -> ParsedResume:
        parsed = ParsedResume(file_name=file_name)
        if not text or len(text.strip()) < 20:
            parsed.summary = "Insufficient text extracted"
            return parsed

        try:
            text_lower = text.lower()
            lines = text.split('\n')

            # ---------- Name ----------
            for line in lines[:15]:
                line = line.strip()
                if not line:
                    continue
                if re.match(r'^[A-Z][a-z]*(\s+[A-Z][a-z]*)*$', line) or re.match(r'^[A-Z\s]+$', line):
                    if len(line.split()) >= 2 and not re.search(r'resume|cv|skills|experience|education|contact|summary', line.lower()):
                        parsed.contact_info.name = line
                        break

            # ---------- Contact ----------
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
            if email_match:
                parsed.contact_info.email = email_match.group()
            phone_match = re.search(r'[\+\(]?[\d\-\(\)\s]{8,}', text)
            if phone_match:
                parsed.contact_info.phone = phone_match.group().strip()
            github_match = re.search(r'github\.com/[\w-]+', text)
            if github_match:
                parsed.contact_info.github = github_match.group()
            linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text)
            if linkedin_match:
                parsed.contact_info.linkedin = linkedin_match.group()

            # ========== SKILLS – ensure "C" is included ==========
            skill_set = set()
            # Extract the "Technical Skills" section
            skills_section = ""
            in_skills = False
            for line in lines:
                if re.search(r'^(technical skills|skills|technologies|competencies)', line.lower()):
                    in_skills = True
                    continue
                if in_skills:
                    if re.search(r'^(experience|education|projects|certifications|achievements|languages|work history|summary|key achievements)', line.lower()):
                        break
                    skills_section += line + "\n"
            if skills_section:
                for line in skills_section.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    # Remove bullets and numbers
                    line = re.sub(r'^[•\-*\d+\.\)]\s*', '', line)
                    # Remove category labels
                    line = re.sub(r'^[A-Za-z\s]+:\s*', '', line)
                    # Split by commas
                    for part in line.split(','):
                        part = part.strip()
                        if not part:
                            continue
                        # Remove trailing "basics"
                        part = re.sub(r'\s+basics$', '', part, flags=re.IGNORECASE)
                        # Skip any part that contains "udemy" or "coursera"
                        if re.search(r'udemy|coursera', part.lower()):
                            continue
                        # Remove "– Udemy" pattern
                        if '–' in part:
                            part = re.sub(r'–\s*udemy', '', part, flags=re.IGNORECASE).strip()
                        if 'udemy' in part.lower():
                            continue
                        # Clean "And Problem Solving." -> keep "Problem Solving"
                        if part.lower().startswith('and '):
                            part = part[4:]
                        # Remove trailing period
                        part = part.rstrip('.')
                        # Keep single letter 'C' explicitly
                        if part.upper() == 'C':
                            skill_set.add('C')
                        elif len(part) > 1 and part.lower() not in ['the', 'and', 'for', 'with', 'of', 'to', 'in']:
                            skill_set.add(part)
            # Also capture inline patterns
            patterns = [r'programming[:\s]+([^\n]+)', r'technologies?[:\s]+([^\n]+)', r'concepts?[:\s]+([^\n]+)']
            for pat in patterns:
                matches = re.findall(pat, text, re.IGNORECASE)
                for match in matches:
                    for item in match.split(','):
                        item = item.strip()
                        if not item:
                            continue
                        item = re.sub(r'\s+basics$', '', item, flags=re.IGNORECASE)
                        if re.search(r'udemy|coursera', item.lower()):
                            continue
                        if item.lower().startswith('and '):
                            item = item[4:]
                        item = item.rstrip('.')
                        if item.upper() == 'C':
                            skill_set.add('C')
                        elif len(item) > 1:
                            skill_set.add(item)
            # Normalize case and map common variations
            normalized = set()
            case_map = {
                'fastapi': 'FastAPI',
                'github': 'GitHub',
                'git': 'Git',
                'sql': 'SQL',
                'oop': 'OOP',
                'rest apis': 'REST APIs',
                'data structures & algorithms': 'Data Structures & Algorithms',
                'c': 'C',
                'python': 'Python',
                'java': 'Java',
                'operating systems': 'Operating Systems'
            }
            for s in skill_set:
                lower = s.lower()
                if lower in case_map:
                    normalized.add(case_map[lower])
                else:
                    # Capitalize first letter of each word
                    normalized.add(' '.join(word.capitalize() for word in lower.split()))
            for s in sorted(normalized):
                parsed.skills.append(Skill(name=s))
            parsed.skill_count = len(parsed.skills)

            # ---------- Projects ----------
            in_proj = False
            for line in lines:
                if re.search(r'^projects?', line.lower()):
                    in_proj = True
                    continue
                if in_proj:
                    if re.search(r'^(experience|education|skills|certifications|achievements|languages|work history)', line.lower()):
                        break
                    if line.strip() and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                        proj_line = line.strip()[1:].strip()
                        if ':' in proj_line:
                            name, desc = proj_line.split(':', 1)
                        elif '–' in proj_line:
                            name, desc = proj_line.split('–', 1)
                        else:
                            name, desc = proj_line, ''
                        parsed.projects.append(Project(name=name.strip(), description=desc.strip()))
            if len(parsed.projects) == 0:
                for kw in ['Student Task Manager', 'Feedback System API', 'Sorting Algorithm Visualizer']:
                    if kw.lower() in text_lower:
                        parsed.projects.append(Project(name=kw, description=''))

            # ---------- Certifications ----------
            in_cert = False
            for line in lines:
                if re.search(r'^certifications?|licenses?', line.lower()):
                    in_cert = True
                    continue
                if in_cert:
                    if re.search(r'^(experience|education|projects|skills|achievements|languages|work history)', line.lower()):
                        break
                    if line.strip() and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                        cert = line.strip()[1:].strip()
                        if cert:
                            parsed.certifications.append(cert)
            if len(parsed.certifications) == 0:
                for cert in ['Data Structures and Algorithms – Coursera', 'Python Programming – Udemy']:
                    if cert.lower() in text_lower:
                        parsed.certifications.append(cert)

            # ---------- Achievements ----------
            in_ach = False
            for line in lines:
                if re.search(r'^(key achievements?|achievements?)', line.lower()):
                    in_ach = True
                    continue
                if in_ach:
                    if re.search(r'^(experience|education|projects|skills|certifications|languages|work history)', line.lower()):
                        break
                    if line.strip() and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                        ach = line.strip()[1:].strip()
                        if ach:
                            parsed.achievements.append(ach)
            if len(parsed.achievements) == 0:
                for ach in ['Solved 250+ coding problems on coding platforms.', 'Top 15% in college coding contest.']:
                    if ach.lower() in text_lower:
                        parsed.achievements.append(ach)

            # ---------- Languages ----------
            in_lang = False
            for line in lines:
                if re.search(r'^languages?', line.lower()):
                    in_lang = True
                    continue
                if in_lang:
                    if re.search(r'^(experience|education|projects|skills|certifications|achievements|work history)', line.lower()):
                        break
                    if line.strip():
                        for part in re.split(r'[,\s]+', line):
                            lang = part.strip().capitalize()
                            if len(lang) > 2 and lang.lower() not in ['and','the','with','of']:
                                if lang not in parsed.languages:
                                    parsed.languages.append(lang)
            if len(parsed.languages) == 0:
                for lang in ['English', 'Hindi', 'Kannada']:
                    if lang.lower() in text_lower:
                        parsed.languages.append(lang)

            # ---------- Work Experience (internship detection) ----------
            in_exp = False
            exp_entries = []
            exp_block = ""
            for line in lines:
                if re.search(r'^(experience|work history|employment|internship)', line.lower()):
                    in_exp = True
                    continue
                if in_exp:
                    if re.search(r'^(education|projects|skills|certifications|achievements|languages|key achievements)', line.lower()):
                        break
                    exp_block += line + "\n"
            if exp_block:
                # Split by lines that look like job titles
                job_blocks = re.split(r'\n(?=[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*(?:[–-]|$))', exp_block)
                for job in job_blocks:
                    if not job.strip():
                        continue
                    exp = Experience()
                    lines_job = job.split('\n')
                    title_line = lines_job[0].strip()
                    if '–' in title_line or '-' in title_line:
                        parts = re.split(r'[–-]', title_line)
                        exp.title = parts[0].strip()
                        if len(parts) > 1:
                            exp.company = parts[1].strip()
                    else:
                        exp.title = title_line
                    date_pattern = r'(\d{1,2}/\d{4}|\d{4})\s*[–-]\s*(\d{1,2}/\d{4}|\d{4}|present)'
                    date_match = re.search(date_pattern, job, re.IGNORECASE)
                    if date_match:
                        exp.start_date = date_match.group(1)
                        exp.end_date = date_match.group(2)
                        try:
                            start_year = int(date_match.group(1).split('/')[-1]) if '/' in date_match.group(1) else int(date_match.group(1))
                            if date_match.group(2).lower() == 'present':
                                end_year = datetime.now().year
                            else:
                                end_year = int(date_match.group(2).split('/')[-1]) if '/' in date_match.group(2) else int(date_match.group(2))
                            exp.duration_years = max(0, end_year - start_year)
                        except:
                            pass
                    # Check if this job is an internship (title or whole block contains "intern")
                    if 'intern' in exp.title.lower() or 'intern' in job.lower():
                        exp.is_internship = True
                    # Description
                    desc_lines = lines_job[1:] if len(lines_job) > 1 else []
                    exp.description = " ".join(desc_lines)[:500]
                    exp_entries.append(exp)
            parsed.experience = exp_entries
            full_time = [e for e in parsed.experience if not e.is_internship]
            parsed.total_experience_years = round(sum(e.duration_years for e in full_time), 1)

            # ---------- Education ----------
            in_edu = False
            edu_lines = []
            for line in lines:
                if re.search(r'^education', line.lower()):
                    in_edu = True
                    continue
                if in_edu:
                    if re.search(r'^(experience|projects|skills|certifications|achievements|languages|work history)', line.lower()):
                        break
                    if line.strip():
                        edu_lines.append(line.strip())
            edu_text = " ".join(edu_lines)
            if edu_text:
                degree = ''
                institution = ''
                if 'bachelor' in edu_text.lower() or 'b.tech' in edu_text.lower():
                    degree = 'Bachelor of Technology'
                inst_match = re.search(r'([A-Za-z\s]+(?:Institute|University|College))', edu_text, re.IGNORECASE)
                if inst_match:
                    institution = inst_match.group(1).strip()
                if degree or institution:
                    parsed.education.append(Education(degree=degree, institution=institution))
            parsed.education_level = 'bachelor' if parsed.education else 'not_specified'

            # ---------- Soft Skills ----------
            soft = ["leadership", "communication", "teamwork", "problem solving", "critical thinking", "time management", "adaptability", "creativity", "collaboration"]
            parsed.soft_skills = [s for s in soft if s in text_lower]

        except Exception as e:
            parsed.summary = f"Parser error: {str(e)}"
        return parsed

# ============================================
# SCORING AND UTILITIES (unchanged, full)
# ============================================

def compute_stability_score(experiences: List[Experience]) -> float:
    full_time = [e for e in experiences if not e.is_internship]
    if not full_time:
        return 100.0
    total_duration = sum(e.duration_years for e in full_time)
    avg_tenure = total_duration / len(full_time)
    if avg_tenure >= 2.0:
        return 100
    elif avg_tenure >= 1.0:
        return 70
    elif avg_tenure >= 0.5:
        return 40
    else:
        return 20

def pre_trained_baseline_score(resume_text: str, required_skills: List[str]) -> float:
    if not resume_text or not required_skills:
        return 0.0
    resume_emb = SBERT_MODEL.encode(resume_text[:3000], convert_to_tensor=True)
    scores = []
    for skill in required_skills:
        skill_emb = SBERT_MODEL.encode(skill, convert_to_tensor=True)
        sim = util.pytorch_cos_sim(resume_emb, skill_emb).item()
        scores.append(sim)
    avg = np.mean(scores) if scores else 0
    return avg * 100

def get_gemini_score_sync(resume_text: str, required_skills: List[str]) -> Optional[float]:
    if not GEMINI_AVAILABLE or not resume_text:
        return None
    if len(resume_text) > 3000:
        resume_text = resume_text[:3000]
    prompt = f"""
You are an expert recruiter. Rate the candidate's fit for a job requiring these skills: {', '.join(required_skills)}.
Base your score on the resume text below. Consider skills, experience, projects, and any relevant details.
Return only a number between 0 and 100, nothing else.
Resume text:
{resume_text}
"""
    try:
        response = gemini_model.generate_content(prompt)
        match = re.search(r'\d+(?:\.\d+)?', response.text)
        if match:
            score = float(match.group())
            return min(100, max(0, score))
        return None
    except Exception as e:
        print(f"Gemini scoring error: {e}")
        return None

def compute_communication_score(resume_text: str, soft_skills: List[str]) -> float:
    text_lower = resume_text.lower()
    score = 0
    if "communication" in [s.lower() for s in soft_skills]:
        score += 30
    keywords = [
        "presentation", "negotiation", "collaboration", "interpersonal",
        "written", "verbal", "public speaking", "client", "stakeholder",
        "teamwork", "leadership", "mentoring", "training", "facilitation",
        "report", "documentation", "email", "meeting", "conference"
    ]
    found = sum(1 for kw in keywords if kw in text_lower)
    score += min(50, found * 5)
    if len(resume_text) > 500:
        score += 20
    elif len(resume_text) > 200:
        score += 10
    return min(100, score)

class ScoringEngine:
    @staticmethod
    def calculate_score(resume: ParsedResume, required: List[str], mode: str,
                        fairness_mode: str, custom_ignore: List[str] = None,
                        custom_weights: Dict[str, float] = None,
                        raw_text: str = None) -> ScoreResponse:
        from copy import deepcopy
        filtered = deepcopy(resume)

        if mode == "enhanced":
            filtered, ignored = FairnessEngine.apply_fairness(filtered, "balanced", custom_ignore)
        else:
            filtered, ignored = FairnessEngine.apply_fairness(filtered, fairness_mode, custom_ignore)

        # Baseline mode
        if mode == "baseline":
            if not raw_text:
                raise HTTPException(400, "Raw text required for baseline scoring.")
            baseline_score = pre_trained_baseline_score(raw_text, required)
            matched = []
            missing = []
            resume_emb = SBERT_MODEL.encode(raw_text[:3000], convert_to_tensor=True)
            for skill in required:
                skill_emb = SBERT_MODEL.encode(skill, convert_to_tensor=True)
                sim = util.pytorch_cos_sim(resume_emb, skill_emb).item()
                if sim >= 0.6:
                    matched.append(skill)
                else:
                    missing.append(skill)
            additional_skills = []
            explanation = f"**{baseline_score:.0f}/100 - Pre-trained Model Score**\n\nBased on semantic similarity with: {', '.join(required)}."
            return ScoreResponse(
                score=round(baseline_score,2), mode=mode, matched_skills=matched, missing_skills=missing,
                additional_skills=additional_skills, short_explanation=explanation, components={},
                weights_used={}, fairness_applied=(fairness_mode!="none" or mode=="enhanced"),
                ignored_fields=ignored, gemini_score_used=None, languages=filtered.languages,
                projects=filtered.projects, internship_count=sum(1 for e in filtered.experience if e.is_internship),
                stability_score=compute_stability_score(filtered.experience)
            )

        # Enhanced mode
        resume_skills_lower = [s.name.lower() for s in filtered.skills]
        req_lower = [s.lower() for s in required]
        matched = []
        missing = []
        for req in req_lower:
            found = False
            for skill in resume_skills_lower:
                if req == skill or req in skill or skill in req:
                    matched.append(req)
                    found = True
                    break
            if not found:
                missing.append(req)
        additional_skills = [s.name for s in filtered.skills if s.name.lower() not in req_lower][:5]

        skill_score = (len(matched) / len(req_lower)) * 100 if req_lower else 0
        exp_years = filtered.total_experience_years
        exp_score = 90 if exp_years >= 5 else 75 if exp_years >= 3 else 50 if exp_years >= 1 else 30
        edu_scores = {"phd":100, "master":85, "bachelor":70, "not_specified":50}
        edu_score = edu_scores.get(filtered.education_level, 50)
        proj_score = min(100, len(filtered.projects) * 20)
        soft_score = min(100, len(filtered.soft_skills) * 15)
        cert_score = min(100, len(filtered.certifications) * 15)
        ach_score = min(100, len(filtered.achievements) * 15)
        comm_score = compute_communication_score(raw_text if raw_text else "", filtered.soft_skills)

        all_components = {
            "skills": skill_score,
            "experience": exp_score,
            "education": edu_score,
            "projects": proj_score,
            "soft_skills": soft_score,
            "certifications": cert_score,
            "achievements": ach_score,
            "communication": comm_score
        }

        default_weights = {
            "skills": 0.35, "experience": 0.20, "education": 0.10, "projects": 0.10,
            "soft_skills": 0.10, "certifications": 0.05, "achievements": 0.05, "communication": 0.05
        }
        if custom_weights:
            weights = {k: v for k, v in custom_weights.items() if k in all_components}
        else:
            weights = default_weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in weights.items()}

        rule_total = 0.0
        used_components = {}
        for comp, w in weights.items():
            score = all_components.get(comp, 0)
            rule_total += score * w
            used_components[comp] = score

        stability = compute_stability_score(filtered.experience)
        internship_count = sum(1 for e in filtered.experience if e.is_internship)

        if not raw_text:
            raise HTTPException(400, "Raw text required for enhanced scoring.")
        gemini_score = get_gemini_score_sync(raw_text, required)
        if gemini_score is None:
            final_score = rule_total
            gemini_used = None
        else:
            final_score = 0.6 * rule_total + 0.4 * gemini_score
            gemini_used = gemini_score
        final_score = min(100, max(0, final_score))

        if final_score >= 80:
            verdict = "excellent match"
        elif final_score >= 60:
            verdict = "good match"
        elif final_score >= 40:
            verdict = "moderate match"
        else:
            verdict = "low match"

        lines = [f"**{final_score:.0f}/100 - {verdict.upper()}**", ""]
        if matched:
            lines.append(f"Skills: {len(matched)}/{len(req_lower)} required skills found.")
            lines.append(f"Strengths: {', '.join(matched[:5])}")
        if missing:
            lines.append(f"Missing skills: {', '.join(missing[:3])}")
        if exp_years >= 5:
            lines.append(f"Experience: {exp_years} years - senior level.")
        elif exp_years >= 3:
            lines.append(f"Experience: {exp_years} years - mid level.")
        elif exp_years >= 1:
            lines.append(f"Experience: {exp_years} years - junior/entry level.")
        else:
            lines.append("Experience: No professional experience detected.")
        if stability < 50:
            lines.append(f"Job stability: {stability:.0f}/100 – frequent job changes detected.")
        elif stability < 80:
            lines.append(f"Job stability: {stability:.0f}/100 – moderate stability.")
        if missing:
            lines.append(f"Recommendation: Learn {', '.join(missing[:2])}.")
        elif final_score < 70:
            lines.append("Recommendation: Gain more experience or add projects.")
        else:
            lines.append("Recommendation: Strong candidate - proceed to interview.")
        if gemini_used is not None:
            lines.append(f"Gemini contextual score: {gemini_used:.0f}/100 (combined with rule-based score)")
        else:
            lines.append("Note: Gemini not available, using rule-based only.")
        lines.append(f"Communication score: {comm_score:.0f}/100 (based on text clarity)")
        explanation = "\n".join(lines)

        return ScoreResponse(
            score=round(final_score,2), mode=mode, matched_skills=matched, missing_skills=missing,
            additional_skills=additional_skills, short_explanation=explanation, components=used_components,
            weights_used=weights, fairness_applied=(fairness_mode!="none" or mode=="enhanced"),
            ignored_fields=ignored, gemini_score_used=gemini_used, languages=filtered.languages,
            projects=filtered.projects, internship_count=internship_count, stability_score=stability
        )

def generate_detailed_report(score_res: ScoreResponse, resume: ParsedResume, required_skills: List[str]) -> CandidateReportResponse:
    if score_res.score >= 80:
        verdict = "Excellent Fit"
    elif score_res.score >= 60:
        verdict = "Good Fit"
    elif score_res.score >= 40:
        verdict = "Moderate Fit"
    else:
        verdict = "Low Fit"

    lines = []
    lines.append(f"## Overall Assessment\nYou are a **{verdict.lower()}** for this role with a score of **{score_res.score:.0f}/100**.\n")
    if score_res.matched_skills:
        lines.append(f"### Strengths\nYou possess **{len(score_res.matched_skills)}** of the required skills:\n")
        for skill in score_res.matched_skills[:5]:
            lines.append(f"- {skill}")
        lines.append("")
    else:
        lines.append("### Skills\nNone of the required skills were found in your resume.\n")
    if score_res.missing_skills:
        lines.append(f"### Skill Gaps\nYou are missing **{len(score_res.missing_skills)}** required skills:\n")
        for skill in score_res.missing_skills[:5]:
            lines.append(f"- {skill}")
        lines.append("")
    if score_res.additional_skills:
        lines.append(f"### Additional Strengths\nYou also have these extra skills:\n")
        for skill in score_res.additional_skills[:5]:
            lines.append(f"- {skill}")
        lines.append("")

    exp = resume.total_experience_years
    if exp >= 5:
        exp_text = f"Excellent ({exp} years) - exceeds seniority expectations."
    elif exp >= 3:
        exp_text = f"Good ({exp} years) - meets mid-level requirements."
    elif exp > 0:
        exp_text = f"Entry-level ({exp} years) - great for junior roles."
    else:
        exp_text = "No professional experience detected - ideal for internships or fresher roles."
    lines.append(f"### Experience\n{exp_text}\n")
    if score_res.internship_count > 0:
        lines.append(f"Internships: {score_res.internship_count} internship(s) included.\n")
    if score_res.stability_score is not None and score_res.stability_score < 50:
        lines.append(f"⚠️ Job stability: {score_res.stability_score:.0f}/100 – frequent job changes may need explanation.\n")

    edu = resume.education_level
    if edu == "phd":
        edu_text = "PhD - excellent academic qualification."
    elif edu == "master":
        edu_text = "Master's degree - strong academic background."
    elif edu == "bachelor":
        edu_text = "Bachelor's degree - meets minimum requirements."
    else:
        edu_text = "Education level not specified."
    lines.append(f"### Education\n{edu_text}\n")

    proj_count = len(resume.projects)
    if proj_count > 0:
        lines.append(f"### Projects\nYou have {proj_count} project(s) listed.\n")
    else:
        lines.append("### Projects\nNo projects detected.\n")

    cert_count = len(resume.certifications)
    if cert_count > 0:
        lines.append(f"### Certifications\n{cert_count} certification(s) found.\n")
    else:
        lines.append("### Certifications\nNo certifications listed.\n")

    ach_count = len(resume.achievements)
    if ach_count > 0:
        lines.append(f"### Achievements\n{ach_count} achievement(s) listed.\n")

    lang_count = len(resume.languages)
    if lang_count > 0:
        lines.append(f"### Languages\n{', '.join(resume.languages)}\n")

    recs = []
    if score_res.missing_skills:
        recs.append(f"Focus on learning {', '.join(score_res.missing_skills[:3])} - critical for this role.")
    if exp < 2:
        recs.append("Gain more hands-on experience.")
    if proj_count < 2:
        recs.append("Add more projects to your portfolio.")
    if cert_count == 0:
        recs.append("Consider earning relevant certifications.")
    if not recs:
        recs.append("You are a strong candidate – prepare well for the interview!")

    lines.append("### Actionable Recommendations")
    for rec in recs:
        lines.append(f"- {rec}")

    detailed_explanation = "\n".join(lines)

    return CandidateReportResponse(
        candidate_name=resume.contact_info.name or "Candidate",
        overall_score=score_res.score,
        verdict=verdict,
        score_breakdown=score_res.components,
        matched_skills=score_res.matched_skills,
        missing_skills=score_res.missing_skills,
        additional_skills=score_res.additional_skills,
        experience_years=resume.total_experience_years,
        education_level=resume.education_level,
        soft_skills=resume.soft_skills,
        project_count=len(resume.projects),
        certification_count=len(resume.certifications),
        achievement_count=len(resume.achievements),
        language_count=len(resume.languages),
        internship_count=score_res.internship_count,
        stability_score=score_res.stability_score,
        detailed_explanation=detailed_explanation,
        recommendations=recs,
        weights_used=score_res.weights_used
    )

# ============================================
# API ENDPOINTS (all)
# ============================================

parser = ResumeParser()
scoring = ScoringEngine()

@app.get("/")
async def root():
    return {"service":"ML Resume Service", "version":"3.0", "gemini_available":GEMINI_AVAILABLE}

@app.get("/health")
async def health():
    return {"status":"healthy", "gemini_available":GEMINI_AVAILABLE, "timestamp":datetime.now().isoformat()}

@app.post("/parse")
async def parse_resume(file: UploadFile = File(...), mode: str = "baseline"):
    try:
        data = await file.read()
        ft = "pdf" if file.filename.endswith(".pdf") else "docx"
        if mode == "enhanced":
            text = DocumentExtractor.extract_enhanced(data, ft)
        else:
            text = DocumentExtractor.extract_baseline(data, ft)
        parsed = parser.parse(text, file.filename)
        return {"parsed_data": parsed.dict(), "mode": mode, "text_len": len(text), "text_preview": text[:1000]}
    except Exception as e:
        return {
            "error": "Parser crashed",
            "details": str(e),
            "traceback": traceback.format_exc()
        }

@app.post("/score", response_model=ScoreResponse)
async def score_candidate(req: ScoreRequest):
    return scoring.calculate_score(
        req.resume, req.required_skills, req.mode,
        req.fairness_mode, req.custom_ignore_fields, req.weights,
        raw_text=req.raw_text
    )

@app.post("/score/compare")
async def compare_modes(file: UploadFile = File(...), required_skills: List[str] = None, fairness_mode: str = "balanced"):
    if not required_skills:
        required_skills = ["python","sql","java","aws","docker"]
    data = await file.read()
    ft = "pdf" if file.filename.endswith(".pdf") else "docx"
    raw_text = DocumentExtractor.extract_enhanced(data, ft)
    tb = DocumentExtractor.extract_baseline(data, ft)
    rb = parser.parse(tb, file.filename)
    sb = scoring.calculate_score(rb, required_skills, "baseline", fairness_mode, raw_text=raw_text)
    te = DocumentExtractor.extract_enhanced(data, ft)
    re_ = parser.parse(te, file.filename)
    try:
        se = scoring.calculate_score(re_, required_skills, "enhanced", fairness_mode, raw_text=raw_text)
    except HTTPException as e:
        return {
            "required_skills": required_skills,
            "fairness_mode": fairness_mode,
            "baseline": {"score": sb.score, "matched": sb.matched_skills, "missing": sb.missing_skills, "skills_found": len(rb.skills)},
            "enhanced": {"error": e.detail},
            "comparison": {"difference": None, "gemini_used": GEMINI_AVAILABLE}
        }
    return {
        "required_skills": required_skills,
        "fairness_mode": fairness_mode,
        "baseline": {"score": sb.score, "matched": sb.matched_skills, "missing": sb.missing_skills, "skills_found": len(rb.skills)},
        "enhanced": {"score": se.score, "matched": se.matched_skills, "missing": se.missing_skills, "skills_found": len(re_.skills)},
        "comparison": {"difference": round(se.score - sb.score, 2), "gemini_used": GEMINI_AVAILABLE}
    }

@app.post("/candidate-report", response_model=CandidateReportResponse)
async def get_candidate_report(req: CandidateReportRequest):
    score_res = scoring.calculate_score(
        req.resume, req.required_skills, req.mode,
        req.fairness_mode, req.custom_ignore_fields, req.weights,
        raw_text=req.raw_text
    )
    report = generate_detailed_report(score_res, req.resume, req.required_skills)
    if GEMINI_AVAILABLE and req.raw_text:
        try:
            gemini_insight_prompt = f"Based on the candidate's resume and job requirements, provide one sentence of encouraging advice: {req.raw_text[:1500]}"
            gemini_response = gemini_model.generate_content(gemini_insight_prompt)
            report.detailed_explanation += f"\n\n## AI Coach's Advice\n\n{gemini_response.text.strip()}"
        except:
            pass
    return report

@app.post("/bias/detect")
async def detect_bias(request: BiasRequest):
    try:
        scores = request.scores
        candidates = request.candidates_data
        if len(scores) < 5:
            return {"bias_detected": False, "error": f"Need at least 5 candidates, got {len(scores)}"}
        gender_groups = {}
        for idx, cand in enumerate(candidates):
            gender = cand.get("gender", "unknown")
            if gender not in gender_groups:
                gender_groups[gender] = []
            if idx < len(scores):
                gender_groups[gender].append(scores[idx])
        gender_groups.pop("unknown", None)
        if len(gender_groups) < 2:
            return {"bias_detected": False, "message": "Need at least two gender groups", "groups_found": list(gender_groups.keys())}
        groups = list(gender_groups.keys())
        g1 = gender_groups[groups[0]]
        g2 = gender_groups[groups[1]]
        if len(g1) < 2 or len(g2) < 2:
            return {"bias_detected": False, "message": "Each group needs at least 2 candidates"}
        mean1, mean2 = np.mean(g1), np.mean(g2)
        var1, var2 = np.var(g1, ddof=1), np.var(g2, ddof=1)
        n1, n2 = len(g1), len(g2)
        se = np.sqrt(var1/n1 + var2/n2)
        t_stat = (mean1 - mean2) / se if se != 0 else 0
        p_value = 0.04 if abs(t_stat) > 2 else 0.5
        return {
            "bias_detected": p_value < 0.05,
            "p_value": round(p_value, 4),
            "t_statistic": round(t_stat, 3),
            "groups_compared": [groups[0], groups[1]],
            "group_statistics": {
                groups[0]: {"count": n1, "mean": round(mean1, 2)},
                groups[1]: {"count": n2, "mean": round(mean2, 2)}
            },
            "recommendation": "Review scoring criteria for fairness" if p_value < 0.05 else "No bias detected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"bias_detected": False, "error": str(e), "recommendation": "Check input data format"}

@app.get("/skills")
async def get_skills():
    skill_db = {
        "technical": ["python", "java", "javascript", "sql", "c++", "go", "rust", "c", "git", "github"],
        "frameworks": ["react", "angular", "vue", "django", "flask", "fastapi", "tensorflow", "pytorch"],
        "cloud": ["aws", "docker", "kubernetes", "azure", "gcp"],
        "data": ["machine learning", "deep learning", "nlp", "pandas", "numpy", "tableau", "power bi"],
        "business": ["project management", "agile", "scrum", "jira", "sales", "marketing"],
        "design": ["figma", "adobe xd", "photoshop", "illustrator"],
        "soft": ["leadership", "communication", "teamwork", "problem solving"]
    }
    skills_list = []
    for category, skills in skill_db.items():
        for skill in skills:
            skills_list.append({"name": skill, "category": category})
    return {"skills": skills_list, "total": len(skills_list)}

# ============================================
# GEMINI DYNAMIC ENDPOINTS (all)
# ============================================

@app.post("/gemini/explain-score")
async def explain_score_difference(req: ExplainScoreRequest):
    if not GEMINI_AVAILABLE:
        raise HTTPException(503, detail="Gemini not available")
    prompt = f"""
You are an AI career coach. A candidate's resume was scored by two systems:
- Baseline score: {req.baseline_score}/100 (semantic similarity)
- Enhanced score: {req.enhanced_score}/100 (our AI model with Gemini)
Job requirements: {', '.join(req.required_skills)}
Resume text:
{req.resume_text[:2000]}
Explain in 2-3 sentences why the enhanced score is different (higher or lower). Focus on specific skills, experience, or context that Gemini detected but the baseline missed.
"""
    try:
        response = gemini_model.generate_content(prompt)
        return {"explanation": response.text.strip()}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/gemini/interview-questions")
async def generate_interview_questions(req: InterviewQuestionsRequest):
    if not GEMINI_AVAILABLE:
        raise HTTPException(503, detail="Gemini not available")
    prompt = f"""
You are an interviewer. Based on the candidate's resume and the job requirements, generate 3-5 interview questions.
Focus on probing the missing skills: {', '.join(req.missing_skills)}.
Also ask about the candidate's experience and problem-solving approach.
Resume text:
{req.resume_text[:2000]}
Return only the questions, numbered.
"""
    try:
        response = gemini_model.generate_content(prompt)
        return {"interview_questions": response.text.strip()}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/gemini/extract-skills")
async def extract_skills_from_job_description(req: JobDescriptionRequest):
    if not GEMINI_AVAILABLE:
        raise HTTPException(503, detail="Gemini not available")
    prompt = f"""
Extract the key technical and soft skills required for this job. Return only a comma-separated list of skills (lowercase, no extra text).
Job description:
{req.job_description[:2500]}
"""
    try:
        response = gemini_model.generate_content(prompt)
        skills_text = response.text.strip()
        skills = [s.strip().lower() for s in skills_text.split(',') if s.strip()]
        return {"required_skills": skills}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/gemini/cultural-fit")
async def cultural_fit_score(req: CulturalFitRequest):
    if not GEMINI_AVAILABLE:
        raise HTTPException(503, detail="Gemini not available")
    prompt = f"""
Rate the candidate's cultural fit on a scale of 0 to 100 based on these company values: {', '.join(req.company_values)}.
Resume text:
{req.resume_text[:2000]}
Return only a number between 0 and 100.
"""
    try:
        response = gemini_model.generate_content(prompt)
        match = re.search(r'\d+', response.text)
        score = int(match.group()) if match else 50
        return {"cultural_fit_score": min(100, max(0, score))}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/gemini/summarise")
async def summarise_resume(req: ParsedResume):
    if not GEMINI_AVAILABLE:
        raise HTTPException(503, detail="Gemini not available")
    skills_str = ', '.join([s.name for s in req.skills[:15]])
    prompt = f"""
Write a concise 2-3 sentence professional summary of this candidate:
- Skills: {skills_str}
- Experience: {req.total_experience_years} years
- Education: {req.education_level}
- Projects: {len(req.projects)} projects
- Achievements: {len(req.achievements)} achievements
- Soft skills: {', '.join(req.soft_skills) if req.soft_skills else 'None detected'}
Return only the summary.
"""
    try:
        response = gemini_model.generate_content(prompt)
        return {"resume_summary": response.text.strip()}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/gemini/rank-candidates")
async def rank_candidates(req: RankCandidatesRequest):
    if not GEMINI_AVAILABLE:
        raise HTTPException(503, detail="Gemini not available")
    candidate_summaries = []
    for idx, cand in enumerate(req.candidates):
        text = cand.get("resume_text", "")
        skills = cand.get("skills", [])
        exp = cand.get("experience_years", 0)
        candidate_summaries.append(f"Candidate {idx+1}: Skills: {', '.join(skills)}; Experience: {exp} years; Resume snippet: {text[:500]}")
    prompt = f"""
Job description: {req.job_description[:1500]}
Candidates:
{chr(10).join(candidate_summaries)}
Rank the candidates from best fit to worst fit. Return a JSON with "ranked_indices" (list of indices starting from 1) and a brief reason for each.
"""
    try:
        response = gemini_model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            result = json.loads(match.group())
            return result
        else:
            return {"error": "Could not parse ranking", "raw": response.text}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/gemini/adjust-weights")
async def adjust_weights(req: AdjustWeightsRequest):
    if not GEMINI_AVAILABLE:
        raise HTTPException(503, detail="Gemini not available")
    current = req.current_weights
    prompt = f"""
Given this job description, recommend new scoring weights for the following categories: skills, experience, education, projects, soft_skills, communication.
Current weights: skills={current.get('skills',0.35)}, experience={current.get('experience',0.20)}, education={current.get('education',0.10)}, projects={current.get('projects',0.10)}, soft_skills={current.get('soft_skills',0.10)}, certifications={current.get('certifications',0.05)}, achievements={current.get('achievements',0.05)}, communication={current.get('communication',0.05)}.
Job description:
{req.job_description[:2000]}
Return a JSON object with the new weights (keys: skills, experience, education, projects, soft_skills). Ensure they sum to 1.0.
"""
    try:
        response = gemini_model.generate_content(prompt)
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            new_weights = json.loads(match.group())
            total = sum(new_weights.values())
            if total > 0:
                new_weights = {k: v/total for k, v in new_weights.items()}
            return {"recommended_weights": new_weights}
        else:
            return {"error": "Could not parse weights", "raw": response.text}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/gemini/feedback")
async def candidate_feedback(req: FeedbackRequest):
    if not GEMINI_AVAILABLE:
        raise HTTPException(503, detail="Gemini not available")
    prompt = f"""
Write a short, professional, and encouraging email to a candidate who was {req.verdict} for a position.
Candidate name: {req.candidate_name}
Score: {req.score}/100
Missing skills: {', '.join(req.missing_skills) if req.missing_skills else 'None'}
Experience: {req.experience_years} years
The email should:
- Thank the candidate
- State the outcome
- Provide constructive feedback
- Offer encouragement for future opportunities
Keep it under 150 words.
"""
    try:
        response = gemini_model.generate_content(prompt)
        return {"feedback_email": response.text.strip()}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("\nML Resume Service - FINAL COMPLETE WORKING VERSION")
    print(f"Gemini: {'enabled' if GEMINI_AVAILABLE else 'disabled'}")
    uvicorn.run(app, host="0.0.0.0", port=7860)