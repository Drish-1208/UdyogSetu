import google.generativeai as genai
import os
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from pydantic import BaseModel, UUID4
from typing import Optional
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

class OfficerDecision(BaseModel):
    ticket_id: UUID4  # Matches your UUID primary key
    decision: str     # "Approved" or "Rejected"
    comments: str

class ExtractedData(BaseModel):
    document_number: Optional[str] = Field(description="The unique ID number of the document. For PAN, this is a 10-character alphanumeric string. Null if illegible.")
    issue_date: Optional[str] = Field(description="Issue date in YYYY-MM-DD format.")
    expiry_date: Optional[str] = Field(description="Expiry date in YYYY-MM-DD format. Return null for documents without expiry (e.g., PAN cards).")
    signatures_present: bool = Field(description="True if a physical or digital signature is detected.")

class DocumentVerificationResult(BaseModel):
    is_valid: bool = Field(description="Strictly True ONLY if the document perfectly matches the requested document_type and is clearly legible.")
    confidence_score: float = Field(description="Confidence score from 0.0 to 1.0.")
    screening_status: str = Field(description="Output 'Passed AI Screening' or 'Rejected: [Specific Reason]'.")
    extracted_data: ExtractedData
    critical_flags: List[str] = Field(description="List of issues (e.g., blurry, expired, mismatched name). Empty if perfect.")

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

# 📜 NEW: Dynamic MAITRI Compliance Rules
DOCUMENT_RULES = {
    "Company Registration (MCA)": "Must contain a 21-character Corporate Identification Number (CIN) and be issued by the Ministry of Corporate Affairs or Registrar of Companies.",
    "GST Registration": "Must contain a 15-character GSTIN. Ensure it explicitly states 'Goods and Services Tax'.",
    "Fire NOC": "Must be issued by Maharashtra Fire Services or a local municipal fire brigade. Must clearly state 'No Objection Certificate' for fire safety.",
    "Environmental Clearance": "Must be issued by the Maharashtra Pollution Control Board (MPCB) or SEIAA. Look for 'Consent to Establish' or 'Consent to Operate' clauses.",
    "Identity Proof": "Valid IDs include PAN Card, Passport, or Voter ID. Note: Indian PAN Cards do not have expiry dates.",
    "Property Lease Agreement": "Must include names of lessor and lessee, property address, and ideally a Maharashtra stamp duty seal or e-registration mark."
}

def analyze_document_with_ai(document_type: str, file_bytes: bytes, mime_type: str):
    """Sends file bytes to Gemini using Pydantic Outputs and Dynamic Legal Rules."""
    try:
        model = genai.GenerativeModel('gemini-3.6-flash')
        
        # Fetch the specific legal rule for the requested document type
        specific_rule = DOCUMENT_RULES.get(document_type, "Perform standard government document verification.")
        
        prompt = f"""
        You are an elite, automated Screening Agent for the MAITRI Single Window Clearance portal of the Maharashtra Government.
        The user claims this document is a: '{document_type}'.
        
        YOUR SPECIFIC SCREENING RULE FOR THIS DOCUMENT:
        {specific_rule}
        
        GENERAL RULES:
        1. STRICT MATCH: If the document violates the specific rule above, or is clearly NOT a '{document_type}', you MUST set is_valid to false and explain exactly why in the screening_status.
        2. ANTI-FRAUD CHECK: If the image is heavily blurred, cut off, unreadable, or shows signs of digital tampering (e.g., mismatched fonts), set is_valid to false.
        3. SMART DATA EXTRACTION: Extract the primary ID/Certificate number, issue date, and expiry date if present. 
        """
        
        response = model.generate_content(
            [prompt, {"mime_type": mime_type, "data": file_bytes}],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=DocumentVerificationResult,
                temperature=0.0 # Absolute zero creativity - strict compliance mode
            )
        )
        
        return json.loads(response.text)
        
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
@app.get("/documents/vault/")
async def get_vault_documents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) 
):
    # Fetch all documents for this user that passed AI Gatekeeper screening
    docs = db.query(models.Document).filter(
        models.Document.user_id == current_user.id,
        models.Document.verification_status.in_(["Verified", "In Review"])
    ).all()
    
    vault_items = []
    for doc in docs:
        meta = doc.ai_extracted_metadata or {}
        extracted = meta.get("extracted_data", {})
        vault_items.append({
            "type": doc.document_type,
            "number": extracted.get("document_number", "N/A"),
            "score": meta.get("confidence_score", 0.0)
        })
        
    return {"vault": vault_items}

@app.get("/admin/tickets/pending/")
def get_pending_tickets(db: Session = Depends(get_db)):
    """Fetches all tickets that passed AI screening and need human review."""
    try:
        tickets = db.query(models.DepartmentApproval).filter(
            models.DepartmentApproval.status == "In Review"
        ).all()
        
        results = []
        for ticket in tickets:
            app_record = db.query(models.Application).filter(models.Application.id == ticket.application_id).first()
            user = db.query(models.User).filter(models.User.id == app_record.user_id).first() if app_record else None
            
            # Safely fetch department name if relationship is loaded, else fallback to license type
            dept_name = ticket.department.name if hasattr(ticket, "department") and ticket.department else ticket.license_type
            
            # Use official_notes as defined in your model
            notes = getattr(ticket, "official_notes", None) or "Awaiting final sign-off."
            
            results.append({
                "ticket_id": str(ticket.id),
                "applicant": user.full_name if user else "Unknown Business",
                "department": dept_name,
                "status": ticket.status,
                "current_note": notes
            })
        return {"tickets": results}
    except Exception as e:
        print(f"Admin Dashboard Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/admin/tickets/review/")
def review_ticket(payload: OfficerDecision, db: Session = Depends(get_db)):
    """Allows a government official to approve or reject a ticket."""
    ticket = db.query(models.DepartmentApproval).filter(models.DepartmentApproval.id == payload.ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")
        
    ticket.status = payload.decision
    ticket.official_notes = f"👨‍⚖️ Official Verdict: {payload.comments}"
    db.commit()
    return {"message": f"Ticket {payload.ticket_id} marked as {payload.decision}."}