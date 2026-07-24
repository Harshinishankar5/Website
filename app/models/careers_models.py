from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float,
    Enum, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

# ─── Enums ────────────────────────────────────────────────────────────────────

class EmploymentTypeEnum(str, enum.Enum):
    full_time = "Full-Time"
    part_time = "Part-Time"
    contract = "Contract"
    internship = "Internship"
    freelance = "Freelance"


class WorkModeEnum(str, enum.Enum):
    onsite = "Onsite"
    remote = "Remote"
    hybrid = "Hybrid"


class ExperienceLevelEnum(str, enum.Enum):
    entry = "Entry"
    mid = "Mid"
    senior = "Senior"
    lead = "Lead"
    manager = "Manager"


class JobStatusEnum(str, enum.Enum):
    draft = "Draft"
    active = "Active"
    closed = "Closed"
    paused = "Paused"


class SkillTypeEnum(str, enum.Enum):
    technical = "technical"
    soft = "soft"


class FormFieldTypeEnum(str, enum.Enum):
    text = "text"
    email = "email"
    tel = "tel"
    number = "number"
    textarea = "textarea"
    file = "file"
    select = "select"
    checkbox = "checkbox"


class ResumeFormatEnum(str, enum.Enum):
    pdf = "pdf"
    doc = "doc"
    docx = "docx"
    rtf = "rtf"
    txt = "txt"


# ─── Models ───────────────────────────────────────────────────────────────────\



class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(255), nullable=False)
    job_category = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    employment_type = Column(Enum(EmploymentTypeEnum), nullable=False)
    job_location = Column(String(150), nullable=False)
    work_mode = Column(Enum(WorkModeEnum), nullable=False)
    experience_level = Column(Enum(ExperienceLevelEnum), nullable=False)
    years_of_experience = Column(Integer, nullable=False)
    number_of_openings = Column(Integer, nullable=False, default=1)
    job_status = Column(Enum(JobStatusEnum), nullable=False, default=JobStatusEnum.draft)
    job_expiry_date = Column(DateTime, nullable=True)
    job_description = Column(Text, nullable=True)
    preferred_qualifications = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    hero_section = relationship("JobHeroSection", back_populates="job", uselist=False, cascade="all, delete-orphan")
    responsibilities = relationship("JobResponsibility", back_populates="job", cascade="all, delete-orphan")
    requirements = relationship("JobRequirement", back_populates="job", cascade="all, delete-orphan")
    application_form_fields = relationship("ApplicationFormField", back_populates="job", cascade="all, delete-orphan")
    resume_settings = relationship("JobResumeSettings", back_populates="job", uselist=False, cascade="all, delete-orphan")


class JobHeroSection(Base):
    __tablename__ = "job_hero_sections"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True)
    hero_title = Column(String(255), nullable=True)       # empty = use job title
    show_back_button = Column(Boolean, default=True)


    # Store card display order as JSON array e.g. ["job_category", "employment_type", ...]
    card_order = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    job = relationship("Job", back_populates="hero_section")


class JobResponsibility(Base):
    __tablename__ = "job_responsibilities"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="responsibilities")


class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    skill_name = Column(String(150), nullable=False)
    skill_type = Column(Enum(SkillTypeEnum), nullable=False)   # "technical" | "soft"
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="requirements")


class ApplicationFormField(Base):
    __tablename__ = "application_form_fields"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    field_name = Column(String(150), nullable=False)       # e.g. "Full Name"
    field_key = Column(String(100), nullable=False)        # e.g. "full_name"
    field_type = Column(Enum(FormFieldTypeEnum), nullable=False)
    is_required = Column(Boolean, default=False)
    is_custom = Column(Boolean, default=False)             # True = added via "+ Add Custom Field"
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    job = relationship("Job", back_populates="application_form_fields")


class JobResumeSettings(Base):
    __tablename__ = "job_resume_settings"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True)
    allowed_formats = Column(JSON, nullable=False, default=["pdf", "doc", "docx"])
    max_file_size_mb = Column(Float, nullable=False, default=5.0)
    resume_upload_mandatory = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    job = relationship("Job", back_populates="resume_settings")
