# TRUSTLENS - COMPLETE APPLICATION (With Home Navigation Button)

import streamlit as st
import time
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="TrustLens - AI Resume Screening", 
    layout="wide",
    page_icon="🎯",
    initial_sidebar_state="collapsed"
)

# ---------------- SESSION STATE FOR NAVIGATION ----------------
# Main navigation state
if "app_page" not in st.session_state:
    st.session_state.app_page = "home"  # home, dashboard, hiring, hr_review, fairness, export

# Home screen states
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_type" not in st.session_state:
    st.session_state.user_type = None
if "show_status_page" not in st.session_state:
    st.session_state.show_status_page = False
if "selected_candidate" not in st.session_state:
    st.session_state.selected_candidate = None
if "show_login_options" not in st.session_state:
    st.session_state.show_login_options = False    
if "candidate_logged_in" not in st.session_state:
    st.session_state.candidate_logged_in = False
if "candidate_app_id" not in st.session_state:
    st.session_state.candidate_app_id = None
if "login_tab" not in st.session_state:
    st.session_state.login_tab = "company"

# Dashboard states
if "decisions" not in st.session_state:
    st.session_state["decisions"] = {}
if "show_model_selection" not in st.session_state:
    st.session_state.show_model_selection = False
if "final_role_temp" not in st.session_state:
    st.session_state.final_role_temp = ""
if "files_temp" not in st.session_state:
    st.session_state.files_temp = None
if "dashboard_page" not in st.session_state:
    st.session_state.dashboard_page = "Dashboard"

# ---------------- SAMPLE DATABASE ----------------
candidate_records = {
    "APP001": {
        "email": "user@gmail.com",
        "password": "alice123",
        "name": "Alice Johnson",
        "skills": "Python, Machine Learning, SQL",
        "status": "Accepted",
        "criteria": "Skill match, ML project experience, problem solving",
        "reason": "Strong ML portfolio and relevant internship experience",
        "improvement": "Improve system design knowledge"
    },
    "APP002": {
        "email": "test@gmail.com",
        "password": "bob123",
        "name": "Bob Smith",
        "skills": "Java, Spring Boot",
        "status": "Rejected",
        "criteria": "Backend development skills, project relevance",
        "reason": "Limited project experience related to job role",
        "improvement": "Work on real backend projects and improve API design skills"
    },
    "APP003": {
        "email": "candidate@gmail.com",
        "password": "charlie123",
        "name": "Charlie Brown",
        "skills": "React, JavaScript, UI Design",
        "status": "Pending",
        "criteria": "Frontend development, UI/UX portfolio",
        "reason": "Application under review by HR team",
        "improvement": "Add more real-world UI projects"
    }
}

company_users = {
    "admin@company.com": {"password": "1234", "name": "Admin User"},
    "hr@company.com": {"password": "hr2024", "name": "HR Manager"},
}

def company_login(email, password):
    if email in company_users and company_users[email]["password"] == password:
        st.session_state.logged_in = True
        st.session_state.user_type = "company"
        st.session_state.app_page = "dashboard"
        st.session_state.dashboard_page = "Dashboard"
        return True
    return False

def candidate_login(app_id, password):
    if app_id in candidate_records and candidate_records[app_id]["password"] == password:
        st.session_state.candidate_logged_in = True
        st.session_state.candidate_app_id = app_id
        st.session_state.selected_candidate = candidate_records[app_id]
        return True
    return False

def go_to_home():
    """Navigate back to home screen"""
    st.session_state.logged_in = False
    st.session_state.candidate_logged_in = False
    st.session_state.user_type = None
    st.session_state.app_page = "home"
    st.session_state.show_login_options = False
    st.session_state.show_status_page = False
    st.session_state.show_model_selection = False

def logout():
    """Full logout"""
    st.session_state.logged_in = False
    st.session_state.candidate_logged_in = False
    st.session_state.user_type = None
    st.session_state.app_page = "home"
    st.session_state.show_login_options = False
    st.session_state.show_status_page = False
    st.session_state.show_model_selection = False

# ============= HOME SCREEN CSS (SAME AS YOUR ORIGINAL) =============
st.markdown("""
<style>
    /* Google Fonts Material Design */
    @import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,100..900&display=swap');
    
    /* Material Design 3 Color System */
    :root {
        --md-primary: #6750A4;
        --md-primary-light: #9A82DB;
        --md-primary-dark: #4A3780;
        --md-secondary: #625B71;
        --md-tertiary: #7D5260;
        --md-surface: #FFFBFE;
        --md-surface-variant: #E7E0EC;
        --md-on-surface: #1C1B1F;
        --md-on-surface-variant: #49454F;
        --md-error: #BA1A1A;
        --md-outline: #79747E;
    }
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(145deg, #F5F0FF 0%, #EBE4F5 100%);
    }
    
    /* Main Container */
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Logo Section */
    .logo-section {
        text-align: center;
        padding: 30px 0 20px 0;
        margin-bottom: 20px;
    }
    
    .logo-title {
        font-family: 'Inter', sans-serif;
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(135deg, var(--md-primary) 0%, var(--md-tertiary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 3px;
        margin-bottom: 12px;
    }
    
    .logo-tagline {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: var(--md-on-surface-variant);
        letter-spacing: 4px;
        word-spacing: 8px;
    }
    
    /* Hero Section */
    .hero-modern {
        background: linear-gradient(135deg, var(--md-primary) 0%, var(--md-tertiary) 100%);
        border-radius: 32px;
        padding: 60px 48px;
        margin-bottom: 60px;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .hero-title-modern {
        font-family: 'Inter', sans-serif;
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 20px;
        line-height: 1.2;
    }
    
    .hero-text-modern {
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        opacity: 0.95;
        margin-bottom: 32px;
        line-height: 1.6;
    }
    
    /* Login Container */
    .login-container-enhanced {
        max-width: 500px;
        margin: 0 auto;
        animation: slideUp 0.4s ease;
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .login-card-enhanced {
        background: white;
        border-radius: 48px;
        padding: 48px 40px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .login-card-enhanced::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, var(--md-primary), var(--md-tertiary));
    }
    
    .login-header-enhanced {
        text-align: center;
        margin-bottom: 32px;
    }
    
    .login-icon-enhanced {
        font-size: 64px;
        margin-bottom: 16px;
    }
    
    .login-title-enhanced {
        font-family: 'Inter', sans-serif;
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(135deg, var(--md-primary), var(--md-tertiary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    
    .login-subtitle-enhanced {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        color: var(--md-on-surface-variant);
    }
    
    /* Demo Credentials Card */
    .demo-card-enhanced {
        background: linear-gradient(135deg, #F5F0FF 0%, #EBE4F5 100%);
        border-radius: 20px;
        padding: 16px;
        margin-top: 24px;
    }
    
    .demo-title-enhanced {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        font-weight: 600;
        color: var(--md-primary);
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .demo-item-enhanced {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        color: var(--md-on-surface-variant);
        padding: 4px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .demo-badge-enhanced {
        background: var(--md-primary);
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 10px;
        font-weight: 600;
    }
    
    /* Features Grid */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 30px;
        margin: 40px 0 60px 0;
        padding: 0;
    }
    
    .feature-card-modern {
        background: white;
        border-radius: 24px;
        padding: 32px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        position: relative;
        border: 1px solid rgba(103, 80, 164, 0.1);
        min-height: 280px;
        display: flex;
        flex-direction: column;
    }
    
    .feature-card-modern:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(103, 80, 164, 0.15);
        border-color: var(--md-primary-light);
    }
    
    .feature-icon-modern {
        font-size: 56px;
        margin-bottom: 20px;
    }
    
    .feature-title-modern {
        font-family: 'Inter', sans-serif;
        font-size: 22px;
        font-weight: 700;
        color: var(--md-primary-dark);
        margin-bottom: 12px;
    }
    
    .feature-desc-modern {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        color: var(--md-on-surface-variant);
        line-height: 1.5;
        flex: 1;
    }
    
    .feature-badge-modern {
        position: absolute;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, var(--md-primary-light), var(--md-primary));
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
    }
    
    /* Testimonials Grid */
    .testimonials-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 30px;
        margin: 40px 0 60px 0;
        padding: 0;
    }
    
    .testimonial-card-modern {
        background: white;
        border-radius: 24px;
        padding: 32px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        position: relative;
        border: 1px solid rgba(103, 80, 164, 0.1);
        min-height: 320px;
        display: flex;
        flex-direction: column;
    }
    
    .testimonial-card-modern:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(103, 80, 164, 0.15);
    }
    
    .testimonial-quote-modern {
        font-size: 48px;
        color: var(--md-primary-light);
        opacity: 0.3;
        position: absolute;
        top: 20px;
        left: 24px;
        font-family: serif;
    }
    
    .testimonial-stars-modern {
        margin-bottom: 20px;
        font-size: 18px;
        letter-spacing: 2px;
    }
    
    .testimonial-text-modern {
        font-family: 'Inter', sans-serif;
        font-size: 15px;
        line-height: 1.6;
        color: var(--md-on-surface);
        margin-bottom: 24px;
        position: relative;
        z-index: 1;
        flex: 1;
    }
    
    .testimonial-author-modern {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: auto;
        padding-top: 20px;
        border-top: 2px solid rgba(103, 80, 164, 0.1);
    }
    
    .testimonial-avatar-modern {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--md-primary-light), var(--md-primary));
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 24px;
        margin: 40px 0 60px 0;
        padding: 0;
    }
    
    .stat-card-modern {
        background: linear-gradient(135deg, var(--md-primary) 0%, var(--md-tertiary) 100%);
        border-radius: 20px;
        padding: 32px 20px;
        text-align: center;
        color: white;
        transition: transform 0.3s ease;
    }
    
    .stat-card-modern:hover {
        transform: translateY(-4px);
    }
    
    .stat-number-modern {
        font-family: 'Inter', sans-serif;
        font-size: 42px;
        font-weight: 800;
        margin: 16px 0;
    }
    
    .stat-label-modern {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        opacity: 0.95;
    }
    
    .stat-icon-modern {
        font-size: 40px;
    }
    
    /* Section Titles */
    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 36px;
        font-weight: 700;
        background: linear-gradient(135deg, var(--md-primary) 0%, var(--md-tertiary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 60px 0 30px 0;
        text-align: center;
    }
    
    /* Dashboard Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--md-primary) 0%, var(--md-primary-dark) 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stRadio > div {
        background: rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 8px;
    }
    
    /* Dashboard Metric Cards */
    .metric-card {
        background: white;
        border-radius: 24px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(103,80,164,0.15);
    }
    
    /* Model Selection Cards */
    .model-card {
        border-radius: 28px;
        padding: 32px;
        text-align: center;
        color: white;
        transition: all 0.3s ease;
        cursor: pointer;
        height: 100%;
    }
    
    .model-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }
    
    /* Responsive Design */
    @media (max-width: 1024px) {
        .features-grid, .testimonials-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .features-grid, .testimonials-grid {
            grid-template-columns: 1fr;
        }
        .stats-grid {
            grid-template-columns: 1fr;
        }
        .hero-title-modern {
            font-size: 32px;
        }
        .hero-modern {
            padding: 40px 24px;
        }
        .section-title {
            font-size: 28px;
        }
        .login-card-enhanced {
            padding: 32px 24px;
            margin: 16px;
        }
        .logo-title {
            font-size: 28px;
        }
        .logo-tagline {
            font-size: 10px;
            letter-spacing: 2px;
        }
        .model-card {
            padding: 20px;
            margin-bottom: 16px;
        }
    }
    
    /* Streamlit Button Overrides */
    .stButton > button {
        background: var(--md-primary);
        color: white;
        border: none;
        border-radius: 40px;
        padding: 12px 24px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        width: 100%;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        background: var(--md-primary-dark);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(103, 80, 164, 0.3);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        border-radius: 16px !important;
        border: 2px solid var(--md-outline) !important;
        padding: 12px 16px !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: var(--md-primary) !important;
        box-shadow: 0 0 0 3px rgba(103,80,164,0.2) !important;
    }
    
    /* Success/Error/Warning */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 16px !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--md-primary), var(--md-tertiary));
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        background: white;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ============= MAIN UI =============
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Logo Section (Common for all pages)
st.markdown("""
<div class="logo-section">
    <div class="logo-title">TRUSTLENS</div>
    <div class="logo-tagline">CLARITY • SECURITY • VERIFICATION</div>
</div>
""", unsafe_allow_html=True)

# ============= NAVIGATION LOGIC =============

# If company is logged in, show Dashboard with sidebar navigation
if st.session_state.app_page == "dashboard" and st.session_state.logged_in:
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 48px;">🏢</div>
            <div style="font-family: Inter; font-size: 20px; font-weight: 700;">TrustLens</div>
            <div style="font-family: Inter; font-size: 12px; opacity: 0.8;">Company Portal</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sidebar Radio for Dashboard Navigation
        selected_page = st.radio(
            "📂 Navigation",
            ["Dashboard", "New Hiring Round", "HR Review", "Fairness Report", "Export Results"],
            index=["Dashboard", "New Hiring Round", "HR Review", "Fairness Report", "Export Results"].index(st.session_state.dashboard_page) if st.session_state.dashboard_page in ["Dashboard", "New Hiring Round", "HR Review", "Fairness Report", "Export Results"] else 0
        )
        
        # Update current page based on selection
        st.session_state.dashboard_page = selected_page
        
        st.markdown("---")
        
        # HOME BUTTON - Navigate back to Home Screen
        if st.button("🏠 Go to Home", use_container_width=True):
            go_to_home()
            st.rerun()
        
        # Logout Button
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
        
        st.markdown("---")
        st.caption("© 2026 TrustLens")
    
    # ============= DASHBOARD CONTENT =============
    
    if st.session_state.dashboard_page == "Dashboard":
        st.title("📊 Company Dashboard")
        st.markdown("<p style='color:#666;margin-bottom:30px;'>Overview of your hiring activity and performance metrics</p>", unsafe_allow_html=True)
        
        total_resumes = 120
        candidates_screened = 100
        shortlisted = 25
        rejected = 60
        pending_reviews = 15
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 32px;">📄</div>
                <div style="font-size: 28px; font-weight: 700;">{total_resumes}</div>
                <div style="color: #666;">Total Resumes</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 32px;">✅</div>
                <div style="font-size: 28px; font-weight: 700;">{shortlisted}</div>
                <div style="color: #666;">Shortlisted</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 32px;">❌</div>
                <div style="font-size: 28px; font-weight: 700;">{rejected}</div>
                <div style="color: #666;">Rejected</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 32px;">⏳</div>
                <div style="font-size: 28px; font-weight: 700;">{pending_reviews}</div>
                <div style="color: #666;">Pending Reviews</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### 📈 Hiring Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Candidate Distribution**")
            labels = ["Shortlisted", "Rejected", "Pending"]
            values = [shortlisted, rejected, pending_reviews]
            colors = ['#4CAF50', '#f44336', '#FF9806']
            
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            ax1.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)
        
        with col2:
            st.markdown("**Hiring Pipeline**")
            categories = ["Uploaded", "Screened", "Shortlisted", "Rejected"]
            values = [total_resumes, candidates_screened, shortlisted, rejected]
            colors_bar = ['#6750A4', '#9A82DB', '#4CAF50', '#f44336']
            
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            bars = ax2.bar(categories, values, color=colors_bar, edgecolor='white', linewidth=2)
            for bar, val in zip(bars, values):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, str(val), ha='center', fontweight='bold')
            ax2.set_ylabel('Number of Candidates')
            st.pyplot(fig2)
        
        st.markdown("---")
        st.subheader("📊 Shortlisting Progress")
        progress = shortlisted / total_resumes
        st.progress(progress)
        st.write(f"**{round(progress * 100, 2)}%** of candidates shortlisted")
        
        st.info("💡 This dashboard provides a quick visual summary of your hiring pipeline.")
    
    elif st.session_state.dashboard_page == "New Hiring Round":
        if not st.session_state.show_model_selection:
            st.title("🆕 New Hiring Round")
            
            col1, col2 = st.columns(2)
            with col1:
                job_roles = ["Software Engineer", "Data Scientist", "ML Engineer", "Frontend Developer", "Backend Developer", "DevOps Engineer"]
                role = st.selectbox("🎯 Select Job Role", job_roles)
            with col2:
                custom_role = st.text_input("✏️ Or enter custom role", placeholder="e.g., AI Research Scientist")
            
            final_role = custom_role if custom_role else role
            
            job_desc = st.text_area("📝 Job Description", height=150, placeholder="Paste the complete job description here...")
            
            st.subheader("⚖️ Fairness Settings")
            mode = st.radio("Fairness Mode", ["Strict", "Balanced", "Custom"], horizontal=True)
            
            files = st.file_uploader(
                "📎 Upload Resumes",
                type=["pdf", "docx", "jpg", "png"],
                accept_multiple_files=True,
                help="Supports PDF, DOCX, JPG, PNG. Max 30 files, 30MB each."
            )
            
            if files:
                if len(files) > 30:
                    st.error("❌ Max 30 files allowed")
                for f in files:
                    if f.size > 30 * 1024 * 1024:
                        st.error(f"❌ {f.name} exceeds 30MB")
                st.success(f"✅ {len(files)} file(s) selected successfully!")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🚀 Start Screening", use_container_width=True, type="primary"):
                    if files and len(files) > 0:
                        st.session_state.show_model_selection = True
                        st.session_state.final_role_temp = final_role
                        st.session_state.files_temp = files
                        st.rerun()
                    else:
                        st.error("❌ Please upload at least one resume before starting screening")
            with col2:
                if st.button("🗑 Clear All", use_container_width=True):
                    st.rerun()
        
        else:
            st.title("🤖 Select Screening Method")
            st.markdown(f"<p style='color:#666;margin-bottom:20px;'>Job Role: <strong>{st.session_state.final_role_temp}</strong> | Files: <strong>{len(st.session_state.files_temp)}</strong> resumes uploaded</p>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2, gap="large")
            
            with col1:
                st.markdown("""
                <div class="model-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <div style="font-size: 72px; margin-bottom: 20px;">📊</div>
                    <h2 style="margin-bottom: 10px;">Pre-trained Model</h2>
                    <p style="opacity: 0.9; margin-bottom: 20px;">Industry-standard AI model trained on millions of resumes</p>
                    <div style="text-align: left; margin-top: 20px;">
                        <p>✓ 98.5% accuracy rate</p>
                        <p>✓ Trained on 1M+ resumes</p>
                        <p>✓ Instant results</p>
                        <p>✓ Industry best practices</p>
                        <p>✓ Bias detection included</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🎯 Use Pre-trained Model", use_container_width=True, key="pretrained_btn"):
                    with st.spinner("🔄 Screening in progress using Pre-trained Model..."):
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.02)
                            progress_bar.progress(i + 1)
                        time.sleep(0.5)
                    st.success(f"✅ Screening completed for {st.session_state.final_role_temp} using Pre-trained Model!")
                    st.balloons()
                    st.info(f"📊 Results: {len(st.session_state.files_temp)} resumes screened. {int(len(st.session_state.files_temp)*0.3)} candidates shortlisted.")
                    if st.button("◀️ Start New Round", use_container_width=True):
                        st.session_state.show_model_selection = False
                        st.rerun()
            
            with col2:
                st.markdown("""
                <div class="model-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <div style="font-size: 72px; margin-bottom: 20px;">🏢</div>
                    <h2 style="margin-bottom: 10px;">Our Custom Model</h2>
                    <p style="opacity: 0.9; margin-bottom: 20px;">Organization-specific model trained on your hiring data</p>
                    <div style="text-align: left; margin-top: 20px;">
                        <p>✓ Customized to your needs</p>
                        <p>✓ Learns from your decisions</p>
                        <p>✓ Better cultural fit</p>
                        <p>✓ Continuous improvement</p>
                        <p>✓ Explainable AI</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🔧 Use Our Custom Model", use_container_width=True, key="custom_btn"):
                    with st.spinner("🔄 Screening in progress using Custom Model..."):
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.02)
                            progress_bar.progress(i + 1)
                        time.sleep(0.5)
                    st.success(f"✅ Screening completed for {st.session_state.final_role_temp} using Our Custom Model!")
                    st.balloons()
                    st.info(f"📊 Results: {len(st.session_state.files_temp)} resumes screened. {int(len(st.session_state.files_temp)*0.35)} candidates shortlisted.")
                    if st.button("◀️ Start New Round", use_container_width=True, key="new_round"):
                        st.session_state.show_model_selection = False
                        st.rerun()
            
            st.markdown("---")
            if st.button("◀️ Back to Form", use_container_width=True):
                st.session_state.show_model_selection = False
                st.rerun()
    
    elif st.session_state.dashboard_page == "HR Review":
        st.title("👩‍💼 HR Review & Candidate Ranking")
        
        candidates = [
            {"app_no": "APP001", "name": "Alice Johnson", "email": "alice@gmail.com", "skills": "Python, ML, SQL", "reason": "Strong ML experience and ML projects", "score": 92},
            {"app_no": "APP002", "name": "Bob Smith", "email": "bob@gmail.com", "skills": "Java, Spring Boot", "reason": "Good backend development experience", "score": 78},
            {"app_no": "APP003", "name": "Charlie Brown", "email": "charlie@gmail.com", "skills": "React, JavaScript", "reason": "Strong frontend portfolio", "score": 85}
        ]
        
        for i, c in enumerate(candidates):
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 1, 1])
                
                with col1:
                    st.markdown(f"**{c['app_no']}**")
                with col2:
                    st.markdown(f"**{c['name']}**")
                with col3:
                    st.markdown(f"{c['skills']}")
                with col4:
                    score_color = "#4CAF50" if c['score'] >= 85 else "#FF9806" if c['score'] >= 70 else "#f44336"
                    st.markdown(f"<span style='background:{score_color};color:white;padding:4px 12px;border-radius:20px;font-size:12px;'>Score: {c['score']}</span>", unsafe_allow_html=True)
                with col5:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("✅", key=f"accept_{i}"):
                            st.session_state["decisions"][c["app_no"]] = "Accepted"
                            st.success(f"{c['name']} Accepted")
                    with col_b:
                        if st.button("❌", key=f"reject_{i}"):
                            st.session_state["decisions"][c["app_no"]] = "Rejected"
                            st.warning(f"{c['name']} Rejected")
                
                with st.expander(f"📋 View Details - {c['name']}"):
                    st.markdown(f"**Email:** {c['email']}")
                    st.markdown(f"**Selection Reason:** {c['reason']}")
                    st.markdown(f"**Skills:** {c['skills']}")
                
                st.markdown("---")
    
    elif st.session_state.dashboard_page == "Fairness Report":
        st.title("⚖️ Fairness Report")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📌 Screening Criteria")
            criteria_data = {
                "Criteria": ["Skills Match", "Experience", "Projects", "Education", "Keywords"],
                "Weight": ["35%", "25%", "20%", "10%", "10%"]
            }
            st.dataframe(pd.DataFrame(criteria_data), use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### 🛡️ Bias Prevention")
            st.info("""
            ✅ Names are anonymized  
            ✅ Gender-neutral evaluation  
            ✅ Age not considered  
            ✅ Photos ignored  
            ✅ Location-based bias removed
            """)
        
        st.markdown("---")
        st.markdown("#### 📊 Score Distribution")
        
        scores = [85, 92, 78, 88, 95, 72, 68, 90, 82, 76]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(scores, bins=10, color='#6750A4', edgecolor='white', linewidth=2, alpha=0.7)
        ax.set_xlabel('Scores')
        ax.set_ylabel('Number of Candidates')
        ax.set_title('Candidate Score Distribution')
        ax.axvline(x=85, color='#4CAF50', linestyle='--', linewidth=2, label='Shortlist Threshold (85)')
        ax.legend()
        st.pyplot(fig)
        
        st.markdown("---")
        st.markdown("#### ⚙️ Fairness Mode: Balanced")
        st.progress(0.7)
        st.write("**Current Setting:** Balanced Mode - Considers both skills and candidate potential")
        
        st.markdown("---")
        st.info("📜 **Responsible AI Statement:** AI assists HR but final decisions require human review. All sensitive attributes are ignored during screening.")
    
    elif st.session_state.dashboard_page == "Export Results":
        st.title("📤 Export Results")
        
        candidates_data = [
            ["APP001", "Alice Johnson", "Python, ML, SQL", st.session_state.get("decisions", {}).get("APP001", "Pending")],
            ["APP002", "Bob Smith", "Java, Spring Boot", st.session_state.get("decisions", {}).get("APP002", "Pending")],
            ["APP003", "Charlie Brown", "React, JavaScript", st.session_state.get("decisions", {}).get("APP003", "Pending")]
        ]
        
        df = pd.DataFrame(candidates_data, columns=["Application No", "Candidate Name", "Skills", "HR Decision"])
        
        st.markdown("#### 📋 Hiring Results")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Candidates", len(df))
        with col2:
            st.metric("Accepted", len(df[df["HR Decision"] == "Accepted"]))
        with col3:
            st.metric("Rejected", len(df[df["HR Decision"] == "Rejected"]))
        
        st.markdown("---")
        st.markdown("#### ⬇️ Download Options")
        
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False)
            st.download_button("📥 Download CSV", data=csv, file_name="hiring_results.csv", mime="text/csv", use_container_width=True)
        with col2:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            st.download_button("📊 Download Excel", data=buffer.getvalue(), file_name="hiring_results.xlsx", use_container_width=True)

# ============= HOME SCREEN VIEW =============
else:
    
    # Header with Login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        if not st.session_state.logged_in and not st.session_state.candidate_logged_in:
            if not st.session_state.show_login_options:
                if st.button("🔐 Login", key="login_main"):
                    st.session_state.show_login_options = True
                    st.rerun()
            else:
                if st.button("🚪 Logout", key="logout_main"):
                    st.session_state.logged_in = False
                    st.session_state.candidate_logged_in = False
                    st.session_state.show_login_options = False
                    st.rerun()
    
    # Login Section with Back Button
    if st.session_state.show_login_options and not st.session_state.logged_in and not st.session_state.candidate_logged_in:
        st.markdown('<div class="login-container-enhanced">', unsafe_allow_html=True)
        
        # Back Button
        back_col1, back_col2, back_col3 = st.columns([1, 3, 1])
        with back_col1:
            back_btn = st.button("◀️ Back", key="back_from_login", use_container_width=True)
            if back_btn:
                st.session_state.show_login_options = False
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Tab Selector
        tab_col1, tab_col2 = st.columns(2)
        with tab_col1:
            if st.button("🏢 Company", use_container_width=True, key="tab_company"):
                st.session_state.login_tab = "company"
                st.rerun()
        with tab_col2:
            if st.button("👤 Candidate", use_container_width=True, key="tab_candidate"):
                st.session_state.login_tab = "candidate"
                st.rerun()
        
        # Company Login Card
        if st.session_state.login_tab == "company":
            st.markdown("""
            <div class="login-card-enhanced">
                <div class="login-header-enhanced">
                    <div class="login-icon-enhanced">🏢</div>
                    <div class="login-title-enhanced">Company Portal</div>
                    <div class="login-subtitle-enhanced">Sign in to access your dashboard</div>
                </div>
            """, unsafe_allow_html=True)
            
            company_email = st.text_input("📧 Email Address", placeholder="admin@company.com", key="company_email_input")
            company_password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="company_password_input")
            
            if st.button("🔑 Sign In", use_container_width=True, key="company_login_btn"):
                if company_login(company_email, company_password):
                    st.success("✅ Login Successful! Redirecting...")
                    time.sleep(1)
                    st.session_state.show_login_options = False
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password")
            
            st.markdown("""
            <div class="demo-card-enhanced">
                <div class="demo-title-enhanced">📋 Demo Credentials</div>
                <div class="demo-item-enhanced">
                    <span class="demo-badge-enhanced">Admin</span>
                    <span>admin@company.com / 1234</span>
                </div>
                <div class="demo-item-enhanced">
                    <span class="demo-badge-enhanced">HR</span>
                    <span>hr@company.com / hr2024</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Candidate Login Card
        else:
            st.markdown("""
            <div class="login-card-enhanced">
                <div class="login-header-enhanced">
                    <div class="login-icon-enhanced">👤</div>
                    <div class="login-title-enhanced">Candidate Portal</div>
                    <div class="login-subtitle-enhanced">Check your application status</div>
                </div>
            """, unsafe_allow_html=True)
            
            candidate_app_id = st.text_input("🆔 Application ID", placeholder="APP001, APP002, APP003", key="candidate_app_input")
            candidate_password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="candidate_password_input")
            
            if st.button("🔍 Check Status", use_container_width=True, key="candidate_login_btn"):
                if candidate_login(candidate_app_id, candidate_password):
                    st.success("✅ Login Successful! Redirecting to your status...")
                    time.sleep(1)
                    st.session_state.show_login_options = False
                    st.session_state.show_status_page = True
                    st.rerun()
                else:
                    st.error("❌ Invalid Application ID or Password")
            
            st.markdown("""
            <div class="demo-card-enhanced">
                <div class="demo-title-enhanced">📋 Demo Credentials</div>
                <div class="demo-item-enhanced">
                    <span class="demo-badge-enhanced" style="background:#4CAF50;">Accepted</span>
                    <span>APP001 / alice123</span>
                </div>
                <div class="demo-item-enhanced">
                    <span class="demo-badge-enhanced" style="background:#f44336;">Rejected</span>
                    <span>APP002 / bob123</span>
                </div>
                <div class="demo-item-enhanced">
                    <span class="demo-badge-enhanced" style="background:#FF9806;">Pending</span>
                    <span>APP003 / charlie123</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Hero Section
    if not st.session_state.logged_in and not st.session_state.candidate_logged_in and not st.session_state.show_login_options:
        st.markdown("""
        <div class="hero-modern">
            <div class="hero-title-modern">🚀 Hire Smarter with AI-Powered Resume Screening</div>
            <div class="hero-text-modern">Quickly filter and shortlist the best candidates using intelligent automation. Our platform reduces hiring time by 70% while ensuring fairness and transparency.</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Candidate Status Page
    if st.session_state.show_status_page and st.session_state.selected_candidate:
        data = st.session_state.selected_candidate
        status_color = "#4CAF50" if data['status'] == "Accepted" else "#f44336" if data['status'] == "Rejected" else "#FF9806"
        
        st.markdown(f"""
        <div style="background:white;border-radius:24px;padding:32px;margin:40px 0;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
            <h2 style="text-align:center;font-family:Inter;">📋 Application Status</h2>
            <div style="background:{status_color};color:white;padding:20px;border-radius:16px;text-align:center;margin:20px 0;">
                <h3 style="font-family:Inter;">{data['status']}</h3>
                <p style="font-family:Inter;">Application ID: {st.session_state.candidate_app_id}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**👤 Name:** {data['name']}")
            st.write(f"**🛠️ Skills:** {data['skills']}")
        with col2:
            st.write(f"**📧 Email:** {data['email']}")
            st.write(f"**📅 Applied on:** January 15, 2026")
        
        st.info(f"**Selection Criteria:** {data['criteria']}")
        
        if data['status'] == "Accepted":
            st.success(f"**Decision:** {data['reason']}")
            st.balloons()
        elif data['status'] == "Rejected":
            st.warning(f"**Decision:** {data['reason']}")
            st.info(f"**Improvement:** {data['improvement']}")
        else:
            st.info(f"**Status:** {data['reason']}")
            st.warning(f"**Suggestions:** {data['improvement']}")
        
        if st.button("◀️ Back to Home", use_container_width=True, key="back_home"):
            st.session_state.show_status_page = False
            st.session_state.candidate_logged_in = False
            st.rerun()
    
    # Core Features Section
    if not st.session_state.logged_in and not st.session_state.candidate_logged_in and not st.session_state.show_login_options:
        st.markdown('<div class="section-title">⚙️ Core Features</div>', unsafe_allow_html=True)
        
        features = [
            ("📄", "Resume Parsing", "Extract structured data from PDF and DOCX resumes automatically with 99% accuracy.", "AI-Powered"),
            ("🤖", "AI Candidate Ranking", "Advanced AI analyzes resumes and ranks candidates based on skills and experience.", "ML Based"),
            ("📊", "Analytics Dashboard", "Get deep insights on recruitment performance and candidate quality metrics.", "Real-time"),
            ("⚡", "Bulk Upload", "Upload and analyze multiple resumes at once with drag-and-drop functionality.", "Fast"),
            ("🎯", "Skill Matching", "Match candidates with job requirements automatically using intelligent algorithms.", "Precise"),
            ("📤", "Export Candidates", "Export shortlisted candidates in CSV, Excel, or PDF formats easily.", "Flexible")
        ]
        
        for i in range(0, len(features), 3):
            cols = st.columns(3, gap="large")
            for j in range(3):
                if i + j < len(features):
                    icon, title, desc, badge = features[i + j]
                    with cols[j]:
                        st.markdown(f"""
                        <div class="feature-card-modern">
                            <div class="feature-badge-modern">{badge}</div>
                            <div class="feature-icon-modern">{icon}</div>
                            <div class="feature-title-modern">{title}</div>
                            <div class="feature-desc-modern">{desc}</div>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Testimonials Section
    if not st.session_state.logged_in and not st.session_state.candidate_logged_in and not st.session_state.show_login_options:
        st.markdown('<div class="section-title">⭐ What Our Users Say</div>', unsafe_allow_html=True)
        
        testimonials = [
            ("👩‍💼", "Sarah Johnson", "HR Manager, TechCorp", "TrustLens has revolutionized our hiring process! The AI screening is incredibly accurate, reducing our time-to-hire by 70%.", 5),
            ("👨‍💻", "Michael Chen", "Tech Recruiter, InnovateLabs", "The fairness features ensure completely unbiased screening. Best investment for our recruitment team!", 5),
            ("👔", "David Williams", "CEO, StartupHub", "Processing 1000+ resumes used to take weeks. Now we do it in hours! TrustLens has transformed our workflow.", 5)
        ]
        
        cols = st.columns(3, gap="large")
        for idx, (avatar, name, title, text, stars) in enumerate(testimonials):
            with cols[idx]:
                star_html = "⭐" * stars
                st.markdown(f"""
                <div class="testimonial-card-modern">
                    <div class="testimonial-quote-modern">"</div>
                    <div class="testimonial-stars-modern">{star_html}</div>
                    <div class="testimonial-text-modern">{text}</div>
                    <div class="testimonial-author-modern">
                        <div class="testimonial-avatar-modern">{avatar}</div>
                        <div>
                            <div style="font-weight:700;font-family:Inter;">{name}</div>
                            <div style="font-size:13px;color:#666;font-family:Inter;">{title}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Stats Section
    if not st.session_state.logged_in and not st.session_state.candidate_logged_in and not st.session_state.show_login_options:
        st.markdown('<div class="section-title">📊 TrustLens by Numbers</div>', unsafe_allow_html=True)
        
        stats = [
            ("📄", "50,000+", "Resumes Processed"),
            ("🏢", "1,200+", "Happy Companies"),
            ("⏱️", "85%", "Faster Hiring"),
            ("🎯", "96%", "Match Accuracy")
        ]
        
        cols = st.columns(4, gap="medium")
        for idx, (icon, number, label) in enumerate(stats):
            with cols[idx]:
                st.markdown(f"""
                <div class="stat-card-modern">
                    <div class="stat-icon-modern">{icon}</div>
                    <div class="stat-number-modern">{number}</div>
                    <div class="stat-label-modern">{label}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # FAQ Section
    if not st.session_state.logged_in and not st.session_state.candidate_logged_in and not st.session_state.show_login_options:
        st.markdown('<div class="section-title">❓ Frequently Asked Questions</div>', unsafe_allow_html=True)
        
        with st.expander("🤔 How does AI screening work?"):
            st.write("""
            Our AI evaluates resumes using:
            - **Natural Language Processing** to understand context
            - **Skill matching algorithms** to compare with job requirements
            - **Experience analysis** to assess relevance
            - **Project evaluation** to gauge practical expertise
            """)
        
        with st.expander("🔒 Is my data secure?"):
            st.write("""
            Absolutely! We use:
            - **End-to-end encryption** for all data
            - **Secure cloud storage** with access controls
            - **GDPR compliance** for data protection
            - **Regular security audits** and penetration testing
            """)
        
        with st.expander("⚡ How fast is the screening process?"):
            st.write("""
            Our AI can screen:
            - **100 resumes** in under 5 minutes
            - **500 resumes** in under 20 minutes
            - **1000+ resumes** in under 1 hour
            """)
    
    # Contact Section
    st.markdown('<div class="section-title">📧 Contact Us</div>', unsafe_allow_html=True)
    
    with st.form("contact_form"):
        col1, col2 = st.columns(2)
        with col1:
            contact_name = st.text_input("👤 Your Name", placeholder="John Doe", key="contact_name")
        with col2:
            contact_email = st.text_input("📧 Email Address", placeholder="john@example.com", key="contact_email")
        
        contact_msg = st.text_area("💬 Message", placeholder="How can we help you?", height=100, key="contact_message")
        
        submit = st.form_submit_button("📤 Send Message", use_container_width=True)
        
        if submit:
            if contact_name and contact_email and contact_msg:
                st.success("✅ Message sent successfully! Our team will get back to you within 24 hours.")
            else:
                st.error("❌ Please fill in all fields.")
    
    # Footer
    st.markdown("""
    <div style="text-align:center;padding:40px 20px;margin-top:60px;border-top:1px solid rgba(103,80,164,0.1);font-family:Inter;color:#666;">
        <p>© 2026 TrustLens - AI Resume Screening Platform</p>
        <p>
            <span style="margin:0 10px;">🔒 Privacy Policy</span> |
            <span style="margin:0 10px;">📜 Terms of Service</span> |
            <span style="margin:0 10px;">© Copyright</span>
        </p>
        <p style="font-size:12px;margin-top:20px;">Made with ❤️ using Material Design 3</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)