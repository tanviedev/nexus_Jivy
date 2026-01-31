import streamlit as st

# =========================================================
# SESSION STATE
# =========================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "hospital" not in st.session_state:
    st.session_state.hospital = None

if "page" not in st.session_state:
    st.session_state.page = "login"

if "pending_requests" not in st.session_state:
    st.session_state.pending_requests = []

# =========================================================
# LOAD CSS
# =========================================================
with open("frontend/styles.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="JIVY", layout="centered")

# =========================================================
# LOGIN PAGE
# =========================================================
def login_page():
    st.markdown("<h1 class='app-title'>🏥 JIVY</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='tagline'>When patient care can’t wait, JIVY doesn’t either.</p>",
        unsafe_allow_html=True
    )

    st.markdown("<div class='hospital-name'>CityCare Hospital</div>", unsafe_allow_html=True)

    st.markdown("<h3 class='login-header'>🔐 Secure Login</h3>", unsafe_allow_html=True)

    hospital = st.selectbox(
        "Hospital",
        ["CityCare Hospital", "Apollo Hospital", "Fortis Healthcare"]
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    role = st.selectbox("Login as", ["Doctor", "Operation's Manager","Hospital Admin"])

    if st.button("Login", type="primary"):
        if username and password:
            st.session_state.logged_in = True
            st.session_state.user_role = role
            st.session_state.hospital = hospital
            st.rerun()
        else:
            st.error("Please enter username and password")

    st.markdown("---")

    if st.button("New user? Request access"):
        st.session_state.page = "request_access"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# REQUEST ACCESS PAGE
# =========================================================
def request_access_page():
    st.markdown("<h1 class='app-title'>🏥 JIVY</h1>", unsafe_allow_html=True)
    st.subheader("📝 Request Access")

    st.caption("🔐 Credentials will be issued after admin approval.")

    with st.form("request_access_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Work Email")
        role = st.selectbox("Requested Role", ["Doctor", "Operation's Manager","Hospital Admin"])
        hospital = st.selectbox(
            "Hospital",
            ["CityCare Hospital", "Apollo Hospital", "Fortis Healthcare"]
        )

        submit = st.form_submit_button("Submit Request")

        if submit:
            if name and email:
                st.session_state.pending_requests.append({
                    "name": name,
                    "email": email,
                    "role": role,
                    "hospital": hospital
                })
                st.success("Access request submitted successfully.")
            else:
                st.error("Please fill all required fields.")

    if st.button("← Back to Login"):
        st.session_state.page = "login"
        st.rerun()

# =========================================================
# ADMIN APPROVAL PAGE
# =========================================================
def admin_approval_page():
    st.subheader("✅ Access Approval Panel")

    if not st.session_state.pending_requests:
        st.info("No pending access requests.")
        return

    for idx, req in enumerate(st.session_state.pending_requests):
        with st.expander(f"{req['name']} · {req['role']}"):
            st.write(f"📧 Email: {req['email']}")
            st.write(f"🏥 Hospital: {req['hospital']}")

            col1, col2 = st.columns(2)

            if col1.button("Approve", key=f"approve_{idx}"):
                st.success(f"Approved access for {req['name']}")
                st.session_state.pending_requests.pop(idx)
                st.rerun()

            if col2.button("Reject", key=f"reject_{idx}"):
                st.warning(f"Rejected access for {req['name']}")
                st.session_state.pending_requests.pop(idx)
                st.rerun()

# =========================================================
# DASHBOARD PAGE
# =========================================================
def dashboard_page():
    st.success(f"Welcome to JIVY · {st.session_state.hospital}")
    st.write(f"Role: {st.session_state.user_role}")

    st.markdown("---")

    if st.session_state.user_role == "Doctor":
        st.subheader("🩺 Doctor Dashboard")
        st.write("• Patient risk overview")
        st.write("• Escalation recommendations")

    else:
        st.subheader("🏥 Hospital Admin Dashboard")
        st.write("• ICU bed availability")
        st.write("• Staff workload")
        st.write("• Hospital pressure index")

        st.markdown("---")
        admin_approval_page()

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.hospital = None
        st.session_state.page = "login"
        st.rerun()

# =========================================================
# ROUTER
# =========================================================
if st.session_state.page == "login":
    if st.session_state.logged_in:
        dashboard_page()
    else:
        login_page()

elif st.session_state.page == "request_access":
    request_access_page()
