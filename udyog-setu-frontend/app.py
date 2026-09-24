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
        
        # Handle new users who haven't finished onboarding
        if "overall_status" not in data:
            st.title("Welcome to Udyog Setu!")
            st.info(data.get("message", "You haven't submitted any applications yet."))
            return

        st.title(f"🏢 Welcome back, {data['applicant']}")
        st.markdown("Monitor your regulatory approvals and submit required documentation below.")
        
        # NEATER UI: Top-level metrics grouped in a styled card container
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Overall Status", value=data["overall_status"])
            with col2:
                # Add a % sign for better visual feedback
                st.metric(label="Total Progress", value=f"{data['total_progress']}%")
            with col3:
                # Calculate how many tickets are not approved yet
                pending_count = len([t for t in data["department_breakdown"] if t['status'] != 'Approved'])
                st.metric(label="Pending Action Items", value=pending_count)
                
        st.divider()
        
        # Split the screen into two neat columns: Tickets on the left, Uploads on the right
        left_col, right_col = st.columns([1.5, 1])
        
        with left_col:
            st.subheader("📋 Department Review Tickets")
            
            # TICKET EXPANSION: Richer ticket display with status icons and progress bars
            for ticket in data["department_breakdown"]:
                # Assign traffic-light icons based on status
                if ticket['status'] == "Approved":
                    status_icon = "🟢"
                    progress_val = 100
                elif ticket['status'] == "Pending":
                    status_icon = "🟠"
                    progress_val = 25
                else:
                    status_icon = "🔴"
                    progress_val = 50

                # Auto-expand tickets that still need attention
                with st.expander(f"{status_icon} {ticket['department']} - {ticket['status']}", expanded=(ticket['status'] == 'Pending')):
                    st.caption(f"Last Updated: {ticket['last_updated']}")
                    
                    if ticket['officer_comments']:
                        st.info(f"💬 **Official Note:** {ticket['officer_comments']}")
                    else:
                        st.write("💬 **Official Note:** Awaiting review from department officer.")
                    
                    # Visual progress bar for each ticket
                    st.progress(progress_val, text="Department Processing Stage")
        
        with right_col:
            st.subheader("📤 Document Center")
            
            # DOCUMENT UPLOAD: Fully functional upload widget connected to FastAPI
            with st.container(border=True):
                st.markdown("Upload required files for verification.")
                
                doc_type = st.selectbox("Select Document Type", [
                    "Company Registration (MCA)", 
                    "GST Registration", 
                    "Fire NOC", 
                    "Environmental Clearance",
                    "Identity Proof",
                    "Property Lease Agreement"
                ])
                
                uploaded_file = st.file_uploader("Upload PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
                
                if st.button("Secure Upload", use_container_width=True, type="primary"):
                    if uploaded_file is not None:
                        with st.spinner("Encrypting and uploading to server..."):
                            # Format the file for FastAPI's UploadFile
                            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                            
                            # Format the Form data
                            data_payload = {
                                "email": st.session_state["user_name"],
                                "document_type": doc_type
                            }
                            
                            # Fire off to your backend endpoint
                            upload_res = requests.post(f"{API_URL}/documents/upload/", data=data_payload, files=files)
                            
                            if upload_res.status_code == 200:
                                result = upload_res.json()
                                meta = result.get("extracted_metadata", {})
                                data = meta.get("extracted_data", {})
                                
                                st.success(f"✅ {doc_type} uploaded successfully!")
                                
                                # 🎨 NEAT UI: Beautiful AI Verification Card replaces raw JSON
                                with st.container(border=True):
                                    st.markdown("### 🤖 AI Verification Results")
                                    
                                    if meta.get("is_valid"):
                                        st.success("Status: **Verified & Valid**")
                                    else:
                                        st.error("Status: **Manual Review Required**")
                                        
                                    score = float(meta.get("confidence_score", 0.0))
                                    st.progress(score, text=f"AI Confidence Score: {int(score * 100)}%")
                                    
                                    st.divider()
                                    
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.caption("Document Number")
                                        st.write(f"**{data.get('document_number', 'N/A')}**")
                                        st.caption("Issue Date")
                                        st.write(f"**{data.get('issue_date', 'N/A')}**")
                                        
                                    with col_b:
                                        st.caption("Signatures Present")
                                        st.write(f"**{'Yes' if data.get('signatures_present') else 'No'}**")
                                        st.caption("Expiry Date")
                                        st.write(f"**{data.get('expiry_date', 'N/A')}**")
                                        
                                    if meta.get("critical_flags"):
                                        st.warning(f"🚩 **Flags:** {', '.join(meta['critical_flags'])}")
                            else:
                                st.error("Upload failed. Check backend logs.")
                    else:
                        st.warning("Please attach a file first.")
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