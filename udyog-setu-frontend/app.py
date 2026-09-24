import streamlit as st
import requests

# Point this to your FastAPI backend
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Udyog Setu Maharashtra", page_icon="🏛️", layout="wide")

# Initialize session state for user login
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

def login_page():
    st.title("🏛️ Udyog Setu Portal")
    
    # Create two elegant tabs
    tab1, tab2 = st.tabs(["🔒 Login", "📝 Register New Business"])
    
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
                    st.success("Account created successfully! Switch to the Login tab to access your dashboard.")
                elif response.status_code == 400:
                    st.error(response.json().get("detail", "This email is already registered."))

def onboarding_flow():
    st.title("📋 Business Onboarding")
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
            
            # Call the secure backend rules engine
            response = requests.post(f"{API_URL}/onboarding/", json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                st.success(data["message"])
                st.info(f"You require **{data['total_approvals_required']}** total approvals.")
                
                for approval in data["required_approvals"]:
                    st.markdown(f"- ✅ {approval}")
                
                # Automatically submit master application to spawn parallel department tickets
                app_payload = {"email": st.session_state["user_name"]} 
                app_response = requests.post(f"{API_URL}/applications/submit/", json=app_payload, headers=headers)
                
                if app_response.status_code == 200:
                    st.balloons()
                    st.success("Your master application has been generated and sent to all departments! Switching to dashboard...")
                    st.session_state["page"] = "applicant"
                    st.rerun()
            else:
                st.error("Failed to generate checklist. Please try again.")

def applicant_dashboard():
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    response = requests.get(f"{API_URL}/dashboard/my-status/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        # 1. FIX THE RED ERROR BOX: Check if the user has no applications yet
        if "overall_status" not in data:
            st.title("Welcome to Udyog Setu!")
            st.info(data.get("message", "You haven't submitted any applications yet."))
            st.markdown("*(Hint: Use the FastAPI docs to submit an application to see your metrics!)*")
            return # This stops the code here so the red error box doesn't happen!

        # 2. FIX THE NAME: Use the actual Full Name from the backend data
        st.title(f"Welcome back, {data['applicant']}")
        st.markdown("### Your Active Applications")
        
        # Display high-level progress
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Overall Status", value=data["overall_status"])
        with col2:
            st.metric(label="Total Progress", value=data["total_progress"])
            
        st.divider()
        st.subheader("Department Breakdown")
        
        # Display tickets
        for ticket in data["department_breakdown"]:
            with st.expander(f"{ticket['department']} - {ticket['status']}"):
                st.write(f"**Last Updated:** {ticket['last_updated']}")
                st.write(f"**Official Comments:** {ticket['officer_comments']}")
    else:
        st.warning("Your session has expired or no data was found.")

def government_analytics():
    st.title("📊 State Analytics Dashboard")
    st.markdown("Real-time bottleneck analysis for the state of Maharashtra.")
    
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
    
    if st.session_state["access_token"]:
        if st.button("My Dashboard"):
            st.session_state["page"] = "applicant"
        if st.button("State Analytics"):
            st.session_state["page"] = "admin"
        if st.button("Logout", type="primary"):
            st.session_state["access_token"] = None
            st.rerun()
    else:
        st.session_state["page"] = "login"

# --- Page Routing ---
page = st.session_state.get("page", "login")

if not st.session_state["access_token"]:
    login_page()
elif page == "applicant":
    # Check if the user has applications. If not, force them to Onboarding!
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    check_status = requests.get(f"{API_URL}/dashboard/my-status/", headers=headers)
    
    if check_status.status_code == 200 and "overall_status" not in check_status.json():
        onboarding_flow()
    else:
        applicant_dashboard()
elif page == "admin":
    government_analytics()