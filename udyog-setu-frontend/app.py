import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Udyog Setu Maharashtra", layout="wide", initial_sidebar_state="expanded")

# --- PREMIUM UI OVERHAUL (CSS INJECTION) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

/* Global Font & Deep Midnight Gradient Background */
html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: #020617 !important;
    background-image: linear-gradient(145deg, #020617 0%, #0f172a 100%) !important;
    color: #f8fafc;
}

/* Custom Sleek Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.25); }

@keyframes slideUpFade {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Hide Streamlit Top Bar & Deploy elements */
[data-testid="stHeader"] { background-color: transparent !important; }
[data-testid="stHeaderActionElements"] { display: none !important; }

/* ---------------------------------------------------- */
/* SIDEBAR STYLING - Clean Menu Aesthetic               */
/* ---------------------------------------------------- */
[data-testid="stSidebar"] {
    background-color: rgba(2, 6, 23, 0.8) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    text-align: left !important;
    justify-content: flex-start !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #94a3b8 !important;
    padding: 12px 16px !important;
    font-weight: 500 !important;
    font-size: 15px !important;
    border-radius: 8px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255, 255, 255, 0.05) !important;
    color: #ffffff !important;
    transform: translateX(4px);
}
[data-testid="stSidebar"] .stButton > button:active {
    background: rgba(56, 189, 248, 0.1) !important;
    color: #38bdf8 !important;
}

/* ---------------------------------------------------- */
/* PREMIUM GLASSMORPHISM CONTAINERS                     */
/* ---------------------------------------------------- */
[data-testid="stVerticalBlockBorderWrapper"], [data-testid="stForm"] {
    background: rgba(30, 41, 59, 0.4) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important; 
    box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.5) !important;
    animation: slideUpFade 0.6s ease-out forwards;
    padding: 10px !important;
}

/* ---------------------------------------------------- */
/* TICKETS & EXPANDERS - Smooth Modern Accordions       */
/* ---------------------------------------------------- */
[data-testid="stExpander"] {
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 14px !important;
    background-color: rgba(15, 23, 42, 0.6) !important;
    margin-bottom: 16px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    animation: slideUpFade 0.5s ease-out forwards;
}
[data-testid="stExpander"] summary { 
    background-color: transparent !important; 
    padding: 16px !important;
    font-weight: 600 !important;
}
[data-testid="stExpander"] summary:hover { background-color: rgba(255, 255, 255, 0.02) !important; }

/* ---------------------------------------------------- */
/* INPUTS & FORMS - Pill shaped, sleek glows            */
/* ---------------------------------------------------- */
div[data-baseweb="select"] > div, 
div[data-baseweb="base-input"] > input, 
div[data-baseweb="input"], 
textarea[data-baseweb="textarea"] {
    background-color: rgba(2, 6, 23, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    color: #f8fafc !important;
    -webkit-text-fill-color: #f8fafc !important;
    transition: all 0.3s ease;
    padding: 4px 8px !important;
}
div[data-baseweb="base-input"] > input:focus, 
div[data-baseweb="input"]:focus-within, 
textarea[data-baseweb="textarea"]:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
    background-color: rgba(2, 6, 23, 0.8) !important;
}

/* File Dropzone */
[data-testid="stFileUploaderDropzone"] {
    background-color: rgba(15, 23, 42, 0.4) !important;
    border: 1.5px dashed rgba(148, 163, 184, 0.3) !important;
    border-radius: 12px !important;
    padding: 24px !important;
    transition: all 0.3s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #38bdf8 !important;
    background-color: rgba(56, 189, 248, 0.05) !important;
}

/* ---------------------------------------------------- */
/* BUTTONS - Modern Gradients & Soft Shadows            */
/* ---------------------------------------------------- */
/* General Buttons (Secondary) */
.stButton>button:not([kind="primary"]), 
.stFormSubmitButton>button:not([kind="primary"]) {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(10px) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-weight: 500 !important;
    padding: 8px 24px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.stButton>button:not([kind="primary"]):hover, 
.stFormSubmitButton>button:not([kind="primary"]):hover {
    background: rgba(255, 255, 255, 0.1) !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
    transform: translateY(-1px);
}

/* Primary Action Buttons (Teal/Emerald Gradient) */
button[kind="primary"] {
    background: linear-gradient(135deg, #0ea5e9, #2563eb) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.3) !important;
    padding: 8px 24px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
button[kind="primary"]:hover {
    background: linear-gradient(135deg, #38bdf8, #3b82f6) !important;
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
    transform: translateY(-1px);
}

/* ---------------------------------------------------- */
/* TYPOGRAPHY & METRICS                                 */
/* ---------------------------------------------------- */
h1, h2, h3, h4, p, span, label { color: #f8fafc !important; }
h1 { font-weight: 700 !important; letter-spacing: -0.5px !important; }

[data-testid="stMetricValue"] { 
    color: #f8fafc !important; 
    font-weight: 700 !important; 
    font-size: 2.2rem !important; 
}
[data-testid="stMetricLabel"] { 
    color: #94a3b8 !important; 
    font-weight: 500 !important;
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.5px;
}

/* Tabs overriding */
button[data-baseweb="tab"] { 
    background: transparent !important; 
    color: #64748b !important; 
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] { 
    color: #e2e8f0 !important; 
    border-bottom: 2px solid #38bdf8 !important; 
}
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

# --- Custom Navigation Sidebar ---
with st.sidebar:
    # Centered Logo
    st.markdown("""
        <div style='display: flex; justify-content: center; margin-bottom: 20px; margin-top: 10px;'>
            <img src='https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Seal_of_Maharashtra.svg/200px-Seal_of_Maharashtra.svg.png' width='90'>
        </div>
        <h2 style='text-align: center; color: #f8fafc; margin-bottom: 30px; font-size: 20px;'>Udyog Setu</h2>
    """, unsafe_allow_html=True)
    
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
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Logout", type="primary"):
            st.session_state["access_token"] = None
            st.session_state["user_name"] = None
            st.session_state["active_app_id"] = None
            st.session_state["generated_certificate"] = None
            st.session_state["page"] = "login"
            st.rerun()
    else:
        st.info("Secure Portal. Please log in to proceed.")

def login_page():
    spacer_left, main_col, spacer_right = st.columns([1, 1.5, 1])
    with main_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; font-size: 2.8em;'>Udyog Setu Portal</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.1em; margin-bottom: 30px;'>Maharashtra Single Window Clearance System</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            tab1, tab2 = st.tabs(["Secure Login", "Register Enterprise"])
            
            with tab1:
                st.markdown("<br>", unsafe_allow_html=True)
                email = st.text_input("Business Email Address", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Access Dashboard", use_container_width=True, type="primary"):
                    payload = {"username": email, "password": password}
                    try:
                        response = requests.post(f"{API_URL}/login/", data=payload)
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state["access_token"] = data["access_token"]
                            st.session_state["user_name"] = email
                            st.success("Login successful! Redirecting...")
                            time.sleep(1)
                            st.session_state["page"] = "welcome"
                            st.rerun()
                        else:
                            st.error("Invalid credentials. Please verify your email and password.")
                    except requests.exceptions.ConnectionError:
                        st.error("Could not connect to the backend server. Is FastAPI running?")
            
            with tab2:
                st.markdown("<br>", unsafe_allow_html=True)
                reg_name = st.text_input("Full Legal Name")
                reg_email = st.text_input("Corporate Email Address", key="reg_email")
                reg_password = st.text_input("Create Secure Password", type="password", key="reg_password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Create Account", use_container_width=True, type="primary"):
                    if not reg_name or not reg_email or not reg_password:
                        st.warning("Please complete all required fields.")
                    else:
                        payload = {"full_name": reg_name, "email": reg_email, "password": reg_password}
                        response = requests.post(f"{API_URL}/users/", json=payload)
                        if response.status_code == 200:
                            st.success("Account successfully created! Please switch to the Login tab.")
                        elif response.status_code == 400:
                            st.error(response.json().get("detail", "This email is already registered."))

def welcome_page():
    spacer_left, main_col, spacer_right = st.columns([1, 4, 1])
    with main_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; font-size: 4em; margin-bottom: 0; background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;'>Udyog Setu</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-size: 1.4em; color: #94a3b8; font-weight: 400; letter-spacing: 1px;'>Maharashtra Single Window Clearance System</p>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; padding: 2rem; background: rgba(30, 41, 59, 0.4); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 2.5rem;'>
            <p style='font-size: 1.15em; color: #cbd5e1; line-height: 1.6; margin: 0;'>
                Accelerate your enterprise journey with our unified, AI-driven compliance engine. 
                Securely manage operational documents in the Smart Vault and seamlessly apply for state and central approvals without redundant paperwork.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<h3 style='text-align: center; color: #f8fafc; margin-bottom: 1.5rem;'>Platform Capabilities</h3>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""
            <div style='background: rgba(15, 23, 42, 0.6); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.2); height: 100%;'>
                <h4 style='color: #38bdf8; margin-top: 0;'>Dynamic AI Routing</h4>
                <p style='color: #94a3b8; font-size: 0.95em;'>Instantly generates the exact regulatory compliance checklist tailored to your specific business parameters.</p>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div style='background: rgba(15, 23, 42, 0.6); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.2); height: 100%;'>
                <h4 style='color: #10B981; margin-top: 0;'>Smart Document Vault</h4>
                <p style='color: #94a3b8; font-size: 0.95em;'>Upload and securely verify your corporate documents once. Attach them to unlimited government requirements.</p>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div style='background: rgba(15, 23, 42, 0.6); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(245, 158, 11, 0.2); height: 100%;'>
                <h4 style='color: #F59E0B; margin-top: 0;'>Master Clearance</h4>
                <p style='color: #94a3b8; font-size: 0.95em;'>Automatically generates a consolidated, digitally verifiable Consent to Establish certificate upon full approval.</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        
        act1, act2, act3 = st.columns(3)
        with act1:
            if st.button("Apply for New Business", use_container_width=True, type="primary"):
                st.session_state["page"] = "onboarding"
                st.rerun()
        with act2:
            if st.button("Access Dashboard", use_container_width=True):
                st.session_state["page"] = "applicant"
                st.rerun()
        with act3:
            if st.button("View My Profile", use_container_width=True):
                st.session_state["page"] = "profile"
                st.rerun()

def profile_page():
    st.title("My Profile")
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    user_res = requests.get(f"{API_URL}/users/me/", headers=headers)
    
    if user_res.status_code == 200:
        user_data = user_res.json()
        with st.container(border=True):
            col1, col2 = st.columns([1, 5])
            with col1:
                full_name = user_data.get('full_name', 'User Name')
                initials = "".join([n[0] for n in full_name.split() if n]).upper()[:2]
                st.markdown(f"<div style='background: linear-gradient(135deg, #38bdf8, #3b82f6); border-radius:50%; width:90px; height:90px; display:flex; align-items:center; justify-content:center; font-size:32px; font-weight:700; color:#fff; box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4);'>{initials}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<h2 style='margin-bottom: 0px;'>{full_name}</h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #94a3b8; font-size: 1.1em;'>{user_data.get('email', 'N/A')} &nbsp;|&nbsp; <span style='color: #38bdf8; font-weight:600;'>{user_data.get('role', 'N/A').capitalize()}</span></p>", unsafe_allow_html=True)
                
    st.markdown("<br>", unsafe_allow_html=True)
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
                        st.caption(f"Registered on: {app['date'][:10]}")
                        
                        status_lower = app['status'].lower()
                        # Color coding for status
                        if "approved" in status_lower: 
                            st.markdown(f"<p style='color: #10B981; font-weight: 600;'>● {app['status']}</p>", unsafe_allow_html=True)
                        elif "review" in status_lower or "pending" in status_lower: 
                            st.markdown(f"<p style='color: #F59E0B; font-weight: 600;'>● {app['status']}</p>", unsafe_allow_html=True)
                        else: 
                            st.markdown(f"<p style='color: #EF4444; font-weight: 600;'>● {app['status']}</p>", unsafe_allow_html=True)
                            
                        if st.button("Open Dashboard", key=f"open_{app['id']}", use_container_width=True):
                            st.session_state["active_app_id"] = app['id']
                            st.session_state["page"] = "applicant"
                            st.rerun()

def onboarding_flow():
    spacer_left, main_col, spacer_right = st.columns([1, 4, 1])
    with main_col:
        st.title("Apply for New Business")
        st.markdown("<p style='color:#94a3b8;'>Provide detailed information about your enterprise. Our Regulatory AI will automatically generate the exact legal compliance tickets required for your operation.</p>", unsafe_allow_html=True)
        
        with st.form("onboarding_form"):
            st.markdown("#### 1. General Information")
            business_name = st.text_input("Business Name", placeholder="e.g., Global Tech Solutions")
            sector = st.selectbox("Business Sector", ["Food & Beverage", "Agriculture", "Textile & Garments", "Heavy Manufacturing", "IT/Tech", "Pharmaceuticals", "Other"])
            description = st.text_area("Brief Description of Business Operations", placeholder="e.g., We manufacture and export woven cotton garments...")
            
            st.markdown("<br>#### 2. Operational Scale", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                employee_count = st.number_input("Estimated Number of Employees", min_value=1, value=5)
                factory_area_sqft = st.number_input("Facility/Factory Area (in sq. ft.)", min_value=100, value=1500)
            with col2:
                investment_tier = st.selectbox("Total Investment Tier", ["Micro (< ₹1 Crore)", "Small (₹1 - ₹10 Crore)", "Medium (₹10 - ₹50 Crore)", "Large (> ₹50 Crore)"])
            
            st.markdown("<br>#### 3. Environmental Factors", unsafe_allow_html=True)
            col3, col4 = st.columns(2)
            with col3: 
                st.markdown("<div style='padding-top:10px;'>", unsafe_allow_html=True)
                hazardous = st.checkbox("Facility handles hazardous chemicals or emissions")
                st.markdown("</div>", unsafe_allow_html=True)
            with col4: 
                st.markdown("<div style='padding-top:10px;'>", unsafe_allow_html=True)
                water_usage = st.checkbox("Requires high ground-water usage / produces effluent")
                st.markdown("</div>", unsafe_allow_html=True)
                
            st.markdown("<br><br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Generate AI Compliance Checklist & Apply", type="primary", use_container_width=True)
            
            if submitted:
                if not business_name or not description:
                    st.warning("Please fill in the Business Name and Description.")
                else:
                    payload = {"business_name": business_name, "sector": sector, "description": description, "employee_count": employee_count, "investment_tier": investment_tier, "factory_area_sqft": factory_area_sqft, "has_hazardous_chemicals": hazardous, "high_water_usage": water_usage}
                    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
                    with st.spinner("AI Gatekeeper is analyzing Maharashtra State laws to generate your custom checklist..."):
                        response = requests.post(f"{API_URL}/onboarding/", json=payload, headers=headers)
                        if response.status_code == 200:
                            data = response.json()
                            st.success("Successfully generated compliance tickets via AI!")
                            st.info(f"You require **{data['total_tickets']}** approvals across various departments.")
                            st.session_state["active_app_id"] = data.get("application_id")
                            time.sleep(2)
                            st.session_state["page"] = "applicant"
                            st.rerun()
                        else:
                            st.error(f"Failed to generate checklist. The server returned an error: {response.status_code}")

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

        st.markdown(f"<h1>Dashboard: <span style='color: #38bdf8;'>{data.get('business_name', 'My Business')}</span></h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#94a3b8; margin-top:-10px;'>Applicant: {data['applicant']}</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1: st.metric(label="Overall Status", value=data["overall_status"])
            with col2: st.metric(label="Total Progress", value=data["total_progress"])
            with col3:
                pending_count = len([t for t in data["department_breakdown"] if t['status'] != 'Approved'])
                st.metric(label="Pending Action Items", value=pending_count)
                
        st.divider()

        # Master Clearance Section
        total_tickets = len(data["department_breakdown"])
        approved_tickets = len([t for t in data["department_breakdown"] if t['status'] == 'Approved'])
        all_approved = (total_tickets > 0 and approved_tickets == total_tickets)

        if all_approved:
            with st.container(border=True):
                st.markdown("""
                <div style="border-left: 4px solid #10B981; padding: 16px; background: rgba(16, 185, 129, 0.08); border-radius: 12px; margin-bottom: 15px;">
                    <h3 style="margin:0; color:#10B981;">Consolidated Master Clearance Granted</h3>
                    <p style="margin:0; padding-top:6px; color:#cbd5e1; font-size:1.1em;">All regulatory departments have approved your submissions. Your official Consent to Establish certificate is ready.</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Generate Master Clearance Certificate", type="primary", use_container_width=True):
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
                    # Styled text area for the certificate
                    st.markdown("""
                    <style>
                    textarea[aria-label="Certificate View"] {
                        font-family: 'Courier New', monospace !important;
                        font-size: 14px !important;
                        line-height: 1.6 !important;
                        background-color: #0f172a !important;
                        color: #f8fafc !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    st.text_area("Certificate View", value=st.session_state["generated_certificate"], height=400, disabled=True, label_visibility="hidden")
                    st.download_button(label="Download Official Certificate (.txt)", data=st.session_state["generated_certificate"], file_name=f"{data.get('business_name', 'Enterprise').replace(' ', '_')}_Clearance_Certificate.txt", mime="text/plain", type="primary", use_container_width=True)
            st.divider()

        # Two Column Layout: Tickets & Vault
        left_col, spacer, right_col = st.columns([1.4, 0.1, 1])
        
        with left_col:
            st.markdown("### Department Review Tickets")
            for ticket in data["department_breakdown"]:
                status_lower = ticket['status'].lower()
                
                # Dynamic border colors based on status
                if "approved" in status_lower: progress_val, status_color, status_alert = 100, "#10B981", st.success
                elif "review" in status_lower: progress_val, status_color, status_alert = 75, "#F59E0B", st.warning
                elif "pending submission" in status_lower: progress_val, status_color, status_alert = 25, "#38bdf8", st.info
                elif "pending" in status_lower: progress_val, status_color, status_alert = 50, "#F59E0B", st.warning
                else: progress_val, status_color, status_alert = 10, "#EF4444", st.error

                needs_upload = "pending submission" in status_lower or "rejected" in status_lower

                # Inject dynamic border color for this specific expander
                st.markdown(f"""
                <style>
                div[data-testid="stExpander"]:has(summary:contains("{ticket['department']} - {ticket['license_name']}")) {{
                    border-left: 5px solid {status_color} !important;
                }}
                </style>
                """, unsafe_allow_html=True)

                with st.expander(f"{ticket['department']} - {ticket['license_name']}", expanded=needs_upload):
                    # Header row inside expander
                    st.markdown(f"""
                    <div style='display:flex; justify-content:space-between; margin-bottom: 10px;'>
                        <span style='color:#94a3b8; font-size:0.9em;'>SLA: {ticket.get('sla', 'N/A')}</span>
                        <span style='color:#94a3b8; font-size:0.9em;'>Updated: {ticket['last_updated'][:10]}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if ticket['officer_comments']: 
                        status_alert(f"**{ticket['status']}** | Note: {ticket['officer_comments']}")
                    else: 
                        status_alert(f"**{ticket['status']}**")
                        
                    st.progress(progress_val, text="Department Processing Stage")
                    
                    if needs_upload:
                        st.divider()
                        st.markdown(f"**Required Document:** <span style='color:#38bdf8;'>{ticket.get('document_required', 'Standard Document')}</span>", unsafe_allow_html=True)
                        uploaded_file = st.file_uploader("Attach clear, legible document", type=["pdf", "png", "jpg", "jpeg"], key=f"upload_{ticket['ticket_id']}")
                        
                        if st.button("Run AI Security Scan & Submit", key=f"scan_{ticket['ticket_id']}", use_container_width=True, type="primary"):
                            if uploaded_file is not None:
                                with st.spinner("AI Gatekeeper is analyzing the document..."):
                                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                                    data_payload = {"email": st.session_state.get("user_name", ""), "document_type": ticket.get('document_required', ticket['department']), "ticket_id": ticket['ticket_id']}
                                    upload_res = requests.post(f"{API_URL}/documents/upload/", data=data_payload, files=files)
                                    if upload_res.status_code == 200:
                                        meta = upload_res.json().get("extracted_metadata", {})
                                        if meta.get("is_valid"): 
                                            st.success("Passed AI Screening! Ticket updated and sent to officer.")
                                        else: 
                                            st.error(f"Rejected: {meta.get('screening_status', 'Mismatch detected.')}")
                                        time.sleep(2.5)
                                        st.rerun()
                            else:
                                st.warning("Please attach a file first.")
                                
        with right_col:
            st.markdown("### Smart Vault")
            st.markdown("<p style='color:#94a3b8; margin-top:-10px; margin-bottom:15px;'>Your verified documents are stored here. Attach them to future requirements instantly.</p>", unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown("#### Upload to Vault")
                vault_doc_type = st.selectbox("Select Document Type", ["Identity Proof", "Company Registration (MCA)", "GST Registration", "Fire NOC", "Environmental Clearance", "Property Lease Agreement", "Floor Plan"], key="vault_doc_type")
                vault_file = st.file_uploader("Upload PDF or Image", type=["pdf", "png", "jpg", "jpeg"], key="vault_file_uploader")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Verify & Save to Vault", use_container_width=True, key="vault_upload_btn", type="primary"):
                    if vault_file is not None:
                        with st.spinner("AI Gatekeeper is analyzing the document..."):
                            files = {"file": (vault_file.name, vault_file.getvalue(), vault_file.type)}
                            data_payload = {"email": st.session_state.get("user_name", ""), "document_type": vault_doc_type, "ticket_id": ""}
                            upload_res = requests.post(f"{API_URL}/documents/upload/", data=data_payload, files=files)
                            if upload_res.status_code == 200:
                                meta = upload_res.json().get("extracted_metadata", {})
                                if meta.get("is_valid"):
                                    st.success(f"Verified and added {vault_doc_type} to Smart Vault!")
                                    time.sleep(2)
                                    st.rerun()
                                else: st.error(f"Rejected: {meta.get('screening_status', 'Mismatch detected.')}")
                    else:
                        st.warning("Please attach a file first.")
            
            st.markdown("<br>", unsafe_allow_html=True)
            vault_res = requests.get(f"{API_URL}/documents/vault/", headers=headers)
            
            if vault_res.status_code == 200:
                vault_data = vault_res.json().get("vault", [])
                if not vault_data: 
                    st.info("Your vault is currently empty.")
                else:
                    actionable_tickets = [t for t in data["department_breakdown"] if t["status"] in ["Pending Submission", "Pending", "Rejected"]]
                    
                    for i, doc in enumerate(vault_data):
                        with st.container(border=True):
                            # Beautiful Vault Item Card
                            st.markdown(f"""
                            <div style='border-left: 4px solid #10B981; padding-left: 14px; margin-bottom: 12px; background: rgba(16, 185, 129, 0.05); border-radius: 6px; padding-top: 10px; padding-bottom: 10px;'>
                                <h4 style='margin:0; padding:0; color:#f8fafc; font-size: 1.1em;'>{doc['type']}</h4>
                                <div style='margin-top:6px; display:flex; justify-content:space-between; color:#94a3b8; font-size: 0.85em;'>
                                    <span>ID: {doc['number']}</span>
                                    <span style='color:#10B981; font-weight:600;'>Score: {int(doc['score'] * 100)}%</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if actionable_tickets:
                                ticket_options = {f"{t['department']} - {t['license_name']} ({t['status']})": t['ticket_id'] for t in actionable_tickets}
                                selected_ticket_label = st.selectbox(f"Select Ticket to Attach", options=list(ticket_options.keys()), key=f"vault_select_{i}")
                                selected_ticket_id = ticket_options[selected_ticket_label]
                                
                                if st.button(f"Attach Document", key=f"vault_attach_{i}", use_container_width=True):
                                    attach_res = requests.post(f"{API_URL}/tickets/attach-vault/", json={"ticket_id": selected_ticket_id, "document_type": doc['type']}, headers=headers)
                                    if attach_res.status_code == 200:
                                        st.success(f"{doc['type']} successfully attached!")
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
            
            with st.container(border=True):
                col_m1, col_m2 = st.columns(2)
                with col_m1: st.metric("Pending Officer Reviews", len(tickets))
                with col_m2: st.metric("Processing Queue Status", "Chronological (Oldest First)")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if not tickets: 
                st.success("Inbox Zero! All AI-screened applications have been processed.")
            else:
                for t in tickets:
                    with st.container(border=True):
                        ticket_col, doc_col = st.columns([1.1, 0.9])
                        
                        with ticket_col:
                            st.markdown(f"<h3 style='color:#38bdf8; margin-bottom:5px;'>{t['applicant']}</h3>", unsafe_allow_html=True)
                            st.write(f"**Department:** {t['department']}")
                            st.write(f"**Approval Type:** {t.get('license_type', 'General')}")
                            
                            st.markdown(f"""
                            <div style='background:rgba(56, 189, 248, 0.1); border:1px solid rgba(56, 189, 248, 0.3); padding:8px 12px; border-radius:8px; margin: 10px 0;'>
                                <span style='color:#38bdf8; font-weight:600;'>Required Document:</span> {t.get('required_document', 'Standard Document')}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.caption(f"Submitted At: {t.get('submitted_at', 'N/A')}")
                            
                            status_lower = t['status'].lower()
                            if "approved" in status_lower: st.success(f"Current Status: **{t['status']}**")
                            elif "review" in status_lower or "pending" in status_lower: st.warning(f"Current Status: **{t['status']}**")
                            else: st.error(f"Current Status: **{t['status']}**")
                                
                            st.info(f"**AI Gatekeeper Note:** {t['current_note']}")
                            
                            with st.form(key=f"review_form_{t['ticket_id']}"):
                                official_comment = st.text_input("Official Officer Comment", placeholder="e.g., Verified against state records. Approved.")
                                st.markdown("<br>", unsafe_allow_html=True)
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
                            st.markdown("#### Document & AI Verification")
                            if t.get("document"):
                                doc_info = t["document"]
                                meta = doc_info.get("metadata", {})
                                extract = meta.get("extracted_data", {})
                                score = meta.get("confidence_score", 0.0)
                                
                                st.progress(score, text=f"AI Confidence Score: {int(score * 100)}%")
                                st.markdown("<br>", unsafe_allow_html=True)
                                
                                st.write(f"**Document Number:** {extract.get('document_number', 'N/A')}")
                                st.write(f"**Issue Date:** {extract.get('issue_date', 'N/A')}")
                                st.write(f"**Expiry Date:** {extract.get('expiry_date', 'N/A')}")
                                st.write(f"**Signatures Verified:** {'Yes' if extract.get('signatures_present') else 'No'}")
                                
                                st.divider()
                                file_url = doc_info.get("file_url", "#")
                                
                                # Beautiful Document Open Button
                                st.markdown(f"""
                                <a href='{file_url}' target='_blank' style='text-decoration:none;'>
                                    <div style='background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), rgba(59, 130, 246, 0.2)); border: 1px solid rgba(56, 189, 248, 0.5); padding: 12px; border-radius: 8px; text-align: center; color: #38bdf8; font-weight: 600; transition: all 0.3s ease;'>
                                        View Original Uploaded Document
                                    </div>
                                </a>
                                """, unsafe_allow_html=True)
                            else:
                                st.info("No document explicitly attached to this specific department requirement yet.")
    
    with analytics_tab:
        st.markdown("### Real-time Bottleneck Analysis")
        response = requests.get(f"{API_URL}/admin/statistics/")
        if response.status_code == 200:
            data = response.json()
            with st.container(border=True):
                col1, col2, col3 = st.columns(3)
                col1.metric("Registered Businesses", data["state_overview"]["total_registered_businesses"])
                col2.metric("Pending Reviews", data["department_bottlenecks"]["pending_reviews"])
                col3.metric("Approval Rate", data["department_bottlenecks"]["overall_approval_rate"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
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