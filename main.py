import google.generativeai as genai
import os
import json
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # <-- Add this new import
import jwt # <-- Add this to decode the token
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import our database tools and recipe book
from database import SessionLocal
import models
import uuid
import auth

app = FastAPI()

# ==========================================
# 1. Pydantic Schemas (The Order Tickets)
# ==========================================
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

    

class BusinessProfile(BaseModel):
    sector: str
    employee_count: int
    has_hazardous_chemicals: bool

class ApplicationCreate(BaseModel):
    email: str

class DepartmentReview(BaseModel):
    approval_id: str  # The specific UUID of the department's ticket
    new_status: str   # e.g., "Approved", "Rejected", "Need More Info"
    comments: str     # e.g., "Fire exits are not marked clearly"

# ==========================================
# 2. Database Dependency
# ==========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# This tells FastAPI where users get their tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# THE BOUNCER: This function checks the token, decodes it, and finds the secure user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials, please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token using your secret key from auth.py
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
# ==========================================
# 3. Rules Engine Data (Scalable Logic)
# ==========================================
INDUSTRY_REQUIREMENTS = {
    "food": ["FSSAI License", "Health Trade License", "Food & Drug Administration (FDA) NOC"],
    "agriculture": ["FSSAI License", "Agri-Export Zone NOC"],
    "textile": ["Textile Ministry Registration", "Effluent Treatment Plant (ETP) Approval"],
    "manufacturing": ["Factory Inspectorate Clearance", "Boiler Registration"]
}

CONDITIONAL_REQUIREMENTS = [
    {
        "evaluator": lambda profile: profile.has_hazardous_chemicals,
        "approvals": ["Fire Safety NOC", "Pollution Control Board (Red Category)"]
    },
    {
        "evaluator": lambda profile: profile.employee_count >= 10,
        "approvals": ["EPFO Registration", "ESIC Worker Insurance"]
    },
    {
        "evaluator": lambda profile: profile.employee_count >= 50,
        "approvals": ["Standing Orders Act Registration", "Workplace Creche Certification"]
    }
]

# ==========================================
# 4. API Endpoints
# ==========================================

@app.get("/")
def read_root():
    return {"Message": "Hello! The government portal backend is awake!"}


@app.post("/users/")
def create_test_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # 1. Catch duplicate emails first!
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="This email is already registered.")

    # 2. Create or fetch the "entrepreneur" role
    role = db.query(models.Role).filter(models.Role.role_name == "entrepreneur").first()
    if not role:
        role = models.Role(role_name="entrepreneur")
        db.add(role)
        db.commit()
        db.refresh(role)

    # 3. Scramble the password using auth.py
    hashed_pwd = auth.get_password_hash(user_data.password)
    
    # 4. Create the actual user with the secure password
    new_user = models.User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hashed_pwd, # Saves the scrambled version!
        role_id=role.id
    )
    
    db.add(new_user)
    db.commit()
    
    return {"message": "Success! User securely saved to Database.", "name": new_user.full_name}


@app.post("/onboarding/")
def generate_checklist(
    profile: BusinessProfile, 
    current_user: models.User = Depends(get_current_user), # The Bouncer handles identity!
    db: Session = Depends(get_db)
):
    # Base approvals everyone needs
    required_approvals = {"Company Registration (MCA)", "GST Registration", "Shops & Establishment License"}
    
    # Dynamic Matrix Lookup 
    sector_approvals = INDUSTRY_REQUIREMENTS.get(profile.sector.lower(), [])
    required_approvals.update(sector_approvals)
    
    # Dynamic Conditional Evaluator 
    for rule in CONDITIONAL_REQUIREMENTS:
        if rule["evaluator"](profile):
            required_approvals.update(rule["approvals"])
            
    final_checklist = list(required_approvals)
        
    # Directly update the user attached to the secure token
    current_user.business_profile = profile.model_dump() 
    db.commit()
        
    return {
        "message": "Checklist generated using scalable Rules Engine!",
        "total_approvals_required": len(final_checklist),
        "required_approvals": final_checklist
    }
import json

# Configure the live AI connection
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_document_with_ai(document_type: str, file_bytes: bytes, mime_type: str):
    """Sends actual file bytes to Gemini for strict, smart screening."""
    try:
        model = genai.GenerativeModel('gemini-3.6-flash') # Or 3.6-flash if you are using that
        
        prompt = f"""
        You are a strict, automated Screening Agent for the Maharashtra Government.
        The user claims this document is a: '{document_type}'.
        
        YOUR SCREENING RULES:
        1. STRICT MATCH: If the document is clearly NOT a {document_type} (e.g. they uploaded a PAN card but selected MCA Registration), you MUST set is_valid to false.
        2. QUALITY CHECK: If the image is heavily blurred, cut off, or unreadable, set is_valid to false.
        3. SMART EXTRACTION: Extract standard fields. Note: Indian PAN Cards do NOT have expiry dates (set to null). Aadhaar cards require both sides or a full e-Aadhaar.
        
        Respond ONLY with a valid JSON object matching this exact structure, with no markdown formatting:
        {{
            "is_valid": true,
            "confidence_score": 0.95,
            "screening_status": "Passed AI Screening" or "Rejected: [Specific Reason]",
            "extracted_data": {{
                "document_number": "extracted number or null",
                "issue_date": "YYYY-MM-DD or null",
                "expiry_date": "YYYY-MM-DD or null"
            }},
            "critical_flags": ["list of issues, if any"]
        }}
        """
        
        response = model.generate_content([
            prompt,
            {"mime_type": mime_type, "data": file_bytes}
        ])
        
        raw_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(raw_text)
        
    except Exception as e:
        print(f"AI Engine Error: {e}")
        return {
            "is_valid": False, 
            "confidence_score": 0.0, 
            "screening_status": "Processing Failed",
            "extracted_data": {}, 
            "critical_flags": ["AI processing failed or file unreadable."]
        }


@app.post("/documents/upload/")
async def upload_document(
    email: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    allowed_types = ["application/pdf", "image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    file_bytes = await file.read()
    
    # Run the LIVE AI Screening
    ai_analysis = analyze_document_with_ai(document_type, file_bytes, file.content_type)
    
    # 🚀 NEW LOGIC: AI is a Gatekeeper, not the final approver.
    auto_status = "Rejected"
    if ai_analysis.get("is_valid") and ai_analysis.get("confidence_score", 0) > 0.85:
        auto_status = "In Review" # Passed to Human Official

    fake_cloud_url = f"https://s3-bucket.com/uploads/{file.filename}"
    
    new_document = models.Document(
        user_id=user.id,
        document_type=document_type,
        file_url=fake_cloud_url,
        verification_status=auto_status,
        ai_extracted_metadata=ai_analysis
    )
    db.add(new_document)
    
    # Sync with Department Tickets
    pending_tickets = db.query(models.DepartmentApproval).join(models.Application).filter(
        models.Application.user_id == user.id,
        models.DepartmentApproval.status == "Pending"
    ).all()
    
    for ticket in pending_tickets:
        if auto_status == "In Review":
            ticket.status = "In Review"
            ticket.officer_comments = f"🟡 AI Screening Passed for {document_type}. Awaiting final human officer sign-off."
        else:
            # Leave it as Pending, but warn the user
            ticket.officer_comments = f"🔴 AI Rejected {document_type}: {ai_analysis.get('screening_status')}. Please upload a correct, clear document."

    db.commit()
    
    return {
        "message": f"Successfully processed {file.filename}",
        "document_type": document_type,
        "status": auto_status,
        "extracted_metadata": ai_analysis
    }
@app.post("/applications/submit/")
def submit_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    # 1. Find the user and their checklist
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    if not user.business_profile or "sector" not in user.business_profile:
        raise HTTPException(status_code=400, detail="Please complete the onboarding checklist first.")

    # 2. Re-run rules engine to get required approvals
    required_approvals = {"Company Registration (MCA)", "GST Registration", "Shops & Establishment License"}
    sector_approvals = INDUSTRY_REQUIREMENTS.get(user.business_profile.get("sector", "").lower(), [])
    required_approvals.update(sector_approvals)
    
    # 3. Create the Master Application
    new_app = models.Application(
        user_id=user.id,
        status="Under Review"
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    # 4. Generate parallel Department Approval tickets
    for approval_name in required_approvals:
        # We use 'name' here to perfectly match your models.py Department class
        dept = db.query(models.Department).filter(models.Department.name == approval_name).first()
        if not dept:
            dept = models.Department(name=approval_name)
            db.add(dept)
            db.commit()
            db.refresh(dept)

        dept_ticket = models.DepartmentApproval(
            application_id=new_app.id,
            department_id=dept.id,         
            status="Pending",
            official_notes="Awaiting officer review." 
        )
        db.add(dept_ticket)
    
    db.commit()

    return {
        "message": "Application submitted successfully to all departments in parallel!",
        "application_id": str(new_app.id),
        "departments_notified": len(required_approvals)
    }



@app.post("/login/")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Swagger UI's form always calls the field 'username', so we map it to our 'email' column
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # Check if user exists AND password is correct
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Create the JWT Token
    access_token = auth.create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "message": "Login successful!"
    }

@app.get("/dashboard/my-status/")
def get_secure_dashboard(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Look how clean this is! We already know the user from the token.
    
    # Get their most recent application
    application = db.query(models.Application).filter(models.Application.user_id == current_user.id).order_by(models.Application.created_at.desc()).first()
    
    if not application:
        return {"message": f"Welcome {current_user.full_name}! No applications found yet.", "dashboard": []}

    # Fetch all parallel department tickets
    department_tickets = db.query(models.DepartmentApproval).filter(models.DepartmentApproval.application_id == application.id).all()

    dashboard_data = [
        {
            "ticket_id": str(ticket.id),
            "department": ticket.department.name, 
            "status": ticket.status,
            "officer_comments": ticket.official_notes, 
            "last_updated": ticket.updated_at
        }
        for ticket in department_tickets
    ]

    return {
        "applicant": current_user.full_name,
        "overall_status": application.status,
        "total_progress": f"{len([t for t in department_tickets if t.status == 'Approved'])}/{len(department_tickets)} Completed",
        "department_breakdown": dashboard_data
    }
@app.patch("/departments/review/")
def official_review(review: DepartmentReview, db: Session = Depends(get_db)):
    # This endpoint is used by the Government Official's frontend
    ticket = db.query(models.DepartmentApproval).filter(models.DepartmentApproval.id == review.approval_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Approval ticket not found.")
        
    ticket.status = review.new_status
    ticket.official_notes = review.comments # Fixed to match your model!
    db.commit()
    
    return {"message": f"Ticket for {ticket.department.name} updated to {review.new_status}"}
@app.get("/admin/statistics/")
def get_government_statistics(db: Session = Depends(get_db)):
    """
    Provides real-time analytics for the Maharashtra State Dashboard.
    (In production, you would lock this down to 'admin' roles only using the token)
    """
    total_users = db.query(models.User).count()
    total_applications = db.query(models.Application).count()
    
    # Check ticket statuses across all departments
    pending_tickets = db.query(models.DepartmentApproval).filter(models.DepartmentApproval.status == "Pending").count()
    approved_tickets = db.query(models.DepartmentApproval).filter(models.DepartmentApproval.status == "Approved").count()
    rejected_tickets = db.query(models.DepartmentApproval).filter(models.DepartmentApproval.status == "Rejected").count()

    total_tickets = pending_tickets + approved_tickets + rejected_tickets
    approval_rate = round((approved_tickets / total_tickets * 100), 1) if total_tickets > 0 else 0

    return {
        "state_overview": {
            "total_registered_businesses": total_users,
            "total_master_applications": total_applications
        },
        "department_bottlenecks": {
            "pending_reviews": pending_tickets,
            "approved_licenses": approved_tickets,
            "rejected_applications": rejected_tickets,
            "overall_approval_rate": f"{approval_rate}%"
        },
        "message": "Real-time state analytics generated successfully."
    }