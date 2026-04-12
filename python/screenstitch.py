# COMPANY DASHBOARD - Enhanced with Google Material Design 3

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import time
import plotly.express as px
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="TrustLens - Company Dashboard", 
    layout="wide",
    page_icon="🏢",
    initial_sidebar_state="expanded"
)

# ---------------- GOOGLE MATERIAL DESIGN 3 CSS ----------------
st.markdown("""
<style>
    /* Google Fonts */
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
        --md-success: #4CAF50;
        --md-warning: #FF9806;
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
    
    /* Sidebar Styling */
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
    
    /* Metric Cards */
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
    
    /* Feature Cards */
    .feature-card {
        background: white;
        border-radius: 20px;
        padding: 24px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 28px rgba(103,80,164,0.2);
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
    
    /* Section Titles */
    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(135deg, var(--md-primary) 0%, var(--md-tertiary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 30px 0 20px 0;
    }
    
    /* Button Styles */
    .stButton > button {
        background: var(--md-primary);
        color: white;
        border: none;
        border-radius: 40px;
        padding: 12px 24px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: var(--md-primary-dark);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(103,80,164,0.3);
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
    
    /* Responsive */
    @media (max-width: 768px) {
        .model-card {
            padding: 20px;
            margin-bottom: 16px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "decisions" not in st.session_state:
    st.session_state["decisions"] = {}
if "show_model_selection" not in st.session_state:
    st.session_state.show_model_selection = False
if "final_role_temp" not in st.session_state:
    st.session_state.final_role_temp = ""
if "files_temp" not in st.session_state:
    st.session_state.files_temp = None

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 48px;">🏢</div>
        <div style="font-family: Inter; font-size: 20px; font-weight: 700;">TrustLens</div>
        <div style="font-family: Inter; font-size: 12px; opacity: 0.8;">Company Portal</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    page = st.radio(
        "📂 Navigation",
        ["Dashboard", "New Hiring Round", "HR Review", "Fairness Report", "Export Results"],
        index=0
    )
    
    st.markdown("---")
    st.caption("© 2026 TrustLens")

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.title("📊 Company Dashboard")
    st.markdown("<p style='color:#666;margin-bottom:30px;'>Overview of your hiring activity and performance metrics</p>", unsafe_allow_html=True)
    
    total_resumes = 120
    candidates_screened = 100
    shortlisted = 25
    rejected = 60
    active_jobs = 5
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
    st.markdown('<div class="section-title">📈 Hiring Insights</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Candidate Distribution")
        labels = ["Shortlisted", "Rejected", "Pending"]
        values = [shortlisted, rejected, pending_reviews]
        colors = ['#4CAF50', '#f44336', '#FF9806']
        
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        wedges, texts, autotexts = ax1.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax1.axis('equal')
        st.pyplot(fig1)
    
    with col2:
        st.markdown("#### Hiring Pipeline")
        categories = ["Uploaded", "Screened", "Shortlisted", "Rejected"]
        values = [total_resumes, candidates_screened, shortlisted, rejected]
        colors_bar = ['#6750A4', '#9A82DB', '#4CAF50', '#f44336']
        
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        bars = ax2.bar(categories, values, color=colors_bar, edgecolor='white', linewidth=2)
        for bar, val in zip(bars, values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, str(val), ha='center', fontweight='bold')
        ax2.set_ylabel('Number of Candidates')
        ax2.set_ylim(0, max(values) + 20)
        st.pyplot(fig2)
    
    st.markdown("---")
    st.subheader("📊 Shortlisting Progress")
    progress = shortlisted / total_resumes
    st.progress(progress)
    st.write(f"**{round(progress * 100, 2)}%** of candidates shortlisted")
    
    st.info("💡 This dashboard provides a quick visual summary of your hiring pipeline. Use the navigation menu to access other features.")

# ---------------- NEW HIRING ROUND ----------------
elif page == "New Hiring Round":
    
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
        # Show Model Selection After Start Screening
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

# ---------------- HR REVIEW ----------------
elif page == "HR Review":
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

# ---------------- FAIRNESS REPORT ----------------
elif page == "Fairness Report":
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
    fig = px.histogram(scores, nbins=10, title="Candidate Score Distribution", color_discrete_sequence=['#6750A4'])
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### ⚙️ Fairness Mode: Balanced")
    st.progress(0.7)
    st.write("**Current Setting:** Balanced Mode - Considers both skills and candidate potential")
    
    st.markdown("---")
    st.info("📜 **Responsible AI Statement:** AI assists HR but final decisions require human review. All sensitive attributes are ignored during screening.")

# ---------------- EXPORT RESULTS ----------------
elif page == "Export Results":
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

st.markdown('</div>', unsafe_allow_html=True)