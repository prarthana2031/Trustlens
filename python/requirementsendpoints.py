#1. Authentication Endpoints

# Company Login
# POST /api/auth/login
# Request Body:
# {
#     "email": "admin@company.com",
#     "password": "1234"
# }
# Response:
# {
#     "success": true,
#     "token": "jwt_token_here",
#     "user": {
#         "id": "user_id",
#         "name": "Admin User",
#         "email": "admin@company.com",
#         "role": "company"
#     }
# }

# Company Logout
# POST /api/auth/logout
# Headers:
#     Authorization: Bearer {token}
# Response:
# {
#     "success": true,
#     "message": "Logged out successfully"
# }

#2. Screening Endpoints

# Start Screening
POST /api/screening/start
Headers:
    Authorization: Bearer {token}
Request (multipart/form-data):
{
    "role": "Software Engineer",
    "model_type": "pretrained" | "custom",
    "fairness_mode": "strict" | "balanced" | "custom",
    "job_description": "string (optional)",
    "resumes": [file1.pdf, file2.pdf, ...]
}
Response:
{
    "success": true,
    "screening_id": "scr_12345",
    "message": "Screening completed successfully",
    "summary": {
        "total": 10,
        "shortlisted": 3,
        "review_needed": 4,
        "rejected": 3
    },
    "candidates": [
        {
            "id": "APP001",
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "skills": ["Python", "ML", "SQL"],
            "score": 92,
            "match_percentage": 92,
            "status": "Shortlisted",
            "reason": "Strong technical skills match"
        }
    ]
}

# Get Screening Status
GET /api/screening/status/{screening_id}
Response:
{
    "success": true,
    "status": "completed" | "processing" | "failed",
    "progress": 100
}


 #3. Candidates Endpoints
# Get All Candidates
GET /api/candidates
Headers:
    Authorization: Bearer {token}
Query Parameters:
    - status (optional): "Shortlisted" | "Rejected" | "Review"
    - limit (optional): default 50
    - offset (optional): default 0
Response:
{
    "success": true,
    "total": 25,
    "candidates": [
        {
            "id": "APP001",
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "skills": "Python, ML, SQL",
            "score": 92,
            "status": "Shortlisted",
            "resume_url": "https://..."
        }
    ]
}


# Get Single Candidate
GET /api/candidates/{candidate_id}
Response:
{
    "success": true,
    "candidate": {
        "id": "APP001",
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "skills": ["Python", "ML", "SQL"],
        "score": 92,
        "status": "Shortlisted",
        "reason": "Strong ML experience",
        "resume_url": "https://...",
        "parsed_data": {
            "experience_years": 5,
            "education": "MS in CS",
            "certifications": ["AWS Certified"]
        }
    }
}

# Review Candidate (Accept/Reject)
POST /api/candidates/{candidate_id}/review
Headers:
    Authorization: Bearer {token}
Request Body:
{
    "decision": "Accepted" | "Rejected",
    "feedback": "optional feedback message",
    "send_email": true (optional)
}
Response:
{
    "success": true,
    "message": "Candidate Accepted",
    "email_sent": true
}

#4. Reports Endpoints
# Get Fairness Report
GET /api/reports/fairness
Headers:
    Authorization: Bearer {token}
Response:
{
    "success": true,
    "data": {
        "screening_criteria": [
            {"criteria": "Skills Match", "weight": "35%", "description": "..."},
            {"criteria": "Experience", "weight": "25%", "description": "..."},
            {"criteria": "Projects", "weight": "20%", "description": "..."},
            {"criteria": "Education", "weight": "10%", "description": "..."},
            {"criteria": "Keywords", "weight": "10%", "description": "..."}
        ],
        "bias_prevention": {
            "ignored_attributes": ["Name", "Gender", "Age", "Photo", "Location", "Religion", "Nationality"],
            "reason": "Ensures fair and unbiased candidate evaluation"
        },
        "score_distribution": {
            "90-100": 5,
            "80-89": 10,
            "70-79": 8,
            "Below 70": 12
        },
        "fairness_metrics": {
            "gender_bias_score": 0.02,
            "age_bias_score": 0.01,
            "location_bias_score": 0.03,
            "overall_fairness": "Excellent"
        }
    }
}

# Export Results
GET /api/reports/export
Headers:
    Authorization: Bearer {token}
Query Parameters:
    - format: "csv" | "excel"
    - screening_id (optional)
Response:
    # For CSV: text/csv file
    # For Excel: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet


#5. File Upload Endpoints
# Upload Resume
POST /api/upload/resume
Headers:
    Authorization: Bearer {token}
Request (multipart/form-data):
{
    "resume": file.pdf
}
Response:
{
    "success": true,
    "file_id": "file_12345",
    "file_url": "https://...",
    "parsed_data": {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "skills": ["Python", "ML"],
        "experience_years": 5
    }
}

# Batch Upload Resumes
POST /api/upload/batch
Headers:
    Authorization: Bearer {token}
Request (multipart/form-data):
{
    "resumes": [file1.pdf, file2.pdf, ...]
}
Response:
{
    "success": true,
    "uploaded_count": 5,
    "failed_count": 0,
    "files": [
        {"name": "resume1.pdf", "file_id": "file_001", "status": "success"},
        {"name": "resume2.pdf", "file_id": "file_002", "status": "success"}
    ]
}


#6. Dashboard/Stats Endpoints
# Get Dashboard Statistics
GET /api/dashboard/stats
Headers:
    Authorization: Bearer {token}
Response:
{
    "success": true,
    "stats": {
        "total_resumes": 120,
        "candidates_screened": 100,
        "shortlisted": 25,
        "rejected": 60,
        "active_jobs": 5,
        "pending_reviews": 15,
        "shortlisting_progress": 20.83
    },
    "recent_activity": [
        {
            "date": "2026-01-15",
            "action": "Screening completed",
            "candidates": 10
        }
    ]
}

# Get Hiring Pipeline Data
GET /api/dashboard/pipeline
Response:
{
    "success": true,
    "pipeline": {
        "uploaded": 120,
        "screened": 100,
        "shortlisted": 25,
        "rejected": 60
    },
    "distribution": {
        "shortlisted": 25,
        "rejected": 60,
        "pending": 15
    }
}



# Health Check (already in your code)
GET /health
Response:
{
    "status": "ok",
    "timestamp": "2026-04-12T10:00:00Z"
}

# Readiness Check
GET /ready
Response:
{
    "status": "ready",
    "database": "connected"
}