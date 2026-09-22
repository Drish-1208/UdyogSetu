import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# -------------------------------------------------------------------
# Junction Table (Many-to-Many) for Applications <-> Documents
# -------------------------------------------------------------------
application_documents = Table(
    'application_documents', 
    Base.metadata,
    Column('application_id', UUID(as_uuid=True), ForeignKey('applications.id'), primary_key=True),
    Column('document_id', UUID(as_uuid=True), ForeignKey('documents.id'), primary_key=True)
)

# -------------------------------------------------------------------
# Identity & Access Management
# -------------------------------------------------------------------
class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String(50), unique=True, nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="role")

class Department(Base):
    __tablename__ = 'departments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="department")
    approvals = relationship("DepartmentApproval", back_populates="department")

class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=True)
    full_name = Column(String(100))
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    business_profile = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Relationships
    role = relationship("Role", back_populates="users")
    department = relationship("Department", back_populates="users")
    documents = relationship("Document", back_populates="owner", foreign_keys='Document.user_id')
    applications = relationship("Application", back_populates="user")

# -------------------------------------------------------------------
# Documents & Applications
# -------------------------------------------------------------------
class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    document_type = Column(String(50))
    file_url = Column(String(255), nullable=False)
    verification_status = Column(String(20), default='Pending')
    ai_extracted_metadata = Column(JSONB, nullable=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Relationships
    owner = relationship("User", back_populates="documents", foreign_keys=[user_id])
    verifier = relationship("User", foreign_keys=[verified_by]) # One-way relationship to user who verified
    applications = relationship("Application", secondary=application_documents, back_populates="documents")

class Application(Base):
    __tablename__ = 'applications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    project_name = Column(String(150))
    status = Column(String(50), default='Draft')
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="applications")
    documents = relationship("Document", secondary=application_documents, back_populates="applications")
    approvals = relationship("DepartmentApproval", back_populates="application", cascade="all, delete-orphan")

class DepartmentApproval(Base):
    __tablename__ = 'department_approvals'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = Column(UUID(as_uuid=True), ForeignKey('applications.id'), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey('departments.id'), nullable=False)
    license_type = Column(String(100))
    status = Column(String(50), default='Pending')
    official_notes = Column(Text, nullable=True)
    assigned_official_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    updated_at = Column(
        DateTime(timezone=True), 
        default=datetime.now(timezone.utc), 
        onupdate=datetime.now(timezone.utc)
    )
    
    # Relationships
    application = relationship("Application", back_populates="approvals")
    department = relationship("Department", back_populates="approvals")
    assigned_official = relationship("User", foreign_keys=[assigned_official_id])