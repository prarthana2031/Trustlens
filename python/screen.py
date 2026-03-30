import streamlit as st
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Company Dashboard", layout="wide")

# ---------------- SESSION STATE INITIALIZATION ----------------

if "decisions" not in st.session_state:
    st.session_state["decisions"] = {}

# ---------------- SIDEBAR ----------------
st.sidebar.title("📂 Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Dashboard",
        "New Hiring Round",
        "HR Review",
        "Fairness Report",
        "Export Results"
    ]
)

# ---------------- EMAIL FUNCTION ----------------
def send_email(to_email, subject, body):

    sender_email = "your_email@gmail.com"
    app_password = "your_app_password"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True

    except Exception as e:
        st.error(f"Email failed: {e}")
        return False


# ---------------- DASHBOARD ----------------
if page == "Dashboard":

    st.title("📊 Company Dashboard")
    st.markdown("### Overview of Hiring Activity")
    st.markdown("---")

    total_resumes = 120
    candidates_screened = 100
    shortlisted = 25
    rejected = 60
    active_jobs = 5
    pending_reviews = 15

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📄 Total Resumes", total_resumes)
        st.metric("✅ Shortlisted", shortlisted)

    with col2:
        st.metric("🤖 Screened", candidates_screened)
        st.metric("❌ Rejected", rejected)

    with col3:
        st.metric("💼 Active Jobs", active_jobs)
        st.metric("⏳ Pending Reviews", pending_reviews)

    st.markdown("---")

    st.markdown("## 📈 Hiring Insights")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Candidate Distribution")

        labels = ["Shortlisted", "Rejected", "Pending"]
        values = [shortlisted, rejected, pending_reviews]

        fig1, ax1 = plt.subplots()
        ax1.pie(values, labels=labels, autopct='%1.1f%%')
        ax1.axis('equal')

        st.pyplot(fig1)

    with col2:

        st.subheader("Hiring Pipeline Overview")

        categories = ["Uploaded", "Screened", "Shortlisted", "Rejected"]
        values = [total_resumes, candidates_screened, shortlisted, rejected]

        fig2, ax2 = plt.subplots()
        ax2.bar(categories, values)

        st.pyplot(fig2)

    st.markdown("---")

    st.subheader("📊 Shortlisting Progress")

    if total_resumes > 0:
        progress = shortlisted / total_resumes
        st.progress(progress)
        st.write(f"{round(progress * 100, 2)}% of candidates shortlisted")

    st.markdown("---")

    st.info("This dashboard provides a quick visual summary of your hiring pipeline.")


# ---------------- NEW HIRING ROUND ----------------
elif page == "New Hiring Round":

    st.title("🆕 New Hiring Round")

    job_roles = [
        "Software Engineer",
        "Data Scientist",
        "ML Engineer",
        "Frontend Developer"
    ]

    role = st.selectbox("Select Job Role", job_roles)
    custom_role = st.text_input("Or enter custom role")

    final_role = custom_role if custom_role else role

    job_desc = st.text_area("Job Description")

    st.subheader("⚖️ Fairness Settings")

    mode = st.radio("Fairness Mode", ["Strict", "Balanced", "Custom"])

    files = st.file_uploader(
        "Upload Resumes",
        type=["pdf", "docx", "jpg"],
        accept_multiple_files=True
    )

    if files:

        if len(files) > 30:
            st.error("❌ Max 30 files allowed")

        for f in files:
            if f.size > 30 * 1024 * 1024:
                st.error(f"❌ {f.name} exceeds 30MB")

    if st.button("Start Screening"):
        st.success(f"🚀 Screening started for {final_role}")


# ---------------- HR REVIEW ----------------
# ---------------- HR REVIEW ----------------
# ---------------- HR REVIEW ----------------
elif page == "HR Review":

    st.title("👩‍💼 HR Review & Candidate Ranking")

    import pandas as pd

    # Initialize session storage
    if "decisions" not in st.session_state:
        st.session_state.decisions = {}

    candidates = [
        {
            "app_no": "APP001",
            "name": "Alice Johnson",
            "email": "alice@gmail.com",
            "skills": "Python, ML, SQL",
            "reason": "Strong ML experience and ML projects",
            "linkedin": "https://linkedin.com/in/alice",
            "github": "https://github.com/alice"
        },
        {
            "app_no": "APP002",
            "name": "Bob Smith",
            "email": "bob@gmail.com",
            "skills": "Java, Spring Boot",
            "reason": "Good backend development experience",
            "linkedin": "https://linkedin.com/in/bob",
            "github": "https://github.com/bob"
        },
        {
            "app_no": "APP003",
            "name": "Charlie Brown",
            "email": "charlie@gmail.com",
            "skills": "React, JavaScript",
            "reason": "Strong frontend portfolio",
            "linkedin": "https://linkedin.com/in/charlie",
            "github": "https://github.com/charlie"
        }
    ]

    # Table header
    header = st.columns(8)
    header[0].markdown("**Application No**")
    header[1].markdown("**Name**")
    header[2].markdown("**Skills**")
    header[3].markdown("**Selection Criteria Reason**")
    header[4].markdown("**LinkedIn**")
    header[5].markdown("**GitHub**")
    header[6].markdown("**Accept**")
    header[7].markdown("**Reject**")

    st.markdown("---")

    for i, c in enumerate(candidates):

        cols = st.columns(8)

        cols[0].write(c["app_no"])
        cols[1].write(c["name"])
        cols[2].write(c["skills"])
        cols[3].write(c["reason"])

        cols[4].markdown(f"[Profile]({c['linkedin']})")
        cols[5].markdown(f"[Repo]({c['github']})")

        # Accept
        if st.button("Accept", key=f"a{i}"):
            st.session_state["decisions"][c["app_no"]] = "Accepted"

            subject = "Application Accepted"
            body = f"Congratulations {c['name']}! Your application has been accepted."

            send_email(c["email"], subject, body)

            st.success(f"{c['name']} Accepted")

        # Reject
        if st.button("Reject", key=f"r{i}"):
            st.session_state["decisions"][c["app_no"]] = "Rejected"
            subject = "Application Rejected"
            body = f"Dear {c['name']}, we regret to inform you that your application was not selected."

            send_email(c["email"], subject, body)

            st.warning(f"{c['name']} Rejected")

        st.markdown("---")

# ---------------- FAIRNESS REPORT ----------------
# ---------------- FAIRNESS REPORT ----------------
elif page == "Fairness Report":

    st.title("⚖ Fairness Report")

    st.markdown("---")

    # 📌 Screening Criteria
    st.subheader("📌 Screening Criteria")

    screening_data = {
        "Evaluation Factor": [
            "Skills Match",
            "Years of Experience",
            "Project Experience",
            "Education Relevance",
            "Keyword Matching"
        ],
        "Description": [
            "Checks how well candidate skills match job requirements",
            "Evaluates relevant work experience",
            "Analyzes projects mentioned in the resume",
            "Considers relevant educational qualifications",
            "Matches resume keywords with job description"
        ]
    }

    st.table(screening_data)

    st.markdown("---")

    # 🛡 Bias Prevention
    st.subheader("🛡 Bias Prevention")

    bias_data = {
        "Ignored Attribute": [
            "Name",
            "Gender",
            "Age",
            "Photo",
            "Nationality",
            "Religion",
            "Address"
        ],
        "Reason": [
            "Prevents identity-based bias",
            "Ensures gender neutrality",
            "Avoids age discrimination",
            "Prevents visual bias",
            "Ensures equal opportunity",
            "Avoids religious bias",
            "Prevents location-based discrimination"
        ]
    }

    st.table(bias_data)

    st.markdown("---")

    # 📉 Score Distribution
    st.subheader("📉 Score Distribution")

    score_distribution = {
        "Score Range": [
            "90 - 100",
            "80 - 89",
            "70 - 79",
            "Below 70"
        ],
        "Number of Candidates": [
            5,
            10,
            8,
            12
        ]
    }

    st.table(score_distribution)

    st.markdown("---")

    # ⚙ Fairness Modes
    st.subheader("⚙ Fairness Modes")

    fairness_modes = {
        "Mode": [
            "Strict Mode",
            "Balanced Mode",
            "Custom Mode"
        ],
        "Description": [
            "Only highly qualified candidates with strong skill match are shortlisted",
            "Considers both skills and candidate potential",
            "Allows HR to define custom screening rules"
        ]
    }

    st.table(fairness_modes)

    st.markdown("---")

    # 🧠 AI Decision Explanation
    st.subheader("🧠 AI Decision Explanation")

    explanation_data = {
        "Candidate": [
            "Alice",
            "Bob"
        ],
        "Score": [
            90,
            80
        ],
        "Reason for Score": [
            "Strong Python, ML, and SQL skills with relevant ML projects",
            "Good backend experience in Java and Spring but limited ML exposure"
        ]
    }

    st.table(explanation_data)

    st.markdown("---")

    # 📜 Responsible AI Statement
    st.subheader("📜 Responsible AI Statement")

    responsible_ai = {
        "Policy": [
            "Human Oversight",
            "Bias Prevention",
            "Transparency",
            "Fair Opportunity"
        ],
        "Explanation": [
            "AI assists HR but final decisions require human review",
            "Sensitive attributes are ignored during screening",
            "Candidates are evaluated based on skills and experience",
            "Every candidate is evaluated using the same criteria"
        ]
    }

    st.table(responsible_ai)


# ---------------- EXPORT RESULTS ----------------
# ---------------- EXPORT RESULTS ----------------
# ---------------- EXPORT RESULTS ----------------
# ---------------- EXPORT RESULTS ----------------
elif page == "Export Results":

    st.title("📤 Export Results")

    import pandas as pd
    from io import BytesIO

    # Candidate data
    candidates = [
        ["APP001", "Alice Johnson", "Python, ML, SQL"],
        ["APP002", "Bob Smith", "Java, Spring Boot"],
        ["APP003", "Charlie Brown", "React, JavaScript"]
    ]

    results = []

    for c in candidates:

        app_no = c[0]

        # Safe access of session state
        decision = st.session_state.get("decisions", {}).get(app_no, "Pending")

        results.append({
            "Application No": c[0],
            "Candidate Name": c[1],
            "Skills": c[2],
            "HR Decision": decision
        })

    df = pd.DataFrame(results)

    # Show table
    st.subheader("📋 Hiring Results Table")
    st.table(df)

    st.markdown("---")

    # Hiring summary
    st.subheader("📊 Hiring Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Candidates", len(df))
    col2.metric("Accepted", len(df[df["HR Decision"] == "Accepted"]))
    col3.metric("Rejected", len(df[df["HR Decision"] == "Rejected"]))

    st.markdown("---")

    st.subheader("⬇ Download Results")

    # CSV export
    csv = df.to_csv(index=False)

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="hiring_results.csv",
        mime="text/csv"
    )

    # Excel export (using openpyxl)
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    st.download_button(
        label="Download Excel",
        data=buffer.getvalue(),
        file_name="hiring_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )