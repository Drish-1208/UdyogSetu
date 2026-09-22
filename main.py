from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import our database tools and recipe book
from database import SessionLocal
import models

app = FastAPI()

# ==========================================
# 1. Pydantic Schemas (The Order Tickets)
# ==========================================
class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str

class BusinessProfile(BaseModel):
    email: str
    sector: str
    employee_count: int
    has_hazardous_chemicals: bool

# ==========================================
# 2. Database Dependency
# ==========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    
    # Catch duplicate emails to prevent 500 Server Errors!
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="This email is already registered.")

    # Create dummy "entrepreneur" role if it doesn't exist
    role = db.query(models.Role).filter(models.Role.role_name == "entrepreneur").first()
    if not role:
        role = models.Role(role_name="entrepreneur")
        db.add(role)
        db.commit()
        db.refresh(role)

    # Create the actual user
    new_user = models.User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=user_data.password, # In a real app, hash this!
        role_id=role.id
    )
    
    db.add(new_user)
    db.commit()
    
    return {"message": "Success! User saved to Database.", "name": new_user.full_name}


@app.post("/onboarding/")
def generate_checklist(profile: BusinessProfile, db: Session = Depends(get_db)):
    
    # Base approvals everyone needs
    required_approvals = {"Company Registration (MCA)", "GST Registration", "Shops & Establishment License"}
    
    # Dynamic Matrix Lookup (O(1) time complexity)
    sector_approvals = INDUSTRY_REQUIREMENTS.get(profile.sector.lower(), [])
    required_approvals.update(sector_approvals)
    
    # Dynamic Conditional Evaluator (O(N) time complexity)
    for rule in CONDITIONAL_REQUIREMENTS:
        if rule["evaluator"](profile):
            required_approvals.update(rule["approvals"])
            
    # Convert the set back to a list for JSON response
    final_checklist = list(required_approvals)
        
    # Save to JSONB in database
    user = db.query(models.User).filter(models.User.email == profile.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register first.")
        
    user.business_profile = profile.model_dump() 
    db.commit()
        
    return {
        "message": "Checklist generated using scalable Rules Engine!",
        "total_approvals_required": len(final_checklist),
        "required_approvals": final_checklist
    }
import json

def analyze_document_with_ai(document_type: str, file_name: str):
    """
    In the final hackathon version, you will pass the file bytes to 
    your OpenAI or Google AI Pro API here.
    """
    
    # We prompt the AI to return this exact JSON structure:
    mock_ai_response = """
    {
        "is_valid": true,
        "confidence_score": 0.96,
        "extracted_data": {
            "document_number": "MH-2026-XYZ890",
            "issue_date": "2023-05-14",
            "expiry_date": "2028-05-13",
            "signatures_present": true
        },
        "critical_flags": []
    }
    """
    # Convert the text string into a Python dictionary
    return json.loads(mock_ai_response)
@app.post("/documents/upload/")
async def upload_document(
    email: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Verify the user exists
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # 2. Security Check
    allowed_types = ["application/pdf", "image/jpeg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    fake_cloud_url = f"https://s3-bucket.com/uploads/{file.filename}"
    
    # 3. Run the AI Scrutiny
    ai_analysis = analyze_document_with_ai(document_type, file.filename)
    
    # 4. Auto-Verification Logic
    # If the AI is highly confident and found no missing signatures, instantly verify it!
    auto_status = "Pending"
    if ai_analysis["is_valid"] and ai_analysis["confidence_score"] > 0.90:
        auto_status = "Verified"

    # 5. Save everything to the database
    new_document = models.Document(
        user_id=user.id,
        document_type=document_type,
        file_url=fake_cloud_url,
        verification_status=auto_status,
        ai_extracted_metadata=ai_analysis # Saves the entire JSON dictionary!
    )
    
    db.add(new_document)
    db.commit()
    
    return {
        "message": f"Successfully processed {file.filename}",
        "document_type": document_type,
        "status": auto_status,
        "extracted_metadata": ai_analysis
    }