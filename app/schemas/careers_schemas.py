from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class EmploymentTypeEnum(str, Enum):
    full_time = "Full-Time"
    part_time = "Part-Time"
    contract = "Contract"
    internship = "Internship"
    freelance = "Freelance"


class WorkModeEnum(str, Enum):
    onsite = "Onsite"
    remote = "Remote"
    hybrid = "Hybrid"


class ExperienceLevelEnum(str, Enum):
    entry = "Entry"
    mid = "Mid"
    senior = "Senior"
    lead = "Lead"
    manager = "Manager"


class JobStatusEnum(str, Enum):
    draft = "Draft"
    active = "Active"
    closed = "Closed"
    paused = "Paused"


class SkillTypeEnum(str, Enum):
    technical = "technical"
    soft = "soft"


class FormFieldTypeEnum(str, Enum):
    text = "text"
    email = "email"
    tel = "tel"
    number = "number"
    textarea = "textarea"
    file = "file"
    select = "select"
    checkbox = "checkbox"


class ResumeFormatEnum(str, Enum):
    pdf = "pdf"
    doc = "doc"
    docx = "docx"
    rtf = "rtf"
    txt = "txt"


# ─── JobHeroSection Schemas ───────────────────────────────────────────────────

class JobHeroSectionBase(BaseModel):
    hero_title: Optional[str] = Field(None, description="Leave empty to use job title")
    card_order: Optional[List[str]] = None


class JobHeroSectionCreate(JobHeroSectionBase):
    pass


class JobHeroSectionUpdate(BaseModel):
    hero_title: Optional[str] = None
    card_order: Optional[List[str]] = None


class JobHeroSectionResponse(JobHeroSectionBase):
    id: int
    job_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── JobResponsibility Schemas ────────────────────────────────────────────────

class JobResponsibilityBase(BaseModel):
    title: str = Field(..., example="Automation Framework Development")
    description: Optional[str] = None
    display_order: int = 0


class JobResponsibilityCreate(JobResponsibilityBase):
    pass


class JobResponsibilityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None


class JobResponsibilityResponse(JobResponsibilityBase):
    id: int
    job_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── JobRequirement Schemas ───────────────────────────────────────────────────

class JobRequirementBase(BaseModel):
    skill_name: str = Field(..., example="Python")
    skill_type: SkillTypeEnum


class JobRequirementCreate(JobRequirementBase):
    pass


class JobRequirementResponse(JobRequirementBase):
    id: int
    job_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── ApplicationFormField Schemas ─────────────────────────────────────────────

class ApplicationFormFieldBase(BaseModel):
    field_name: str = Field(..., example="Full Name")
    field_key: str = Field(..., example="full_name")
    field_type: FormFieldTypeEnum
    is_required: bool = False
    is_custom: bool = False
    display_order: int = 0


class ApplicationFormFieldCreate(ApplicationFormFieldBase):
    pass


class ApplicationFormFieldUpdate(BaseModel):
    field_name: Optional[str] = None
    field_type: Optional[FormFieldTypeEnum] = None
    is_required: Optional[bool] = None
    display_order: Optional[int] = None


class ApplicationFormFieldResponse(ApplicationFormFieldBase):
    id: int
    job_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── JobResumeSettings Schemas ────────────────────────────────────────────────

class JobResumeSettingsBase(BaseModel):
    allowed_formats: List[ResumeFormatEnum] = [
        ResumeFormatEnum.pdf,
        ResumeFormatEnum.doc,
        ResumeFormatEnum.docx,
    ]
    max_file_size_mb: float = Field(5.0, ge=1.0, le=20.0)
    resume_upload_mandatory: bool = True

    @validator("allowed_formats")
    def formats_not_empty(cls, v):
        if not v:
            raise ValueError("At least one file format must be allowed")
        return v


class JobResumeSettingsCreate(JobResumeSettingsBase):
    pass


class JobResumeSettingsUpdate(BaseModel):
    allowed_formats: Optional[List[ResumeFormatEnum]] = None
    max_file_size_mb: Optional[float] = Field(None, ge=1.0, le=20.0)
    resume_upload_mandatory: Optional[bool] = None


class JobResumeSettingsResponse(JobResumeSettingsBase):
    id: int
    job_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Job Schemas ──────────────────────────────────────────────────────────────

class JobBase(BaseModel):
    job_title: str
    job_category: str
    department: str
    employment_type: EmploymentTypeEnum
    job_location: str
    work_mode: WorkModeEnum
    experience_level: ExperienceLevelEnum
    years_of_experience: int = Field(..., ge=0)
    number_of_openings: int = 1
    job_status: JobStatusEnum = JobStatusEnum.draft
    job_expiry_date: Optional[datetime] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    job_title: Optional[str] = None
    job_category: Optional[str] = None
    department: Optional[str] = None
    employment_type: Optional[EmploymentTypeEnum] = None
    job_location: Optional[str] = None
    work_mode: Optional[WorkModeEnum] = None
    experience_level: Optional[ExperienceLevelEnum] = None
    years_of_experience: int = Field(..., ge=0)
    number_of_openings: Optional[int] = Field(None, ge=1)
    job_status: Optional[JobStatusEnum] = None
    job_expiry_date: Optional[datetime] = None


class JobResponse(JobBase):
    id: int
    created_at: datetime
    updated_at: datetime


    class Config:
        from_attributes = True

class JobDescriptionCreate(BaseModel):
    job_description: str


class JobDescriptionUpdate(BaseModel):
    job_description: Optional[str] = None


class JobDescriptionResponse(BaseModel):
    job_id: int
    job_description: Optional[str]

    class Config:
        from_attributes = True

class PreferredQualificationCreate(BaseModel):
    preferred_qualifications: str


class PreferredQualificationUpdate(BaseModel):
    preferred_qualifications: Optional[str] = None


class PreferredQualificationResponse(BaseModel):
    job_id: int
    preferred_qualifications: Optional[str]

    class Config:
        from_attributes = True

class JobListResponse(BaseModel):
    id: int
    job_title: str
    job_category: str
    department: str
    employment_type: EmploymentTypeEnum
    job_location: str
    work_mode: WorkModeEnum
    experience_level: ExperienceLevelEnum
    number_of_openings: int
    job_status: JobStatusEnum
    job_expiry_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class JobCompleteResponse(BaseModel):
    job: JobResponse

    hero_section: Optional[JobHeroSectionResponse] = None

    description: Optional[JobDescriptionResponse] = None

    preferred_qualifications: Optional[PreferredQualificationResponse] = None

    responsibilities: List[JobResponsibilityResponse] = []

    requirements: List[JobRequirementResponse] = []

    resume_settings: Optional[JobResumeSettingsResponse] = None

    # Uncomment if you enable Application Form Fields
    # form_fields: List[ApplicationFormFieldResponse] = []

    class Config:
        from_attributes = True