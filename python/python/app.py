# HOMESCREEN

import streamlit as st

# --------------- PAGE CONFIG ----------------
st.set_page_config(page_title="TrustLens", layout="wide")

# --------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_type" not in st.session_state:
    st.session_state.user_type = None

if "show_company_login" not in st.session_state:
    st.session_state.show_company_login = False

if "show_candidate_status" not in st.session_state:
    st.session_state.show_candidate_status = False

if "show_status_page" not in st.session_state:
    st.session_state.show_status_page = False

if "selected_candidate" not in st.session_state:
    st.session_state.selected_candidate = None

if "show_login_options" not in st.session_state:
    st.session_state.show_login_options = False    

if "login_type" not in st.session_state:
    st.session_state.login_type = None    


# --------------- SAMPLE CANDIDATE DATABASE ----------------
candidate_records = {
    "APP001": {
        "email": "user@gmail.com",
        "name": "Alice Johnson",
        "skills": "Python, Machine Learning, SQL",
        "status": "Accepted",
        "criteria": "Skill match, ML project experience, problem solving",
        "reason": "Strong ML portfolio and relevant internship experience",
        "improvement": "Improve system design knowledge"
    },
    "APP002": {
        "email": "test@gmail.com",
        "name": "Bob Smith",
        "skills": "Java, Spring Boot",
        "status": "Rejected",
        "criteria": "Backend development skills, project relevance",
        "reason": "Limited project experience related to job role",
        "improvement": "Work on real backend projects and improve API design skills"
    },
    "APP003": {
        "email": "candidate@gmail.com",
        "name": "Charlie Brown",
        "skills": "React, JavaScript, UI Design",
        "status": "Pending",
        "criteria": "Frontend development, UI/UX portfolio",
        "reason": "Application under review by HR team",
        "improvement": "Add more real-world UI projects"
    }
}


# --------------- SIMPLE COMPANY AUTH SYSTEM ----------------
users = {
    "company": {"admin@company.com": "1234"}
}

def login(email, password):
    if email in users["company"] and users["company"][email] == password:
        st.session_state.logged_in = True
        st.session_state.user_type = "company"
        return True
    return False


# --------------- HEADER ----------------
# --------------- HEADER ----------------
col1, col2, col3 = st.columns([2,6,2])

with col1:
    st.image("Gemini_Generated_Image_8urn5p8urn5p8urn.png", width=120)

with col2:
    st.markdown(
        "<h1 style='text-align:center;'>TrustLens</h1>",
        unsafe_allow_html=True
    )

with col3:

    if not st.session_state.logged_in:

        if not st.session_state.show_login_options:
            if st.button("🔐 Login"):
                st.session_state.show_login_options = True

        else:
            if st.button("🏢 Company"):
                st.session_state.login_type = "company"
                st.session_state.show_company_login = True
                st.session_state.show_candidate_status = False

            if st.button("👤 Candidate"):
                st.session_state.login_type = "candidate"
                st.session_state.show_candidate_status = True
                st.session_state.show_company_login = False

    else:
        st.success("Logged in as Company")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_type = None




# ---------------- HERO SECTION ----------------

st.markdown('<div class="section-space"></div>', unsafe_allow_html=True)

hero_col1, hero_col2 = st.columns([1.2,1], gap="large")

with hero_col1:

    st.markdown(
        '<div class="hero-title">🚀 Hire Smarter with AI-Powered Resume Screening</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero-text">Quickly filter and shortlist the best candidates using intelligent automation.</div>',
        unsafe_allow_html=True
    )

    st.button("Start Screening", use_container_width=True)

with hero_col2:

    st.image(
        "https://blog.loopcv.pro/content/images/2025/02/AI-powered-resume-builders.jpg",
        use_container_width=True
    )

    st.markdown(
        '<div class="hero-caption">AI Resume Screening Platform</div>',
        unsafe_allow_html=True
    )

st.markdown('<div class="section-space"></div>', unsafe_allow_html=True)



# ---------------- PROMOTIONAL / METRICS ----------------

st.markdown("## 🌟 Why Choose Us?")

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric("Resumes Screened", "10,000+")

with metric2:
    st.metric("Companies Onboarded", "500+")

with metric3:
    st.metric("Time Saved", "70%")

st.markdown('<div class="section-space"></div>', unsafe_allow_html=True)



# ---------------- FEATURES ----------------

st.markdown("## ⚙️ Core Features")

f1, f2, f3 = st.columns(3)

with f1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📄 Resume Parsing</div>
        <div class="feature-text">
        Extract structured data from PDF and DOCX resumes automatically.
        </div>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🤖 AI Candidate Ranking</div>
        <div class="feature-text">
        AI analyzes resumes and ranks candidates based on skills.
        </div>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📊 Analytics Dashboard</div>
        <div class="feature-text">
        Get insights on recruitment performance and candidate quality.
        </div>
    </div>
    """, unsafe_allow_html=True)


f4, f5, f6 = st.columns(3)

with f4:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">⚡ Bulk Upload</div>
        <div class="feature-text">
        Upload and analyze multiple resumes at once.
        </div>
    </div>
    """, unsafe_allow_html=True)

with f5:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">🎯 Skill Matching</div>
        <div class="feature-text">
        Match candidates with job requirements automatically.
        </div>
    </div>
    """, unsafe_allow_html=True)

with f6:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">📤 Export Candidates</div>
        <div class="feature-text">
        Export shortlisted candidates easily.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-space"></div>', unsafe_allow_html=True)



# ---------------- TESTIMONIALS ----------------

st.markdown("## ⭐ Testimonials")

t1, t2 = st.columns(2)

with t1:
    st.success("“Reduced hiring time drastically.” – HR Manager")

with t2:
    st.success("“Very efficient tool.” – Recruiter")

st.markdown('<div class="section-space"></div>', unsafe_allow_html=True)            

# --------------- COMPANY LOGIN ----------------
# --------------- COMPANY LOGIN ----------------
if st.session_state.show_company_login:

    c1,c2,c3 = st.columns([3,2,3])

    with c2:
        st.subheader("Company Login")

        email = st.text_input("Company Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if login(email, password):
                st.success("Login Successful!")
                st.session_state.show_company_login = False
                st.session_state.show_login_options = False

            else:
                st.error("Invalid credentials")


# --------------- CANDIDATE STATUS CHECK ----------------
# --------------- CANDIDATE STATUS CHECK ----------------
if st.session_state.show_candidate_status:

    c1,c2,c3 = st.columns([3,2,3])

    with c2:
        st.subheader("Candidate Application Status")

        email = st.text_input("Candidate Email")
        app_id = st.text_input("Application ID")

        if st.button("Check Status"):

            if app_id in candidate_records:

                record = candidate_records[app_id]

                if record["email"] == email:
                    st.session_state.selected_candidate = record
                    st.session_state.show_status_page = True

                else:
                    st.error("Email does not match the Application ID")

            else:
                st.error("Invalid Application ID")


# --------------- STATUS PAGE ----------------
if st.session_state.show_status_page:

    data = st.session_state.selected_candidate

    st.title("Application Status")

    st.success(f"Current Status: {data['status']}")

    st.markdown("### Candidate Details")

    st.table({
        "Field": [
            "Candidate Name",
            "Skills Identified",
            "Selection Criteria Considered",
            "Reason for Decision",
            "Suggested Improvements"
        ],
        "Details": [
            data["name"],
            data["skills"],
            data["criteria"],
            data["reason"],
            data["improvement"]
        ]
    })

    if st.button("Back"):
        st.session_state.show_status_page = False


st.markdown("---")


# --------------- HERO SECTION ----------------

st.markdown("""
<style>
.hero-title{
font-size:36px;
font-weight:700;
margin-bottom:10px;
}

.hero-text{
font-size:18px;
color:#444;
margin-bottom:20px;
}

.hero-caption{
font-size:22px;
font-weight:600;
text-align:center;
margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1.2,1])

with col1:
    st.markdown('<div class="hero-title">🚀 Hire Smarter with AI-Powered Resume Screening</div>', unsafe_allow_html=True)

    st.markdown('<div class="hero-text">Quickly filter and shortlist the best candidates using intelligent automation.</div>', unsafe_allow_html=True)

    st.button("Start Screening", use_container_width=True, key="start_screening_btn")

with col2:
    st.image(
        "https://blog.loopcv.pro/content/images/2025/02/AI-powered-resume-builders.jpg",
        use_container_width=True
    )

    st.markdown('<div class="hero-caption">AI Resume Screening</div>', unsafe_allow_html=True)

st.markdown("---")


# --------------- PROMOTIONAL ----------------
st.markdown("## 🌟 Why Choose Us?")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Resumes Screened", "10,000+")

with col2:
    st.metric("Companies Onboarded", "500+")

with col3:
    st.metric("Time Saved", "70%")


st.markdown("---")


# --------------- ABOUT ----------------
st.markdown("## ℹ️ About Our Platform")

st.write("""
Our AI-powered platform helps companies streamline hiring
by automatically screening and ranking resumes.
""")


st.markdown("---")


# --------------- FEATURES ----------------
st.markdown("## ⚙️ Core Features")

features = [
    "Resume Parsing (PDF, DOCX)",
    "AI-Based Ranking",
    "Skill Matching",
    "Bulk Upload",
    "Analytics Dashboard",
    "Export Candidates"
]

for f in features:
    st.write(f"✔️ {f}")


st.markdown("---")


# --------------- TESTIMONIALS ----------------
st.markdown("## ⭐ Testimonials")

col1, col2 = st.columns(2)

with col1:
    st.info("“Reduced hiring time drastically.” – HR Manager")

with col2:
    st.info("“Very efficient tool.” – Recruiter")


st.markdown("---")



# --------------- CONTACT ----------------
st.markdown("## 📧 Contact Us")

with st.form("contact"):

    name = st.text_input("Name")
    email = st.text_input("Email")
    msg = st.text_area("Message")

    submit = st.form_submit_button("Send")

    if submit:
        st.success("Message sent!")


st.markdown("---")


# --------------- FAQ ----------------
st.markdown("## ❓ FAQ")

with st.expander("How does AI screening work?"):
    st.write("AI evaluates resumes using skills and keywords.")

with st.expander("Is data secure?"):
    st.write("Yes, we use encryption and secure storage.")


st.markdown("---")


# --------------- FOOTER ----------------
st.markdown("""
© 2026 AI Resume Screening Platform  

Privacy Policy | Terms | Copyright
""")







