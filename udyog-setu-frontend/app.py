import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Udyog Setu Maharashtra", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"] {
    background-color: #0e1117 !important;
    background-image: linear-gradient(135deg, #0e1117 0%, #1a1e24 100%) !important;
    color: #e0e0e0;
}
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #0e1117; }
::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.4); }

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

[data-testid="stHeader"] { background-color: transparent !important; }
[data-testid="stHeaderActionElements"] { display: none !important; }

[data-testid="stSidebar"] {
    background-color: rgba(14, 17, 23, 0.98) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}

[data-testid="stVerticalBlockBorderWrapper"], [data-testid="stForm"], [data-testid="stExpander"] > div {
    background: rgba(30, 34, 43, 0.4) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-radius: 16px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important; 
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5) !important;
    animation: fadeIn 0.6s ease-out forwards;
}

[data-testid="stExpander"] {
    border: 2px solid rgba(255, 255, 255, 0.3) !important;
    border-radius: 12px !important;
    background-color: rgba(30, 34, 43, 0.5) !important;
    margin-bottom: 12px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary { background-color: transparent !important; }
[data-testid="stExpander"] summary:hover { background-color: rgba(255, 255, 255, 0.05) !important; }

div[data-baseweb="select"] > div, div[data-baseweb="base-input"] > input, div[data-baseweb="input"], textarea[data-baseweb="textarea"] {
    background-color: rgba(30, 34, 43, 0.6) !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

[data-testid="stFileUploaderDropzone"] {
    background-color: rgba(30, 34, 43, 0.6) !important;
    border: 1px dashed rgba(255, 255, 255, 0.3) !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploaderDropzone"] * { color: #ffffff !important; fill: #ffffff !important; }

.stButton>button, .stFormSubmitButton>button {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(5px) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    transition: all 0.3s ease !important;
}
.stButton>button:hover, .stFormSubmitButton>button:hover {
    background: rgba(255, 255, 255, 0.15) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
}

button[kind="primary"] {
    background: rgba(76, 175, 80, 0.2) !important;
    border: 1px solid rgba(76, 175, 80, 0.4) !important;
}
button[kind="primary"]:hover { background: rgba(76, 175, 80, 0.4) !important; }

h1, h2, h3, h4, p, span, label { color: #f0f2f6 !important; }
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "active_app_id" not in st.session_state:
    st.session_state["active_app_id"] = None
if "generated_certificate" not in st.session_state:
    st.session_state["generated_certificate"] = None

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_Maharashtra.svg/200px-Seal_of_Maharashtra.svg.png", width=100)
    st.title("Navigation")
    
    if st.session_state.get("access_token"):
        if st.button("Home"):
            st.session_state["page"] = "welcome"
            st.rerun()
        if st.button("My Profile"):
            st.session_state["page"] = "profile"
            st.rerun()
        if st.button("My Dashboard"):
            st.session_state["page"] = "applicant"
            st.rerun()
        if st.button("Apply for Business"):
            st.session_state["page"] = "onboarding"
            st.rerun()
        if st.button("Officer Approval Desk"):
            st.session_state["page"] = "admin"
            st.rerun()
            
        if st.button("Logout", type="primary"):
            st.session_state["access_token"] = None
            st.session_state["user_name"] = None
            st.session_state["active_app_id"] = None
            st.session_state["generated_certificate"] = None
            st.session_state["page"] = "login"
            st.rerun()
    else:
        st.write("Please log in to access your portal.")

def login_page():
    spacer_left, main_col, spacer_right = st.columns([1, 2, 1])
    with main_col:
        st.title("Udyog Setu Portal")
        st.write("Welcome to the Maharashtra Single Window Clearance System.")
        st.divider()
        tab1, tab2 = st.tabs(["Login", "Register New Business"])
        with tab1:
            st.subheader("Access your dashboard")
            email = st.text_input("Email Address", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Secure Login", use_container_width=True, type="primary"):
                payload = {"username": email, "password": password}
                try:
                    response = requests.post(f"{API_URL}/login/", data=payload)
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state["access_token"] = data["access_token"]
                        st.session_state["user_name"] = email
                        st.success("Login successful!")
                        time.sleep(1)
                        st.session_state["page"] = "welcome"
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
            if st.button("Register Account", use_container_width=True, type="primary"):
                if not reg_name or not reg_email or not reg_password:
                    st.warning("Please fill in all fields.")
                else:
                    payload = {"full_name": reg_name, "email": reg_email, "password": reg_password}
                    response = requests.post(f"{API_URL}/users/", json=payload)
                    if response.status_code == 200:
                        st.success("Account created successfully! Switch to the Login tab.")
                    elif response.status_code == 400:
                        st.error(response.json().get("detail", "This email is already registered."))

def welcome_page():
    spacer_left, main_col, spacer_right = st.columns([1, 3, 1])
    with main_col:
        st.markdown("<h1 style='text-align: center; font-size: 3em; margin-bottom: 0;'>Welcome to Udyog Setu</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 1.2em; color: #aaaaaa;'>Maharashtra Single Window Clearance System</p>", unsafe_allow_html=True)
        st.divider()
        st.write("Udyog Setu accelerates your enterprise journey by providing a unified, AI-driven portal for all your business licensing and registration needs.")
        st.markdown("### Next Steps")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Apply for New Business", use_container_width=True, type="primary"):
                st.session_state["page"] = "onboarding"
                st.rerun()
        with c2:
            if st.button("View My Profile", use_container_width=True):
                st.session_state["page"] = "profile"
                st.rerun()
        with c3:
            if st.button("Access Dashboard", use_container_width=True):
                st.session_state["page"] = "applicant"
                st.rerun()

def profile_page():
    st.title("My Profile")
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    user_res = requests.get(f"{API_URL}/users/me/", headers=headers)
    if user_res.status_code == 200:
        user_data = user_res.json()
        with st.container(border=True):
            col1, col2 = st.columns([1, 4])
            with col1:
                full_name = user_data.get('full_name', 'User Name')
                initials = "".join([n[0] for n in full_name.split() if n]).upper()[:2]
                st.markdown(f"<div style='background:rgba(255,255,255,0.1); border-radius:50%; width:100px; height:100px; display:flex; align-items:center; justify-content:center; font-size:36px; font-weight:bold; border: 2px solid rgba(255,255,255,0.2);'>{initials}</div>", unsafe_allow_html=True)
            with col2:
                st.subheader(full_name)
                st.write(f"**Email Address:** {user_data.get('email', 'N/A')}")
                st.write(f"**System Role:** {user_data.get('role', 'N/A').capitalize()}")
    st.divider()
    st.subheader("My Registered Businesses")
    app_res = requests.get(f"{API_URL}/applications/my-applications/", headers=headers)
    if app_res.status_code == 200:
        applications = app_res.json()
        if not applications:
            st.info("You haven't registered any businesses yet.")
            if st.button("Register a Business Now", type="primary"):
                st.session_state["page"] = "onboarding"
                st.rerun()
        else:
            cols = st.columns(2)
            for i, app in enumerate(applications):
                with cols[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"### {app['name']}")
                        st.caption(f"Date Created: {app['date'][:10]}")
                        status_lower = app['status'].lower()
                        if "approved" in status_lower: st.success(f"Status: {app['status']}")
                        elif "review" in status_lower or "pending" in status_lower: st.warning(f"Status: {app['status']}")
                        else: st.error(f"Status: {app['status']}")
                        if st.button("Open Dashboard", key=f"open_{app['id']}", use_container_width=True):
                            st.session_state["active_app_id"] = app['id']
                            st.session_state["page"] = "applicant"
                            st.rerun()

def onboarding_flow():
    _, main_col, _ = st.columns([1, 3, 1])
    with main_col:
        st.title("Apply for New Business")
        st.markdown("Provide detailed information about your enterprise. Our AI will automatically generate the exact legal compliance tickets required for your operation.")
        with st.form("onboarding_form"):
            st.subheader("1. General Information")
            business_name = st.text_input("Business Name", placeholder="e.g., Global Tech Solutions")
            sector = st.selectbox("Business Sector", ["Food & Beverage", "Agriculture", "Textile & Garments", "Heavy Manufacturing", "IT/Tech", "Pharmaceuticals", "Other"])
            description = st.text_area("Brief Description of Business Operations", placeholder="e.g., We manufacture and export woven cotton garments...")
            st.subheader("2. Operational Scale")
            col1, col2 = st.columns(2)
            with col1:
                employee_count = st.number_input("Estimated Number of Employees", min_value=1, value=5)
                factory_area_sqft = st.number_input("Facility/Factory Area (in sq. ft.)", min_value=100, value=1500)
            with col2:
                investment_tier = st.selectbox("Total Investment Tier", ["Micro (< ₹1 Crore)", "Small (₹1 - ₹10 Crore)", "Medium (₹10 - ₹50 Crore)", "Large (> ₹50 Crore)"])
            st.subheader("3. Environmental Factors")
            col3, col4 = st.columns(2)
            with col3: hazardous = st.checkbox("Will your facility handle hazardous chemicals or emissions?")
            with col4: water_usage = st.checkbox("Requires high ground-water usage or produces chemical effluent?")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Generate AI Compliance Checklist & Apply", type="primary", use_container_width=True)
            if submitted:
                if not business_name or not description:
                    st.warning("Please fill in the Business Name and Description.")
                else:
                    payload = {"business_name": business_name, "sector": sector, "description": description, "employee_count": employee_count, "investment_tier": investment_tier, "factory_area_sqft": factory_area_sqft, "has_hazardous_chemicals": hazardous, "high_water_usage": water_usage}
                    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
                    with st.spinner("AI Gatekeeper is reading Maharashtra State laws to generate your checklist..."):
                        response = requests.post(f"{API_URL}/onboarding/", json=payload, headers=headers)
                        if response.status_code == 200:
                            data = response.json()
                            st.success("Successfully generated compliance tickets via AI!")
                            st.info(f"You require **{data['total_tickets']}** approvals across various departments.")
                            st.balloons()
                            st.session_state["active_app_id"] = data.get("application_id")
                            time.sleep(2)
                            st.session_state["page"] = "applicant"
                            st.rerun()

def applicant_dashboard():
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    params = {}
    if st.session_state.get("active_app_id"):
        params["app_id"] = st.session_state["active_app_id"]
    response = requests.get(f"{API_URL}/dashboard/my-status/", headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if "overall_status" not in data:
            st.title("Welcome to Udyog Setu!")
            st.info(data.get("message", "You haven't submitted any applications yet."))
            if st.button("Apply for Business", type="primary"):
                st.session_state["page"] = "onboarding"
                st.rerun()
            return

        st.title(f"Dashboard: {data.get('business_name', 'My Business')}")
        st.write(f"Applicant: {data['applicant']}")
        
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1: st.metric(label="Overall Status", value=data["overall_status"])
            with col2: st.metric(label="Total Progress", value=data["total_progress"])
            with col3:
                pending_count = len([t for t in data["department_breakdown"] if t['status'] != 'Approved'])
                st.metric(label="Pending Action Items", value=pending_count)
                
        st.divider()

        total_tickets = len(data["department_breakdown"])
        approved_tickets = len([t for t in data["department_breakdown"] if t['status'] == 'Approved'])
        all_approved = (total_tickets > 0 and approved_tickets == total_tickets)

        if all_approved:
            with st.container(border=True):
                st.markdown("""
                <div style="border-left: 4px solid #4CAF50; padding: 12px; background: rgba(76, 175, 80, 0.1); border-radius: 8px;">
                    <h3 style="margin:0; color:#4CAF50;">Consolidated Master Clearance Granted</h3>
                    <p style="margin:0; padding-top:4px; color:#e0e0e0;">All regulatory departments have approved your submissions. Your official Consent to Establish certificate can now be generated.</p>
                </div>
                """, unsafe_allow_html=True)
                st.write("")
                if st.button("Generate Master Clearance to Establish Certificate", type="primary", use_container_width=True):
                    with st.spinner("Generating official certificate via Gemini AI Engine..."):
                        app_target_id = st.session_state.get("active_app_id") or data.get("application_id", "")
                        cert_res = requests.post(f"{API_URL}/certificates/generate/", json={"application_id": app_target_id}, headers=headers)
                        if cert_res.status_code == 200:
                            cert_data = cert_res.json()
                            st.session_state["generated_certificate"] = cert_data["certificate_text"]
                            st.success("Official Certificate Generated Successfully!")

            if st.session_state.get("generated_certificate"):
                st.markdown("### Official Clearance to Establish Industry Certificate")
                with st.container(border=True):
                    st.text_area("Certificate View", value=st.session_state["generated_certificate"], height=350, disabled=True)
                    st.download_button(label="Download Official Certificate", data=st.session_state["generated_certificate"], file_name=f"{data.get('business_name', 'Enterprise').replace(' ', '_')}_Clearance_Certificate.txt", mime="text/plain", type="primary", use_container_width=True)
            st.divider()

        left_col, right_col = st.columns([1.5, 1])
        with left_col:
            st.subheader("Department Review Tickets")
            for ticket in data["department_breakdown"]:
                status_lower = ticket['status'].lower()
                if "approved" in status_lower: progress_val, status_alert = 100, st.success
                elif "review" in status_lower: progress_val, status_alert = 75, st.warning
                elif "pending submission" in status_lower: progress_val, status_alert = 25, st.info
                elif "pending" in status_lower: progress_val, status_alert = 50, st.warning
                else: progress_val, status_alert = 10, st.error

                needs_upload = "pending submission" in status_lower or "rejected" in status_lower

                with st.expander(f"{ticket['department']} - {ticket['license_name']}", expanded=needs_upload):
                    st.caption(f"SLA: {ticket.get('sla', 'N/A')} | Last Updated: {ticket['last_updated'][:10]}")
                    if ticket['officer_comments']: status_alert(f"Status: {ticket['status']} | Note: {ticket['officer_comments']}")
                    else: status_alert(f"Status: {ticket['status']}")
                    st.progress(progress_val, text="Department Processing Stage")
                    
                    if needs_upload:
                        st.divider()
                        st.write(f"**Required Document:** {ticket.get('document_required', 'Standard Document')}")
                        uploaded_file = st.file_uploader("Attach clear, legible document", type=["pdf", "png", "jpg", "jpeg"], key=f"upload_{ticket['ticket_id']}")
                        if st.button("Run AI Security Scan & Submit", key=f"scan_{ticket['ticket_id']}", use_container_width=True, type="primary"):
                            if uploaded_file is not None:
                                with st.spinner("AI Gatekeeper is analyzing the document..."):
                                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                                    data_payload = {"email": st.session_state.get("user_name", ""), "document_type": ticket.get('document_required', ticket['department']), "ticket_id": ticket['ticket_id']}
                                    upload_res = requests.post(f"{API_URL}/documents/upload/", data=data_payload, files=files)
                                    if upload_res.status_code == 200:
                                        meta = upload_res.json().get("extracted_metadata", {})
                                        if meta.get("is_valid"): st.success("Passed AI Screening! Ticket updated and sent to officer.")
                                        else: st.error(f"Rejected: {meta.get('screening_status', 'Mismatch detected.')}")
                                        time.sleep(2.5)
                                        st.rerun()
        with right_col:
            st.subheader("Smart Vault")
            st.info("Your verified documents are stored here. You can attach them to future requirements.")
            with st.container(border=True):
                st.markdown("#### Upload to Vault")
                vault_doc_type = st.selectbox("Select Document Type", ["Identity Proof", "Company Registration (MCA)", "GST Registration", "Fire NOC", "Environmental Clearance", "Property Lease Agreement", "Floor Plan"], key="vault_doc_type")
                vault_file = st.file_uploader("Upload PDF or Image", type=["pdf", "png", "jpg", "jpeg"], key="vault_file_uploader")
                if st.button("Verify & Save to Vault", use_container_width=True, key="vault_upload_btn", type="primary"):
                    if vault_file is not None:
                        with st.spinner("AI Gatekeeper is analyzing the document..."):
                            files = {"file": (vault_file.name, vault_file.getvalue(), vault_file.type)}
                            data_payload = {"email": st.session_state.get("user_name", ""), "document_type": vault_doc_type, "ticket_id": ""}
                            upload_res = requests.post(f"{API_URL}/documents/upload/", data=data_payload, files=files)
                            if upload_res.status_code == 200:
                                meta = upload_res.json().get("extracted_metadata", {})
                                extract = meta.get("extracted_data", {})
                                if meta.get("is_valid"):
                                    st.success(f"Verified and added {vault_doc_type} to Smart Vault!")
                                    time.sleep(3)
                                    st.rerun()
                                else: st.error(f"Rejected: {meta.get('screening_status', 'Mismatch detected.')}")
            
            vault_res = requests.get(f"{API_URL}/documents/vault/", headers=headers)
            if vault_res.status_code == 200:
                vault_data = vault_res.json().get("vault", [])
                if not vault_data: st.write("Your vault is currently empty.")
                else:
                    actionable_tickets = [t for t in data["department_breakdown"] if t["status"] in ["Pending Submission", "Pending", "Rejected"]]
                    for i, doc in enumerate(vault_data):
                        with st.container(border=True):
                            st.markdown(f"<div style='border-left: 4px solid #4CAF50; padding-left: 12px; margin-bottom: 8px; background: rgba(76, 175, 80, 0.05); border-radius: 4px; padding-top: 8px; padding-bottom: 8px;'><h4 style='margin:0; padding:0; color:#fff;'>{doc['type']}</h4><p style='margin:0; padding-top:4px; color:#bbb; font-size: 0.85em;'>ID Number: {doc['number']} | Security Score: {int(doc['score'] * 100)}%</p></div>", unsafe_allow_html=True)
                            if actionable_tickets:
                                ticket_options = {f"{t['department']} - {t['license_name']} ({t['status']})": t['ticket_id'] for t in actionable_tickets}
                                selected_ticket_label = st.selectbox(f"Attach to Ticket", options=list(ticket_options.keys()), key=f"vault_select_{i}")
                                selected_ticket_id = ticket_options[selected_ticket_label]
                                if st.button(f"Attach Document to Selected Ticket", key=f"vault_attach_{i}", use_container_width=True):
                                    attach_res = requests.post(f"{API_URL}/tickets/attach-vault/", json={"ticket_id": selected_ticket_id, "document_type": doc['type']}, headers=headers)
                                    if attach_res.status_code == 200:
                                        st.success(f"{doc['type']} successfully attached to selected ticket!")
                                        time.sleep(1.5)
                                        st.rerun()

def government_analytics():
    st.title("Government Officer Portal")
    desk_tab, analytics_tab = st.tabs(["Officer Approval Desk", "State Analytics"])
    with desk_tab:
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        res = requests.get(f"{API_URL}/admin/tickets/pending/", headers=headers)
        if res.status_code == 200:
            tickets = res.json().get("tickets", [])
            col_m1, col_m2 = st.columns(2)
            with col_m1: st.metric("Pending Officer Reviews", len(tickets))
            with col_m2: st.metric("Processing Queue Status", "Chronological (Oldest First)")
            st.divider()
            if not tickets: st.success("Inbox Zero! All AI-screened applications have been processed.")
            else:
                for t in tickets:
                    with st.container(border=True):
                        ticket_col, doc_col = st.columns([1.1, 0.9])
                        with ticket_col:
                            st.markdown(f"### {t['applicant']}")
                            st.write(f"**Department:** {t['department']}")
                            st.write(f"**Approval Type:** {t.get('license_type', 'General')}")
                            # Clearly state required document for the officer
                            st.markdown(f"<p style='color:#4CAF50; font-weight:bold; margin-bottom:4px;'>Required Document: {t.get('required_document', 'Standard Document')}</p>", unsafe_allow_html=True)
                            st.caption(f"Submitted At: {t.get('submitted_at', 'N/A')}")
                            
                            status_lower = t['status'].lower()
                            if "approved" in status_lower: st.success(f"Current Status: **{t['status']}**")
                            elif "review" in status_lower or "pending" in status_lower: st.warning(f"Current Status: **{t['status']}**")
                            else: st.error(f"Current Status: **{t['status']}**")
                                
                            st.info(f"**AI Gatekeeper Note:** {t['current_note']}")
                            with st.form(key=f"review_form_{t['ticket_id']}"):
                                official_comment = st.text_input("Official Officer Comment", placeholder="e.g., Verified against state records. Approved.")
                                col_a, col_b = st.columns(2)
                                with col_a: approve = st.form_submit_button("Approve Application", use_container_width=True, type="primary")
                                with col_b: reject = st.form_submit_button("Reject Application", use_container_width=True)
                                if approve or reject:
                                    decision = "Approved" if approve else "Rejected"
                                    patch_res = requests.patch(f"{API_URL}/admin/tickets/review/", json={"ticket_id": t['ticket_id'], "decision": decision, "comments": official_comment or f"Application {decision.lower()} by officer."}, headers=headers)
                                    if patch_res.status_code == 200:
                                        st.success(f"Ticket {decision} successfully!")
                                        time.sleep(1)
                                        st.rerun()
                        with doc_col:
                            st.markdown("#### Document & Verification")
                            if t.get("document"):
                                doc_info = t["document"]
                                meta = doc_info.get("metadata", {})
                                extract = meta.get("extracted_data", {})
                                score = meta.get("confidence_score", 0.0)
                                st.progress(score, text=f"AI Confidence Score: {int(score * 100)}%")
                                st.write(f"**Document Number:** {extract.get('document_number', 'N/A')}")
                                st.write(f"**Issue Date:** {extract.get('issue_date', 'N/A')}")
                                st.write(f"**Expiry Date:** {extract.get('expiry_date', 'N/A')}")
                                st.write(f"**Signatures Verified:** {'Yes' if extract.get('signatures_present') else 'No'}")
                                st.divider()
                                file_url = doc_info.get("file_url", "#")
                                st.markdown(f"**Original File:** <a href='{file_url}' target='_blank' style='color:#4CAF50; font-weight:bold; text-decoration:none;'>Open Uploaded Document in New Tab</a>", unsafe_allow_html=True)
                            else:
                                st.info("No document explicitly attached to this specific department requirement yet.")
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
            st.bar_chart({"Approved": [data["department_bottlenecks"]["approved_licenses"]], "Pending": [data["department_bottlenecks"]["pending_reviews"]], "Rejected": [data["department_bottlenecks"]["rejected_applications"]]})

page = st.session_state.get("page", "login")
if not st.session_state["access_token"]: login_page()
elif page == "welcome": welcome_page()
elif page == "profile": profile_page()
elif page == "applicant":
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    check_status = requests.get(f"{API_URL}/dashboard/my-status/", headers=headers)
    if check_status.status_code == 200 and "overall_status" not in check_status.json():
        st.session_state["page"] = "profile"
        st.rerun()
    else: applicant_dashboard()
elif page == "onboarding": onboarding_flow()
elif page == "admin": government_analytics()