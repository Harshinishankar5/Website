from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl, Field

from pydantic import BaseModel, ConfigDict


class JobTitleCreate(BaseModel):
    job_title: str


class JobTitleOut(BaseModel):
    id: int
    job_title: str

    model_config = ConfigDict(from_attributes=True)

class JobApplicationBase(BaseModel):
    job_id: int
    candidate_name: str
    enter_email: EmailStr
    contact_number: str

    total_experience: float = Field(..., ge=0)
    relevant_experience: float = Field(..., ge=0)

    current_location: str

    current_ctc: float = Field(..., ge=0)
    expected_ctc: float = Field(..., ge=0)

    linkedin_profile_url: Optional[str] = None
    technical_proficiency: Optional[str] = None


class JobApplicationCreate(JobApplicationBase):
    pass


class JobApplicationOut(JobApplicationBase):
    id: int
    job_title: str
    upload_your_latest_resume: str

    class Config:
        from_attributes = True