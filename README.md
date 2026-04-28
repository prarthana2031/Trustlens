# TrustLens – Fairness AI Recruitment Platform

**AI-Powered Resume Screening with Bias Detection, Fairness Monitoring & Explainable Decisions**

TrustLens is an end-to-end platform that detects, measures, and mitigates unconscious bias in AI-powered hiring. It combines resume parsing, intelligent scoring, statistical fairness metrics, active debiasing, and complete audit trails – all delivered through a modern React frontend, FastAPI backend, and dedicated ML microservice.

---

## 🎯 Problem & Solution

| Problem | TrustLens Solution |
|---------|-------------------|
| Gender/ethnicity bias in scoring | Demographic parity adjustment, equal opportunity monitoring, disparate impact (80% rule) |
| Name/location discrimination | Blind screening with configurable redaction (strict/balanced/maximum) |
| Opaque AI decisions | Explainable reports (strengths, gaps, experience, stability, AI coach advice) |
| No fairness metrics | Statistical t-test on groups, group means, p-values, recommendations |
| Compliance risk | Complete audit logging for all screening decisions |
| Scanned/image resumes | OCR fallback (OCR.space + Tesseract) |

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Clients                                       │
│                    (Web App, Mobile, ATS Integrations)                      │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ HTTP/JSON
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                         React Frontend (Vite + Tailwind)                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐  │
│  │   Upload     │ │  Dashboard   │ │  Analytics   │ │   Auth (Firebase)  │  │
│  │ (Single/Batch)│ │ (Candidates) │ │(Bias Reports)│ │    (JWT Tokens)    │  │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ HTTPS / JSON
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                         FastAPI Backend (Google Cloud Run)                  │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────────────────────────┐   │
│  │   Auth      │ │    API       │ │           Middleware                 │   │
│  │ (Firebase)  │ │  (v1 Router) │ │ (Audit, CORS, Rate Limit, TrustHost) │   │
│  └─────────────┘ └──────────────┘ └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Business Logic Layer                           │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌────────────────────────────┐  │   │
│  │  │  Screening   │ │   Upload     │ │      Bias Analysis         │  │   │
│  │  │ Orchestrator │ │ Orchestrator │ │      Orchestrator           │  │   │
│  │  └──────┬───────┘ └──────┬───────┘ └─────────────┬──────────────┘  │   │
│  │         └────────────────┼───────────────────────┘                 │   │
│  │  ┌───────────────────────▼───────────────────────────────────────┐ │   │
│  │  │                      Service Layer                             │ │   │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │ │   │
│  │  │  │  ML Client   │  │  Debiasing   │  │     Storage        │   │ │   │
│  │  │  │ (HF/Gemini)  │  │   Service    │  │  Service (Supabase) │   │ │   │
│  │  │  └──────────────┘  └──────────────┘  └────────────────────┘   │ │   │
│  │  └────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │ Internal API Calls
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                    ML Service (Hugging Face Spaces)                         │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │   /parse    │ │    /score    │ │  /bias/      │ │   /gemini/*        │   │
│  │ (Resume +   │ │ (Baseline /  │ │  detect      │ │ (Explain, Q&A,     │   │
│  │  OCR)       │ │  Enhanced)   │ │ (t-test)     │ │  Rank, Summarise)  │   │
│  └─────────────┘ └──────────────┘ └──────────────┘ └────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │   │
│  │  │Sentence-BERT│  │   Gemini   │  │  OCR.space │  │  Tesseract   │  │   │
│  │  │ (Baseline) │  │ (Enhanced) │  │  (Cloud)   │  │   (Local)    │  │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                              Data Layer                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────────────┐   │
│  │  PostgreSQL  │  │    Redis     │  │           Supabase              │   │
│  │ (Candidates, │  │   (Cache)    │  │  (Resume Storage + Metadata)     │   │
│  │  Scores,     │  │              │  │                                 │   │
│  │ BiasMetrics) │  │              │  │                                 │   │
│  └──────────────┘  └──────────────┘  └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘

**Deployment status:**
- Frontend + Backend → Google Cloud Run
- ML Service → Hugging Face Spaces (`https://preeee-276-ml-service-api.hf.space`)

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+, Node.js 18+
- PostgreSQL 14+ (or Supabase), Redis (optional)
- Tesseract OCR (optional, for local OCR)

### Backend Setup
```bash
cd TrustLens/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit with your credentials
alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000

cd trustlens-frontend
npm install
cp .env.example .env   # set VITE_API_BASE_URL
npm run dev            # → http://localhost:5173
cd ml-service-api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="your_key"
python ml_service.py   # → http://localhost:7860

cd ml-service-api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="your_key"
python ml_service.py   # → http://localhost:7860
VITE_API_BASE_URL=https://resume-backend-948277799081.us-central1.run.app
GEMINI_API_KEY=your_google_ai_key   # optional, enables enhanced endpoints

Backend Endpoints (FastAPI – Port 8000)
Method	Endpoint	Description	Auth
GET	/health, /ready	Health checks	No
POST	/api/v1/upload	Upload resume (PDF/DOCX)	Yes
GET/POST	/api/v1/candidates	List/create candidates	Yes
POST	/api/v1/screening	Batch screening	Yes
POST	/api/v1/bias/analyze	Fairness analysis	Yes
POST	/api/v1/candidates/{id}/enhance	AI-enhanced scoring	Yes

ML Service Endpoints (Hugging Face – Port 7860)
Method	Endpoint	Description
POST	/parse	Extract structured data from resume
POST	/score	Baseline or enhanced scoring
POST	/score/compare	Baseline vs enhanced
POST	/candidate-report	Human-readable report
POST	/bias/detect	Statistical t-test across candidates
POST	/gemini/explain-score	Explain baseline/enhanced difference
POST	/gemini/interview-questions	Personalised questions
POST	/gemini/extract-skills	Job description → skills
POST	/gemini/rank-candidates	Rank candidates for a role

⚖️ Fairness Metrics & Debiasing
Demographic Parity Ratio
text
ratio = min(group_mean_scores) / max(group_mean_scores)
Threshold: 0.8 (80% rule – EEOC standard)

Equal Opportunity Difference
text
diff = max(TPR_groups) - min(TPR_groups)   # TPR = True Positive Rate
Disparate Impact
text
impact = group_selection_rate / max_selection_rate
Active Debiasing Methods
Demographic parity adjustment – algorithmic score reweighting

Blind resume processing – remove name, email, address, university (configurable levels)

Recommendations engine – suggests mitigation actions

🧪 Testing
bash
# Backend
pytest                                          # all tests
pytest app/tests/test_api/test_bias.py -v      # bias tests
pytest --cov=app --cov-report=html

# Frontend
npm run test        # if configured
☁️ Deployment
Docker (Backend)
bash
docker build -t trustlens-backend .
docker run -p 8080:8080 -e DATABASE_URL=... -e FIREBASE_KEY='{...}' trustlens-backend
Google Cloud Run (Backend)
bash
gcloud run deploy trustlens-backend --source . --region us-central1 --platform managed \
  --allow-unauthenticated \
  --set-env-vars "DATABASE_URL=...,FIREBASE_KEY=secret"
Frontend (Production Build)
bash
cd trustlens-frontend
npm run build        # output in dist/
# Deploy dist/ to any static hosting (Firebase Hosting, Cloud Run Nginx, etc.)
ML Service (Hugging Face Spaces)
Already deployed: https://preeee-276-ml-service-api.hf.space
Update by pushing to the Hugging Face Space repository.

📂 Project Structure
TrustLens/
├── backend/                     # FastAPI backend (Cloud Run)
│   ├── app/
│   │   ├── api/v1/endpoints/    # Routes
│   │   ├── core/                # Config, DB, logging
│   │   ├── middlewares/         # Audit, CORS, rate limiting
│   │   ├── orchestrators/       # Screening, upload, bias
│   │   ├── services/            # ML client, debiasing, storage
│   │   └── tests/
│   ├── migrations/              # Alembic
│   └── Dockerfile
├── trustlens-frontend/          # React frontend
│   ├── src/
│   │   ├── components/          # Reusable UI
│   │   ├── pages/               # Upload, dashboard, reports
│   │   ├── services/api.ts      # API client (proxy + direct)
│   │   └── types/
│   └── vite.config.ts           # Proxy config to backend
└── ml-service-api/              # ML microservice (Hugging Face)
    ├── ml_service.py            # Main FastAPI app
    ├── requirements.txt
    └── Dockerfile

🔒 Security & Compliance
JWT authentication (Firebase) – all API endpoints protected except health/readiness

CORS whitelist – configurable origins

Audit logging – complete request/response logs for compliance (JSON format)

Input validation – file type/size, magic bytes check

SQL injection protection – SQLAlchemy parameterised queries

Host header protection – TrustedHostMiddleware

📄 License
MIT License – see LICENSE file.

🙏 Acknowledgments
FastAPI, SQLAlchemy, Alembic

React, Vite, Tailwind CSS, React Query, Zustand

Hugging Face (Sentence-BERT, Spaces)

Google Gemini API, Firebase, Cloud Run

OCR.space, Tesseract

Built with ❤️ for fairer hiring practices

📞 Support & Links
Live ML API: https://preeee-276-ml-service-api.hf.space/docs

Backend (Cloud Run): https://resume-backend-948277799081.us-central1.run.app

Frontend (dev): http://localhost:5173

Issues: Check browser console / backend logs; verify environment variables.
