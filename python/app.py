import streamlit as st
import pandas as pd
import numpy as np
import time
import hashlib
import json
import os

st.set_page_config(page_title="TruthLens", layout="wide")

# ----------------------------
# USER DATABASE
# ----------------------------
USER_DB = "users.json"

def load_users():
    if not os.path.exists(USER_DB):
        return {}
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ----------------------------
# SESSION STATE
# ----------------------------
if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "candidates" not in st.session_state:
    st.session_state.candidates = pd.DataFrame()

# ----------------------------
# GLOBAL STYLING
# ----------------------------
st.markdown("""
<style>
.hero {
    text-align: center;
    padding: 40px;
}
.title {
    font-size: 48px;
    font-weight: bold;
}
.subtitle {
    font-size: 20px;
    color: gray;
}
.section {
    padding: 25px;
    border-radius: 12px;
    background-color: #f7f9fc;
    margin-top: 20px;
}
.card {
    padding: 20px;
    border-radius: 12px;
    background-color: #f7f9fc;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# HOMEPAGE (Landing + Auth)
# ----------------------------
def homepage():
    st.markdown('<div class="hero">', unsafe_allow_html=True)

    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=120)
    st.markdown('<div class="title">TruthLens</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Fair • Transparent • AI-Powered Hiring</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # AUTH SECTION (Login + Signup Tabs)
    st.markdown('<div class="section">', unsafe_allow_html=True)
    tabs = st.tabs(["🔐 Login", "📝 Sign Up"])

    users = load_users()

    # LOGIN TAB
    with tabs[0]:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            if username in users and users[username] == hash_password(password):
                st.session_state.user = username
                st.success(f"Welcome {username}")
                st.session_state.page = "Dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials")

    # SIGNUP TAB
    with tabs[1]:
        new_user = st.text_input("New Username", key="signup_user")
        new_pass = st.text_input("New Password", type="password", key="signup_pass")

        if st.button("Create Account"):
            if new_user in users:
                st.error("User already exists")
            elif new_user and new_pass:
                users[new_user] = hash_password(new_pass)
                save_users(users)
                st.success("Account created! Please login.")
            else:
                st.error("Fill all fields")

    st.markdown("</div>", unsafe_allow_html=True)

    # ABOUT
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📖 About TruthLens")
    st.write("""
    TruthLens is an AI-powered hiring platform designed to ensure fair, transparent,
    and unbiased candidate selection.

    - AI-based candidate ranking  
    - Explainable decisions (SHAP)  
    - Fairness monitoring  
    - Data-driven hiring  
    """)
    st.markdown("</div>", unsafe_allow_html=True)

    # FEATURES
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("✨ Features")
    col1, col2, col3 = st.columns(3)
    col1.info("📊 Smart Ranking")
    col2.info("🧠 Explainable AI")
    col3.info("⚖️ Bias Detection")
    st.markdown("</div>", unsafe_allow_html=True)

    # ADVERTISEMENT
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("🔥 Why Choose TruthLens?")
    st.success("✔ Reduce hiring bias by 40%")
    st.success("✔ 3x faster hiring")
    st.success("✔ Transparent AI decisions")
    st.markdown("💡 Join companies transforming hiring with TruthLens.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# SIDEBAR
# ----------------------------
def sidebar():
    st.sidebar.title(f"👤 {st.session_state.user}")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.page = "Home"
        st.rerun()

    pages = [
        "Dashboard",
        "New Hiring Round",
        "Upload Resumes",
        "Candidate Ranking",
        "Candidate Detail",
        "Fairness Report",
        "Export Results"
    ]

    for p in pages:
        if st.sidebar.button(p):
            st.session_state.page = p
            st.rerun()

# ----------------------------
# LOGIN PROTECTION
# ----------------------------
def require_login():
    if not st.session_state.user:
        st.warning("Please login first")
        st.session_state.page = "Home"
        st.rerun()

# ----------------------------
# DASHBOARD
# ----------------------------
def dashboard():
    require_login()

    st.title("📊 Hiring Dashboard")

    # ----------------------------
    # TOP METRICS
    # ----------------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Active Rounds", 3)
    col2.metric("Total Candidates", 245)
    col3.metric("Avg Score", "78%")
    col4.metric("Shortlisted", 52)

    st.markdown("---")

    # ----------------------------
    # QUICK ACTIONS
    # ----------------------------
    st.subheader("⚡ Quick Actions")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕ New Hiring Round"):
            st.session_state.page = "New Hiring Round"
            st.rerun()

    with col2:
        if st.button("📂 Upload Resumes"):
            st.session_state.page = "Upload Resumes"
            st.rerun()

    st.markdown("---")

    # ----------------------------
    # HIRING ROUNDS (MAIN SECTION)
    # ----------------------------
    st.subheader("📁 Hiring Rounds")

    data = pd.DataFrame({
        "Role": ["Data Scientist", "Frontend Developer", "Backend Engineer"],
        "Date": ["2026-03-20", "2026-03-22", "2026-03-25"],
        "Candidates": [120, 85, 60],
        "Status": ["Ongoing", "Completed", "Ongoing"]
    })

    # Search Filter
    search = st.text_input("🔍 Search role")

    if search:
        data = data[data["Role"].str.contains(search, case=False)]

    # Card Layout
    cols = st.columns(3)

    for i, row in data.iterrows():
        with cols[i % 3]:
            st.markdown(f"""
            <div style="
                padding:20px;
                border-radius:12px;
                background-color:#f7f9fc;
                margin-bottom:15px;
                box-shadow:0px 4px 10px rgba(0,0,0,0.05);
            ">
                <h4>{row['Role']}</h4>
                <p><b>Date:</b> {row['Date']}</p>
                <p><b>Candidates:</b> {row['Candidates']}</p>
                <p><b>Status:</b> {row['Status']}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Open {row['Role']}", key=f"open_{i}"):
                st.session_state.page = "Candidate Ranking"
                st.rerun()

    st.markdown("---")

    # ----------------------------
    # ANALYTICS
    # ----------------------------
    st.subheader("📈 Analytics")

    col1, col2 = st.columns(2)

    with col1:
        scores = np.random.randint(50, 100, 50)
        st.write("Score Distribution")
        st.line_chart(scores)

    with col2:
        gender_data = pd.DataFrame({
            "Gender": ["Male", "Female"],
            "Count": [140, 105]
        }).set_index("Gender")

        st.write("Gender Distribution")
        st.bar_chart(gender_data)

    st.markdown("---")

    # ----------------------------
    # FAIRNESS SNAPSHOT
    # ----------------------------
    st.subheader("⚖️ Fairness Snapshot")

    col1, col2 = st.columns(2)

    col1.metric("Disparate Impact", "0.91")
    col2.metric("Bias Risk", "Low")

    st.bar_chart({
        "Male": 0.65,
        "Female": 0.60
    })

    st.markdown("---")

    # ----------------------------
    # RECENT ACTIVITY
    # ----------------------------
    st.subheader("🕒 Recent Activity")

    st.write("• 25 resumes uploaded for Data Scientist role")
    st.write("• Ranking completed for Backend Engineer")
    st.write("• Fairness report generated")

# ----------------------------
# NEW ROUND
# ----------------------------
def new_round():
    require_login()
    st.title("🆕 New Hiring Round")
    st.text_area("Job Description")

# ----------------------------
# UPLOAD
# ----------------------------
def upload():
    require_login()
    files = st.file_uploader("Upload resumes", accept_multiple_files=True)

    if files:
        st.session_state.candidates = pd.DataFrame({
            "Name": [f"Candidate {i+1}" for i in range(len(files))],
            "Score": np.random.randint(60, 100, len(files))
        })
        st.success("Resumes processed")

# ----------------------------
# RANKING
# ----------------------------
def ranking():
    require_login()
    df = st.session_state.candidates

    if df.empty:
        st.warning("Upload resumes first")
        return

    df = df.sort_values(by="Score", ascending=False)
    st.dataframe(df)

# ----------------------------
# DETAIL
# ----------------------------
def detail():
    require_login()
    st.write("Candidate detail page")

# ----------------------------
# FAIRNESS
# ----------------------------
def fairness():
    require_login()
    st.write("Fairness dashboard")

# ----------------------------
# EXPORT
# ----------------------------
def export():
    require_login()
    df = st.session_state.candidates

    if df.empty:
        st.warning("No data")
        return

    st.download_button("Download CSV", df.to_csv(index=False))

# ----------------------------
# ROUTER
# ----------------------------
if st.session_state.user:
    sidebar()

page = st.session_state.page

if page == "Home":
    homepage()
elif page == "Dashboard":
    dashboard()
elif page == "New Hiring Round":
    new_round()
elif page == "Upload Resumes":
    upload()
elif page == "Candidate Ranking":
    ranking()
elif page == "Candidate Detail":
    detail()
elif page == "Fairness Report":
    fairness()
elif page == "Export Results":
    export()

