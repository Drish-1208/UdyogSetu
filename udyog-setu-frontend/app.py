import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Udyog Setu Maharashtra", layout="wide")

# CSS Injection for Full-Page Dark Theme & Glassmorphism
st.markdown("""
<style>
/* Overall dark theme setup & Header */
.stApp, [data-testid="stAppViewContainer"] {
    background-color: #0e1117 !important;
    background-image: linear-gradient(135deg, #0e1117 0%, #1a1e24 100%) !important;
    color: #e0e0e0;
}
[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: rgba(14, 17, 23, 0.98) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}

/* Glassmorphism Containers and Expanders (Distinct Ticket Borders) */
[data-testid="stVerticalBlockBorderWrapper"], 
[data-testid="stForm"], 
[data-testid="stExpander"] > div {
    background: rgba(30, 34, 43, 0.4) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important; 
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5) !important;
}

/* Distinct Ticket Borders (Streamlit Expanders) */
[data-testid="stExpander"] {
    border: 2px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 12px !important;
    background-color: rgba(30, 34, 43, 0.5) !important;
    margin-bottom: 12px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    background-color: transparent !important;
}
[data-testid="stExpander"] summary:hover {
    background-color: rgba(255, 255, 255, 0.05) !important;
}

/* Glassmorphism Inputs & Selectboxes */
div[data-baseweb="select"] > div,
div[data-baseweb="select"] div[role="button"],
div[data-baseweb="base-input"] > input,
div[data-baseweb="base-input"],
div[data-baseweb="input"] {
    background-color: rgba(30, 34, 43, 0.6) !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* Dropdown Menu List Items */
ul[data-baseweb="menu"] {
    background-color: #1a1e24 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}
li[data-baseweb="menu-item"] {
    color: #ffffff !important;
}
li[data-baseweb="menu-item"]:hover {
    background-color: rgba(255, 255, 255, 0.1) !important;
}

/* File Uploader Dropzone Fix */
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploadDropzone"] {
    background-color: rgba(30, 34, 43, 0.6) !important;
    background-image: none !important;
    border: 1px dashed rgba(255, 255, 255, 0.3) !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploaderDropzone"] *,
[data-testid="stFileUploadDropzone"] * {
    color: #ffffff !important;
    fill: #ffffff !important;
}

/* Dark Upload Button Fix */
[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploadDropzone"] button {
    background-color: rgba(20, 24, 31, 0.95) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    color: #ffffff !important;
}
[data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="stFileUploadDropzone"] button:hover {
    background-color: rgba(45, 52, 63, 0.95) !important;
    border-color: rgba(255, 255, 255, 0.4) !important;
}

/* Uploaded File Preview Box */
[data-testid="stUploadedFile"] {
    background-color: rgba(20, 24, 31, 0.9) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 8px !important;
}
[data-testid="stUploadedFile"] div, 
[data-testid="stUploadedFile"] span, 
[data-testid="stUploadedFile"] small {
    color: #ffffff !important;
}
[data-testid="stUploadedFile"] svg {
    fill: #ffffff !important;
}

/* General Button styling */
.stButton>button, 
.stFormSubmitButton>button {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(5px) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    transition: all 0.3s ease !important;
}
.stButton>button:hover, 
.stFormSubmitButton>button:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.1) !important;
}

/* Primary Button Override */
button[kind="primary"] {
    background: rgba(255, 75, 75, 0.2) !important;
    border: 1px solid rgba(255, 75, 75, 0.4) !important;
}
button[kind="primary"]:hover {
    background: rgba(255, 75, 75, 0.4) !important;
}

/* Text & metric overrides */
h1, h2, h3, h4, p, span, label {
    color: #f0f2f6 !important;
}
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
    color: #ffffff !important;
}

/* Tabs overriding */
button[data-baseweb="tab"] {
    background: transparent !important;
    color: #aaaaaa !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None
if "vault" not in st.session_state:
    st.session_state["vault"] = []  

def login_page():
    st.title("Udyog Setu Portal")
    
    tab1, tab2 = st.tabs(["Login", "Register New Business"])
    
    with tab1:
        st.subheader("Access your dashboard")
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Secure Login"):
            payload = {"username": email, "password": password}
            try:
                response = requests.post(f"{API_URL}/login/", data=payload)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state["access_token"] = data["access_token"]
                    st.session_state["user_name"] = email
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend server. Is FastAPI running?")

    with tab2:
        st.subheader("Create your enterprise account")
        reg_name = st.text_input("Full Legal Name")
        reg_email = st.text_input("Business Email Address", key="reg_email")
        reg_password = st.text_input("Create Password", type="password", key="reg_password")
        
        if st.button("Register Account"):
            if not reg_name or not reg_email or not reg_password:
                st.warning("Please fill in all fields.")
            else:
                payload = {
                    "full_name": reg_name,
                    "email": reg_email,
                    "password": reg_password
                }
                response = requests.post(f"{API_URL}/users/", json=payload)
                
                if response.status_code == 200:
                    st.success("Account created successfully! Switch to the Login tab.")
                elif response.status_code == 400:
                    st.error(response.json().get("detail", "This email is already registered."))

def onboarding_flow():
    st.title("Business Onboarding")
    st.markdown("Let's figure out exactly which licenses you need to operate in Maharashtra.")
    
    with st.form("onboarding_form"):
        sector = st.selectbox("Business Sector", ["Food", "Agriculture", "Textile", "Manufacturing", "IT/Tech", "Other"])
        employee_count = st.number_input("Estimated Number of Employees", min_value=1, value=5)
        hazardous = st.checkbox("Will your facility handle hazardous chemicals?")
        
        submitted = st.form_submit_button("Generate Required Checklist", type="primary")
        
        if submitted:
            payload = {
                "sector": sector,
                "employee_count": employee_count,
                "has_hazardous_chemicals": hazardous
            }
            headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
            
            response = requests.post(f"{API_URL}/onboarding/", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                st.success(data["message"])
                st.info(f"You require **{data['total_approvals_required']}** total approvals.")
                
                for approval in data["required_approvals"]:
                    st.markdown(f"- {approval}")
                
                app_payload = {"email": st.session_state["user_name"]} 
                app_response = requests.post(f"{API_URL}/applications/submit/", json=app_payload, headers=headers)
                
                if app_response.status_code == 200:
                    st.balloons()
                    st.success("Master application generated! Switching to dashboard...")
                    st.session_state["page"] = "applicant"
                    st.rerun()
            else:
                st.error("Failed to generate checklist.")

def applicant_dashboard():
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    response = requests.get(f"{API_URL}/dashboard/my-status/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        if "overall_status" not in data:
            st.title("Welcome to Udyog Setu!")
            st.info(data.get("message", "You haven't submitted any applications yet."))
            return

        st.title(f"Welcome back, {data['applicant']}")
        
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Overall Status", value=data["overall_status"])
            with col2:
                st.metric(label="Total Progress", value=f"{data['total_progress']}%")
            with col3:
                pending_count = len([t for t in data["department_breakdown"] if t['status'] != 'Approved'])
                st.metric(label="Pending Action Items", value=pending_count)
                
        st.divider()
        
        left_col, right_col = st.columns([1.5, 1])
        
        with left_col:
            st.subheader("Department Review Tickets")
            
            for ticket in data["department_breakdown"]:
                if ticket['status'] == "Approved":
                    progress_val = 100
                elif ticket['status'] == "In Review":
                    progress_val = 75
                elif ticket['status'] == "Pending":
                    progress_val = 25
                else:
                    progress_val = 50

                # Determine if ticket needs attention
                needs_action = ticket['status'] in ['Pending', 'Rejected']

                with st.expander(f"{ticket['department']} - {ticket['status']}", expanded=needs_action):
                    st.caption(f"Last Updated: {ticket['last_updated']}")
                    
                    if ticket['officer_comments']:
                        st.info(f"**Official Note:** {ticket['officer_comments']}")
                    else:
                        st.write("**Official Note:** Awaiting review from department officer.")
                    
                    st.progress(progress_val, text="Department Processing Stage")
                    
                    # NEW LOGIC: Unique upload interface embedded into specific tickets
                    if needs_action:
                        st.divider()
                        st.write(f"**Upload requirement: {ticket['department']}**")
                        uploaded_file = st.file_uploader(
                            "Attach clear, legible document", 
                            type=["pdf", "png", "jpg", "jpeg"], 
                            key=f"upload_{ticket['ticket_id']}"
                        )
                        
                        if st.button("Run AI Security Scan", key=f"scan_{ticket['ticket_id']}", use_container_width=True, type="primary"):
                            if uploaded_file is not None:
                                with st.spinner("AI Gatekeeper is analyzing the document..."):
                                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                                    data_payload = {
                                        "email": st.session_state["user_name"],
                                        "document_type": ticket['department'], 
                                        "ticket_id": ticket['ticket_id']
                                    }
                                    
                                    upload_res = requests.post(f"{API_URL}/documents/upload/", data=data_payload, files=files)
                                    
                                    if upload_res.status_code == 200:
                                        result = upload_res.json()
                                        meta = result.get("extracted_metadata", {})
                                        
                                        if meta.get("is_valid"):
                                            st.success("Passed AI Screening! Ticket updated and sent to officer.")
                                            # Optional: Save to vault implicitly here
                                        else:
                                            st.error(f"Rejected: {meta.get('screening_status', 'Mismatch detected.')}")
                                            
                                        # Let the user read the result before refreshing the dashboard status
                                        time.sleep(2.5)
                                        st.rerun()
                                    else:
                                        st.error("Upload failed. Check backend logs.")
                            else:
                                st.warning("Please attach a file first.")
        
        with right_col:
            st.subheader("Smart Vault")
            st.info("Your verified documents are stored here. You can attach them to future requirements.")
            
            vault_res = requests.get(f"{API_URL}/documents/vault/", headers=headers)
            
            if vault_res.status_code == 200:
                vault_data = vault_res.json().get("vault", [])
                
                if not vault_data:
                    st.write("Your vault is currently empty.")
                else:
                    for i, doc in enumerate(vault_data):
                        with st.container(border=True):
                            st.write(f"**{doc['type']}**")
                            st.caption(f"ID Number: {doc['number']} | Security Score: {int(doc['score'] * 100)}%")
                            
                            if st.button("Attach to Pending Tickets", key=f"vault_{doc['type']}_{i}", use_container_width=True):
                                st.success(f"{doc['type']} instantly attached to all requiring departments!")
                                st.balloons()
            else:
                st.error("Failed to load vault data from the server.")

def government_analytics():
    st.title("Government Officer Portal")
    
    desk_tab, analytics_tab = st.tabs(["Officer Approval Desk", "State Analytics"])
    
    with desk_tab:
        st.markdown("### Pending AI-Screened Applications")
        st.info("These applications have passed the AI Gatekeeper and require final human sign-off.")
        
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        res = requests.get(f"{API_URL}/admin/tickets/pending/", headers=headers)
        
        if res.status_code == 200:
            tickets = res.json().get("tickets", [])
            
            if not tickets:
                st.success("Inbox Zero! All AI-screened applications have been processed.")
            else:
                for t in tickets:
                    with st.container(border=True):
                        st.subheader(f"{t['applicant']} - {t['department']}")
                        st.warning(f"Current Status: **{t['status']}**")
                        st.write(f"**AI Note:** {t['current_note']}")
                        
                        with st.form(key=f"review_form_{t['ticket_id']}"):
                            official_comment = st.text_input("Official Officer Comment", placeholder="e.g., Verified against state records. Approved.")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                approve = st.form_submit_button("Approve Application", use_container_width=True, type="primary")
                            with col_b:
                                reject = st.form_submit_button("Reject Application", use_container_width=True)
                                
                            if approve or reject:
                                decision = "Approved" if approve else "Rejected"
                                payload = {
                                    "ticket_id": t['ticket_id'],
                                    "decision": decision,
                                    "comments": official_comment or f"Application {decision.lower()} by officer."
                                }
                                
                                patch_res = requests.patch(f"{API_URL}/admin/tickets/review/", json=payload, headers=headers)
                                if patch_res.status_code == 200:
                                    st.success(f"Ticket {decision} successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to update ticket.")
    
    with analytics_tab:
        st.markdown("### Real-time Bottleneck Analysis")
        response = requests.get(f"{API_URL}/admin/statistics/")
        if response.status_code == 200:
            data = response.json()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Registered Businesses", data["state_overview"]["total_registered_businesses"])
            col2.metric("Pending Reviews", data["department_bottlenecks"]["pending_reviews"])
            col3.metric("Approval Rate", data["department_bottlenecks"]["overall_approval_rate"])
            
            st.divider()
            st.bar_chart({
                "Approved": [data["department_bottlenecks"]["approved_licenses"]],
                "Pending": [data["department_bottlenecks"]["pending_reviews"]],
                "Rejected": [data["department_bottlenecks"]["rejected_applications"]]
            })

# --- Navigation Sidebar ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_Maharashtra.svg/200px-Seal_of_Maharashtra.svg.png", width=100)
    st.title("Navigation")
    
    if st.session_state.get("access_token"):
        if st.button("My Dashboard"):
            st.session_state["page"] = "applicant"
        if st.button("State Analytics"):
            st.session_state["page"] = "admin"
            
        if st.button("Logout", type="primary"):
            st.session_state["access_token"] = None
            st.session_state["user_name"] = None
            st.session_state["vault"] = []
            st.session_state["page"] = "login"
            st.rerun()
    else:
        st.session_state["page"] = "login"

# --- Page Routing ---
page = st.session_state.get("page", "login")

if not st.session_state["access_token"]:
    login_page()
elif page == "applicant":
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    check_status = requests.get(f"{API_URL}/dashboard/my-status/", headers=headers)
    
    if check_status.status_code == 200 and "overall_status" not in check_status.json():
        onboarding_flow()
    else:
        applicant_dashboard()
elif page == "admin":
    government_analytics()