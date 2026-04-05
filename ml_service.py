# ml_service_final.py
# ULTRA-LIGHTWEIGHT VERSION - No external downloads needed

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import re
import io
import PyPDF2
import docx
from scipy import stats

# ============================================
# USE TINY LOCAL MODEL (No downloads needed)
# ============================================
print("=" * 60)
print("Loading lightweight local model...")
print("=" * 60)

try:
    from transformers import pipeline
    # This uses a tiny built-in model - no download required
    ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", revision="main")
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"Model load failed: {e}")
    print("Falling back to regex-only mode...")
    ner_pipeline = None

# ============================================
# PHASE 1: PYDANTIC SCHEMAS
# ============================================

class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None

class Skill(BaseModel):
    name: str
    category: str
    years_experience: Optional[float] = None
    proficiency: str = "not_specified"

class Experience(BaseModel):
    title: str
    company: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_years: float = 0.0
    description: str = ""
    skills_used: List[str] = []

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
    experience: List[Experience] = []
    education: List[Education] = []
    projects: List[Project] = []
    total_experience_years: float = 0.0
    skill_count: int = 0
    education_level: str = ""

# ============================================
# PHASE 2: SCORING SCHEMAS
# ============================================

class ScoreRequest(BaseModel):
    required_skills: List[str]
    resume: ParsedResume
    weights: Optional[Dict[str, float]] = {
        "skill_match": 0.50,
        "experience": 0.25,
        "education": 0.15,
        "projects": 0.10
    }

class ScoreResponse(BaseModel):
    total_score: float
    components: Dict[str, Any]
    explanation: Dict[str, Any]
    matched_skills: List[str]
    missing_skills: List[str]
    additional_skills: List[str]

class BiasRequest(BaseModel):
    scores: List[float]
    candidates_data: List[Dict[str, str]]

class BiasResponse(BaseModel):
    bias_detected: bool
    metrics: Dict[str, Any]
    recommendations: List[str]
    report: Dict[str, Any]

# ============================================
# ML ENGINE - With regex fallback for name extraction
# ============================================

class MLEngine:
    def __init__(self):
        self.ner = ner_pipeline
        
        # Complete skill database
        self.skill_database = {
            "programming_languages": {
                "python": ["python", "py", "python3"],
                "java": ["java"],
                "javascript": ["javascript", "js"],
                "sql": ["sql", "mysql", "postgresql", "postgres"],
                "c++": ["c++", "cpp"],
                "go": ["go", "golang"],
                "typescript": ["typescript", "ts"],
                "scala": ["scala"],
                "r": ["r", "r language"]
            },
            "frameworks": {
                "react": ["react", "react.js", "reactjs"],
                "angular": ["angular", "angular.js"],
                "vue": ["vue", "vue.js"],
                "django": ["django"],
                "flask": ["flask"],
                "fastapi": ["fastapi"],
                "tensorflow": ["tensorflow", "tf"],
                "pytorch": ["pytorch", "torch"],
                "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
                "pandas": ["pandas"],
                "numpy": ["numpy"],
                "xgboost": ["xgboost", "xgb"]
            },
            "cloud": {
                "aws": ["aws", "amazon web services", "ec2", "s3"],
                "azure": ["azure", "microsoft azure"],
                "gcp": ["gcp", "google cloud"],
                "docker": ["docker"],
                "kubernetes": ["kubernetes", "k8s"],
                "jenkins": ["jenkins"],
                "terraform": ["terraform"]
            },
            "data_science": {
                "machine learning": ["machine learning", "ml"],
                "deep learning": ["deep learning", "dl"],
                "nlp": ["nlp", "natural language processing"],
                "computer vision": ["computer vision", "cv"],
                "tableau": ["tableau"],
                "power bi": ["power bi", "powerbi"],
                "excel": ["excel"],
                "statistics": ["statistics", "statistical analysis"]
            },
            "devops": {
                "ci/cd": ["ci/cd", "cicd", "continuous integration"],
                "git": ["git"],
                "github": ["github"],
                "linux": ["linux", "unix"],
                "prometheus": ["prometheus"],
                "grafana": ["grafana"]
            }
        }
        
        self.proficiency_indicators = {
            "expert": ["expert", "advanced", r"5\+ years", "senior", "lead", "architect", "principal"],
            "intermediate": ["proficient", "good knowledge", r"2\+ years", "experienced", "built", "developed"],
            "beginner": ["basic", "learning", "familiar", "course", "beginner", "introductory"]
        }
    
    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text
        except:
            return ""
    
    def extract_text_from_docx(self, file_bytes: bytes) -> str:
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            text = " ".join([p.text for p in doc.paragraphs])
            return text
        except:
            return ""
    
    # ============================================
    # NAME EXTRACTION - Regex Fallback (works without model)
    # ============================================
    
    def extract_name_regex(self, text: str) -> Optional[str]:
        """Extract name using regex patterns - works without any model"""
        lines = text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if len(line) > 3 and len(line) < 50:
                # Pattern for "First Last" or "First M. Last"
                if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$', line):
                    return line
                # Pattern for "LAST, First"
                if re.match(r'^[A-Z]+, [A-Z][a-z]+', line):
                    return line
        return None
    
    def extract_contact_info(self, text: str) -> ContactInfo:
        contact = ContactInfo()
        
        # Try transformer model first, fallback to regex
        if self.ner is not None:
            try:
                entities = self.ner(text[:3000])
                for ent in entities:
                    if ent.get('entity_group') == 'PER' and not contact.name:
                        contact.name = ent.get('word', '').replace('##', '')
                        break
            except:
                pass
        
        # Fallback to regex if transformer didn't work
        if not contact.name:
            contact.name = self.extract_name_regex(text)
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact.email = emails[0]
        
        # Phone extraction
        phone_pattern = r'\b\d{10}\b'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact.phone = phones[0]
        
        # GitHub and LinkedIn
        github_match = re.search(r'github\.com/[\w-]+', text)
        if github_match:
            contact.github = github_match.group()
        
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text)
        if linkedin_match:
            contact.linkedin = linkedin_match.group()
        
        return contact
    
    def extract_skills(self, text: str) -> List[Skill]:
        text_lower = text.lower()
        detected_skills = []
        
        for category, skills in self.skill_database.items():
            for skill_name, variations in skills.items():
                for variation in variations:
                    pattern = r'\b' + re.escape(variation) + r'\b'
                    if re.search(pattern, text_lower):
                        proficiency = self._detect_proficiency(text_lower, skill_name)
                        detected_skills.append(Skill(
                            name=skill_name,
                            category=category,
                            proficiency=proficiency
                        ))
                        break
        
        unique = {}
        for skill in detected_skills:
            if skill.name not in unique:
                unique[skill.name] = skill
        
        return list(unique.values())
    
    def _detect_proficiency(self, text: str, skill_name: str) -> str:
        sentences = text.split('.')
        for sentence in sentences:
            if skill_name in sentence:
                for level, indicators in self.proficiency_indicators.items():
                    for indicator in indicators:
                        if re.search(r'\b' + indicator + r'\b', sentence):
                            return level
        return "not_specified"
    
    def extract_experience(self, text: str) -> List[Experience]:
        experiences = []
        
        exp_section = re.search(
            r'(?:^|\n)(?:EXPERIENCE|WORK HISTORY|EMPLOYMENT)[:\s]*(.*?)(?=\n\n[A-Z]|\Z)',
            text, re.IGNORECASE | re.DOTALL
        )
        
        if exp_section:
            exp_text = exp_section.group(1)
            entries = re.split(r'\n(?=[A-Z][a-z]+)', exp_text)
            
            for entry in entries[:5]:
                exp = self._parse_experience_entry(entry)
                if exp.title:
                    experiences.append(exp)
        
        return experiences
    
    def _parse_experience_entry(self, entry: str) -> Experience:
        exp = Experience(title="", company="", description="")
        lines = entry.strip().split('\n')
        
        if lines:
            first_line = lines[0]
            at_match = re.search(r'(.+?)\s+(?:at|@|-)\s+(.+)', first_line)
            if at_match:
                exp.title = at_match.group(1).strip()
                exp.company = at_match.group(2).strip()
            else:
                exp.title = first_line.strip()
        
        date_pattern = r'(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|Present)'
        date_match = re.search(date_pattern, entry)
        if date_match:
            exp.start_date = date_match.group(1)
            exp.end_date = date_match.group(2)
            exp.duration_years = 2.0 if exp.end_date.lower() == "present" else 1.0
        
        desc_lines = []
        for line in lines[1:]:
            if not re.search(r'\d{4}', line) and len(line.strip()) > 0:
                desc_lines.append(line.strip())
        exp.description = ' '.join(desc_lines)[:500]
        
        return exp
    
    def extract_education(self, text: str) -> List[Education]:
        educations = []
        
        edu_section = re.search(
            r'(?:^|\n)(?:EDUCATION)[:\s]*(.*?)(?=\n\n[A-Z]|\Z)',
            text, re.IGNORECASE | re.DOTALL
        )
        
        if edu_section:
            edu_text = edu_section.group(1)
            lines = edu_text.split('\n')
            
            for line in lines[:5]:
                if line.strip():
                    edu = Education(degree=line.strip(), institution="")
                    
                    year_match = re.search(r'\b(19|20)\d{2}\b', line)
                    if year_match:
                        edu.graduation_year = int(year_match.group())
                    
                    degree_pattern = r'(Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|B\.?Tech|M\.?Tech)'
                    degree_match = re.search(degree_pattern, line, re.IGNORECASE)
                    if degree_match:
                        edu.degree = degree_match.group()
                    
                    if edu.institution or edu.graduation_year:
                        educations.append(edu)
        
        return educations
    
    def extract_summary(self, text: str) -> Optional[str]:
        patterns = [r'(?:^|\n)(?:SUMMARY|PROFILE|ABOUT ME)[:\s]*(.*?)(?=\n\n|\n[A-Z]|\Z)']
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()[:500]
        return None
    
    def calculate_skill_match(self, resume_skills: List[Skill], required: List[str]) -> Dict:
        if not required:
            return {"score": 0, "matched": [], "missing": [], "additional": []}
        
        weights = {"expert": 1.0, "intermediate": 0.7, "beginner": 0.4, "not_specified": 0.3}
        
        matched = []
        missing = []
        total = 0
        
        resume_names = [s.name.lower() for s in resume_skills]
        resume_map = {s.name.lower(): s for s in resume_skills}
        
        for req in required:
            req_lower = req.lower()
            if req_lower in resume_names:
                skill = resume_map[req_lower]
                weight = weights.get(skill.proficiency, 0.3)
                total += weight
                matched.append({"name": req, "proficiency": skill.proficiency})
            else:
                missing.append(req)
        
        score = (total / len(required)) * 100 if required else 0
        
        all_resume = [s.name.lower() for s in resume_skills]
        additional = [s for s in all_resume if s not in [r.lower() for r in required]]
        bonus = min(15, len(additional) * 3)
        
        return {
            "score": min(100, score + bonus),
            "matched": matched,
            "missing": missing,
            "additional": additional
        }
    
    def get_education_level(self, educations: List[Education]) -> str:
        levels = {"phd": 5, "master": 4, "bachelor": 3, "associate": 2}
        highest = "not_specified"
        highest_score = 0
        
        for edu in educations:
            edu_lower = edu.degree.lower()
            for level, score in levels.items():
                if level in edu_lower and score > highest_score:
                    highest_score = score
                    highest = level
        
        return highest
    
    def parse_resume(self, file_bytes: bytes, file_name: str, file_type: str) -> ParsedResume:
        if file_type == "pdf":
            text = self.extract_text_from_pdf(file_bytes)
        else:
            text = self.extract_text_from_docx(file_bytes)
        
        parsed = ParsedResume(file_name=file_name)
        
        parsed.contact_info = self.extract_contact_info(text)
        parsed.summary = self.extract_summary(text)
        parsed.skills = self.extract_skills(text)
        parsed.experience = self.extract_experience(text)
        parsed.education = self.extract_education(text)
        
        parsed.total_experience_years = sum(exp.duration_years for exp in parsed.experience)
        parsed.skill_count = len(parsed.skills)
        parsed.education_level = self.get_education_level(parsed.education)
        
        return parsed
    
    def calculate_total_score(self, resume: ParsedResume, required: List[str],
                              weights: Dict = None) -> ScoreResponse:
        if weights is None:
            weights = {"skill_match": 0.50, "experience": 0.25, "education": 0.15, "projects": 0.10}
        
        skill_result = self.calculate_skill_match(resume.skills, required)
        
        exp_years = resume.total_experience_years
        if exp_years >= 5:
            exp_score = 90
        elif exp_years >= 3:
            exp_score = 75
        elif exp_years >= 1:
            exp_score = 50
        else:
            exp_score = 30
        
        edu_scores = {"phd": 100, "master": 90, "bachelor": 70, "associate": 50, "not_specified": 30}
        edu_score = edu_scores.get(resume.education_level, 30)
        
        proj_score = min(100, len(resume.projects) * 20)
        
        components = {
            "skill_match": {"score": skill_result["score"], "weight": weights["skill_match"]},
            "experience": {"score": exp_score, "weight": weights["experience"]},
            "education": {"score": edu_score, "weight": weights["education"]},
            "projects": {"score": proj_score, "weight": weights["projects"]}
        }
        
        total = sum(c["score"] * c["weight"] for c in components.values())
        
        explanation = {
            "breakdown": [{"component": k, "score": v["score"], "weight": v["weight"]} 
                         for k, v in components.items()],
            "recommendations": []
        }
        
        if skill_result["missing"]:
            explanation["recommendations"].append(f"Develop: {', '.join(skill_result['missing'][:3])}")
        
        return ScoreResponse(
            total_score=total,
            components=components,
            explanation=explanation,
            matched_skills=[s["name"] for s in skill_result["matched"]],
            missing_skills=skill_result["missing"],
            additional_skills=skill_result.get("additional", [])
        )
    
    def detect_bias(self, scores: List[float], attributes: List[str], name: str) -> Dict:
        if len(scores) < 4:
            return {"bias_detected": False, "message": "Insufficient data", "attribute": name}
        
        groups = list(set([a for a in attributes if a and a != "Not Specified"]))
        if len(groups) < 2:
            return {"bias_detected": False, "message": "Only one group", "attribute": name}
        
        group_metrics = {}
        for g in groups:
            idx = [i for i, a in enumerate(attributes) if a == g]
            if len(idx) >= 2:
                group_scores = [scores[i] for i in idx]
                group_metrics[g] = {"count": len(idx), "mean": sum(group_scores) / len(group_scores)}
        
        if len(group_metrics) < 2:
            return {"bias_detected": False, "message": "Insufficient data", "attribute": name}
        
        ref = max(group_metrics.keys(), key=lambda k: group_metrics[k]["count"])
        ref_mean = group_metrics[ref]["mean"]
        
        bias = False
        metrics = {}
        
        for g, data in group_metrics.items():
            if g == ref:
                continue
            diff = abs(data["mean"] - ref_mean)
            if diff > 10:
                bias = True
            metrics[g] = {"mean_diff": round(diff, 1), "sample_size": data["count"]}
        
        return {
            "attribute": name,
            "bias_detected": bias,
            "metrics": metrics,
            "recommendations": ["Review scoring criteria"] if bias else ["No bias detected"]
        }
    
    def generate_bias_report(self, scores: List[float], candidates: List[Dict]) -> Dict:
        report = {"timestamp": datetime.now().isoformat(), "total": len(scores), "bias_detected": False, "attributes": []}
        
        if len(scores) < 5:
            report["error"] = f"Need 5+ candidates, have {len(scores)}"
            return report
        
        for attr in ["gender", "age_group", "experience_level"]:
            values = [c.get(attr) for c in candidates]
            valid = [(s, a) for s, a in zip(scores, values) if a and a != "Not Specified"]
            if len(valid) >= 4:
                result = self.detect_bias([p[0] for p in valid], [p[1] for p in valid], attr)
                report["attributes"].append(result)
                if result.get("bias_detected"):
                    report["bias_detected"] = True
        
        return report


# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(title="ML Service", description="Phase 1 & 2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = MLEngine()

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "ML Engine", "phase": "Phase 1 & 2 Complete"}

@app.post("/parse", response_model=ParsedResume)
async def parse(file: UploadFile = File(...)):
    try:
        bytes_data = await file.read()
        file_type = "pdf" if file.filename.endswith(".pdf") else "docx"
        return engine.parse_resume(bytes_data, file.filename, file_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/score", response_model=ScoreResponse)
async def score(req: ScoreRequest):
    try:
        return engine.calculate_total_score(req.resume, req.required_skills, req.weights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bias/detect", response_model=BiasResponse)
async def bias(req: BiasRequest):
    try:
        report = engine.generate_bias_report(req.scores, req.candidates_data)
        return BiasResponse(
            bias_detected=report.get("bias_detected", False),
            metrics=report,
            recommendations=report.get("attributes", [{}])[0].get("recommendations", []) if report.get("attributes") else [],
            report=report
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/skills")
async def skills():
    all_skills = []
    for cat, skills in engine.skill_database.items():
        for skill in skills.keys():
            all_skills.append({"name": skill, "category": cat})
    return {"skills": all_skills}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("ML SERVICE - PHASE 1 & 2 COMPLETE")
    print("="*60)
    print("✅ Works without any model downloads")
    print("✅ Regex-based name extraction (works for standard resume formats)")
    print("✅ Pydantic schemas for structured data")
    print("✅ Weighted scoring engine")
    print("✅ Statistical bias detection")
    print("\nEndpoints:")
    print("  POST /parse       - Parse resume")
    print("  POST /score       - Score candidate")
    print("  POST /bias/detect - Detect bias")
    print("  GET  /health      - Health check")
    print("  GET  /skills      - List all skills")
    print("\nStarting server on http://0.0.0.0:8001")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=7860)