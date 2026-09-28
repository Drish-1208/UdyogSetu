import google.generativeai as genai
import os
import json
from pydantic import BaseModel, Field, UUID4
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
import jwt 
from sqlalchemy.orm import Session

from database import SessionLocal
import models
import uuid
import auth

app = FastAPI()

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

class OfficerDecision(BaseModel):
    ticket_id: UUID4  
    decision: str     
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

# --- NEW: Dynamic AI Onboarding Schemas ---
class ComplianceTicket(BaseModel):
    department: str = Field(description="The issuing government department (e.g., Fire Department, MPCB).")
    license_name: str = Field(description="The exact name of the license or approval required.")
    required_document_type: str = Field(description="The primary physical document the user must upload to apply (e.g., Floor Plan, PAN Card, Lease Agreement).")
    sla_days: int = Field(description="The maximum allowed processing time in days (Service Level Agreement).")

class AIComplianceChecklist(BaseModel):
    tickets: List[ComplianceTicket]

class BusinessProfile(BaseModel):
    business_name: str
    sector: str
    description: str
    employee_count: int
    investment_tier: str
    factory_area_sqft: int
    has_hazardous_chemicals: bool
    high_water_usage: bool

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class DepartmentReview(BaseModel):
    approval_id: str
    new_status: str
    comments: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials, please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
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

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@app.get("/")
def read_root():
    return {"Message": "Hello! The government portal backend is awake!"}

@app.post("/users/")
def create_test_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="This email is already registered.")

    role = db.query(models.Role).filter(models.Role.role_name == "entrepreneur").first()
    if not role:
        role = models.Role(role_name="entrepreneur")
        db.add(role)
        db.commit()
        db.refresh(role)

    hashed_pwd = auth.get_password_hash(user_data.password)
    
    new_user = models.User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hashed_pwd,
        role_id=role.id
    )
    
    db.add(new_user)
    db.commit()
    return {"message": "Success! User securely saved to Database.", "name": new_user.full_name}

@app.get("/users/me/")
def get_user_profile(current_user: models.User = Depends(get_current_user)):
    return {
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role.role_name if current_user.role else "User"
    }

@app.post("/onboarding/")
def generate_dynamic_checklist_and_apply(
    profile: BusinessProfile, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.business_profile = profile.model_dump()
    db.commit()
    
    # 1. Ask Gemini to generate a highly specific legal checklist based on the deep parameters
    try:
        model = genai.GenerativeModel('gemini-3.6-flash')
        prompt = f"""
        You are the Chief Regulatory AI for the Maharashtra Government MAITRI portal.
        Analyze this business profile and generate the required government approvals.
        Always include standard things like 'Company Registration (MCA)' and 'GST Registration'.
        Then add specific approvals based on the profile:
        - Sector: {profile.sector}
        - Description: {profile.description}
        - Employees: {profile.employee_count}
        - Investment: {profile.investment_tier}
        - Factory Area: {profile.factory_area_sqft} sqft
        - Hazardous Chemicals: {profile.has_hazardous_chemicals}
        - High Water Usage: {profile.high_water_usage}
        """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=AIComplianceChecklist,
                temperature=0.2
            )
        )
        ai_checklist = json.loads(response.text)
        tickets = ai_checklist.get("tickets", [])
        
    except Exception as e:
        print(f"AI Generation Failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate compliance checklist from AI Engine.")

    # 2. Automatically create the Application and the Tickets
    new_app = models.Application(
        user_id=current_user.id,
        project_name=profile.business_name,
        status="Under Review"
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    for item in tickets:
        dept_name = item.get("department", "General Department")
        dept = db.query(models.Department).filter(models.Department.name == dept_name).first()
        if not dept:
            dept = models.Department(name=dept_name)
            db.add(dept)
            db.commit()
            db.refresh(dept)

        # We inject the document requirement and SLA directly into the license_type field so the frontend can read it
        formatted_license_type = f"{item.get('license_name')} | DOC_REQ: {item.get('required_document_type')} | SLA: {item.get('sla_days')} Days"
        
        dept_ticket = models.DepartmentApproval(
            application_id=new_app.id,
            department_id=dept.id,         
            license_type=formatted_license_type,
            status="Pending Submission", # NEW STATUS
            official_notes="Submit a document to proceed." 
        )
        db.add(dept_ticket)
    
    db.commit()

    return {
        "message": "AI Checklist Generated and Application Submitted!",
        "application_id": str(new_app.id),
        "total_tickets": len(tickets)
    }

def analyze_document_with_ai(document_type: str, file_bytes: bytes, mime_type: str):
    try:
        model = genai.GenerativeModel('gemini-3.6-flash')
        prompt = f"""
        You are an elite, automated Screening Agent for the MAITRI Single Window Clearance portal.
        The user claims this document satisfies the requirement for: '{document_type}'.
        
        GENERAL RULES:
        1. STRICT MATCH: Check if the document matches the required context of '{document_type}'. If it is completely irrelevant, set is_valid to false and explain why.
        2. ANTI-FRAUD CHECK: If the image is heavily blurred, cut off, unreadable, or tampered with, set is_valid to false.
        3. SMART DATA EXTRACTION: Extract the primary ID/Certificate number, issue date, and expiry date if present. 
        """
        
        response = model.generate_content(
            [prompt, {"mime_type": mime_type, "data": file_bytes}],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=DocumentVerificationResult,
                temperature=0.0
            )
        )
        return json.loads(response.text)
        
    except Exception as e:
        return {
            "is_valid": False, "confidence_score": 0.0, "screening_status": "Processing Failed",
            "extracted_data": {}, "critical_flags": ["AI processing failed or file unreadable."]
        }

@app.post("/documents/upload/")
async def upload_document(
    email: str = Form(...),
    document_type: str = Form(...),
    ticket_id: str = Form(""),  
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
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    real_url = f"http://127.0.0.1:8000/uploads/{file.filename}"
    ai_analysis = analyze_document_with_ai(document_type, file_bytes, file.content_type)
    
    auto_status = "Rejected"
    if ai_analysis.get("is_valid") and ai_analysis.get("confidence_score", 0) > 0.85:
        auto_status = "In Review"

    new_document = models.Document(
        user_id=user.id,
        document_type=document_type,
        file_url=real_url,
        verification_status=auto_status,
        ai_extracted_metadata=ai_analysis
    )
    db.add(new_document)
    
    if ticket_id and ticket_id.strip():
        try:
            ticket = db.query(models.DepartmentApproval).filter(models.DepartmentApproval.id == ticket_id).first()
            if ticket:
                if auto_status == "In Review":
                    ticket.status = "In Review"
                    ticket.official_notes = f"AI Screening Passed for {document_type}. Awaiting final human officer sign-off."
                else:
                    ticket.status = "Rejected"
                    ticket.official_notes = f"AI Rejected {document_type}: {ai_analysis.get('screening_status')}. Please upload a clear document."
        except Exception as e:
            print(f"Skipping ticket lookup: {e}")

    db.commit()
    
    return {
        "message": f"Successfully processed {file.filename}",
        "document_type": document_type,
        "status": auto_status,
        "extracted_metadata": ai_analysis
    }

@app.get("/applications/my-applications/")
def get_my_applications(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    apps = db.query(models.Application).filter(models.Application.user_id == current_user.id).order_by(models.Application.created_at.desc()).all()
    return [
        {
            "id": str(a.id), 
            "name": a.project_name or f"Application {str(a.id)[:8]}", 
            "status": a.status, 
            "date": a.created_at
        } 
        for a in apps
    ]

@app.post("/login/")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "message": "Login successful!"}

@app.get("/dashboard/my-status/")
def get_secure_dashboard(app_id: Optional[str] = None, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if app_id:
        application = db.query(models.Application).filter(models.Application.user_id == current_user.id, models.Application.id == app_id).first()
    else:
        application = db.query(models.Application).filter(models.Application.user_id == current_user.id).order_by(models.Application.created_at.desc()).first()
    
    if not application:
        return {"message": f"Welcome {current_user.full_name}! No applications found yet.", "dashboard": []}

    department_tickets = db.query(models.DepartmentApproval).filter(models.DepartmentApproval.application_id == application.id).order_by(models.DepartmentApproval.status.desc()).all()

    dashboard_data = []
    for ticket in department_tickets:
        # Unpack the injected string if it exists
        lic_str = ticket.license_type or "General Approval"
        doc_req = "Standard Document"
        sla = "N/A"
        
        if " | DOC_REQ: " in lic_str:
            parts = lic_str.split(" | ")
            lic_str = parts[0]
            if len(parts) > 1:
                doc_req = parts[1].replace("DOC_REQ: ", "")
            if len(parts) > 2:
                sla = parts[2].replace("SLA: ", "")

        dashboard_data.append({
            "ticket_id": str(ticket.id),
            "department": ticket.department.name, 
            "license_name": lic_str,
            "document_required": doc_req,
            "sla": sla,
            "status": ticket.status,
            "officer_comments": ticket.official_notes, 
            "last_updated": ticket.updated_at
        })

    return {
        "applicant": current_user.full_name,
        "business_name": application.project_name or "My Business",
        "overall_status": application.status,
        "total_progress": f"{len([t for t in department_tickets if t.status == 'Approved'])}/{len(department_tickets)} Completed",
        "department_breakdown": dashboard_data
    }

@app.patch("/departments/review/")
def official_review(review: DepartmentReview, db: Session = Depends(get_db)):
    ticket = db.query(models.DepartmentApproval).filter(models.DepartmentApproval.id == review.approval_id).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Approval ticket not found.")
        
    ticket.status = review.new_status
    ticket.official_notes = review.comments
    db.commit()
    
    return {"message": f"Ticket for {ticket.department.name} updated to {review.new_status}"}

@app.get("/admin/statistics/")
def get_government_statistics(db: Session = Depends(get_db)):
    total_users = db.query(models.User).count()
    total_applications = db.query(models.Application).count()
    
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
    try:
        tickets = db.query(models.DepartmentApproval).filter(
            models.DepartmentApproval.status == "In Review"
        ).all()
        
        results = []
        for ticket in tickets:
            app_record = db.query(models.Application).filter(models.Application.id == ticket.application_id).first()
            user = db.query(models.User).filter(models.User.id == app_record.user_id).first() if app_record else None
            
            dept_name = ticket.department.name if hasattr(ticket, "department") and ticket.department else "General"
            
            lic_str = ticket.license_type or "General Approval"
            if " | DOC_REQ: " in lic_str:
                lic_str = lic_str.split(" | ")[0]

            notes = getattr(ticket, "official_notes", None) or "Awaiting final sign-off."
            
            doc = None
            if user:
                # Get the most recent doc matching the department or license type
                doc = db.query(models.Document).filter(
                    models.Document.user_id == user.id
                ).order_by(models.Document.created_at.desc()).first()

            doc_info = None
            if doc:
                doc_info = {
                    "file_url": doc.file_url,
                    "metadata": doc.ai_extracted_metadata
                }

            results.append({
                "ticket_id": str(ticket.id),
                "applicant": user.full_name if user else "Unknown Business",
                "department": dept_name,
                "license_type": lic_str,
                "status": ticket.status,
                "current_note": notes,
                "document": doc_info
            })
        return {"tickets": results}
    except Exception as e:
        print(f"Admin Dashboard Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/admin/tickets/review/")
def review_ticket(payload: OfficerDecision, db: Session = Depends(get_db)):
    ticket = db.query(models.DepartmentApproval).filter(models.DepartmentApproval.id == payload.ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")
        
    ticket.status = payload.decision
    ticket.official_notes = f"Official Verdict: {payload.comments}"
    db.commit()
    return {"message": f"Ticket {payload.ticket_id} marked as {payload.decision}."}