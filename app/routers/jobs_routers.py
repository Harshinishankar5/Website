import os
import traceback
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.jobs_models import JobTitle
from app.models.jobs_models import JobApplication
from app.schemas.jobs_schemas import JobApplicationOut, JobTitleOut, JobTitleCreate
from app.core.s3 import upload_resume_to_s3

router = APIRouter(
    prefix="/job-applications",
    tags=["Job Applications"],
)


@router.post(
    "/",
    response_model=JobApplicationOut,
    status_code=status.HTTP_201_CREATED,
)
async def submit_application(
    job_id: int = Form(...),
    candidate_name: str = Form(...),
    enter_email: str = Form(...),
    country_code: str = Form(...),
    phone_number: str = Form(...),
    total_experience: float = Form(...),
    relevant_experience: float = Form(...),
    current_location: str = Form(...),
    current_ctc: float = Form(...),
    expected_ctc: float = Form(...),
    linkedin_profile_url: str | None = Form(None),
    technical_proficiency: str | None = Form(None),
    upload_your_latest_resume: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    job_title_obj = db.query(JobTitle).filter(JobTitle.id == job_id).first()
    if not job_title_obj:
        raise HTTPException(status_code=404, detail="Job title not found. Please create the job title before applying.")

    if not country_code.startswith("+"):
        raise HTTPException(status_code=400, detail="Country code must start with '+'.")

    if not phone_number.isdigit():
        raise HTTPException(status_code=400, detail="Phone number must contain only digits.")

    contact_number = f"{country_code} {phone_number}"

    contents = await upload_your_latest_resume.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Resume size should not exceed 2 MB.")

    upload_your_latest_resume.file.seek(0)

    extension = os.path.splitext(upload_your_latest_resume.filename)[1].lower()
    if extension not in [".pdf", ".doc", ".docx"]:
        raise HTTPException(status_code=400, detail="Only PDF, DOC and DOCX files are allowed.")

    try:
        resume_url = upload_resume_to_s3(upload_your_latest_resume.file, upload_your_latest_resume.filename)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to upload resume: {str(e)}")

    application = JobApplication(
        job_id=job_id,
        candidate_name=candidate_name,
        enter_email=enter_email,
        contact_number=contact_number,
        total_experience=total_experience,
        relevant_experience=relevant_experience,
        current_location=current_location,
        current_ctc=current_ctc,
        expected_ctc=expected_ctc,
        linkedin_profile_url=linkedin_profile_url,
        technical_proficiency=technical_proficiency,
        upload_your_latest_resume=resume_url,
    )

    try:
        db.add(application)
        db.commit()
        db.refresh(application)
    except Exception:
        db.rollback()
        raise

    return {**application.__dict__, "job_title": job_title_obj.job_title}


# ⚠️ STATIC ROUTE MUST COME BEFORE /{application_id}
@router.get(
    "/get_all_applications",
    response_model=List[JobApplicationOut],
)
def get_all_applications(db: Session = Depends(get_db)):
    results = (
        db.query(JobApplication, JobTitle.job_title)
        .join(JobTitle, JobTitle.id == JobApplication.job_id)
        .order_by(JobApplication.created_at.desc())
        .all()
    )
    return [{**application.__dict__, "job_title": job_title} for application, job_title in results]


# ⚠️ DYNAMIC ROUTE MUST COME AFTER /get_all_applications
@router.get(
    "/{application_id}",
    response_model=JobApplicationOut,
    status_code=status.HTTP_200_OK,
)
def get_application_by_id(
    application_id: int,
    db: Session = Depends(get_db),
):
    result = (
        db.query(JobApplication, JobTitle.job_title)
        .join(JobTitle, JobTitle.id == JobApplication.job_id)
        .filter(JobApplication.id == application_id)
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="Application not found.")

    application, job_title = result
    return {**application.__dict__, "job_title": job_title}


@router.post(
    "/job_title",
    response_model=JobTitleOut,
    status_code=status.HTTP_201_CREATED,
)
def create_job_title(
    payload: JobTitleCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(JobTitle)
        .filter(JobTitle.job_title == payload.job_title)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job title already exists."
        )

    job_title = JobTitle(job_title=payload.job_title)

    db.add(job_title)
    db.commit()
    db.refresh(job_title)

    return job_title


@router.get(
    "/",
    response_model=List[JobTitleOut],
)
def get_all_job_titles(db: Session = Depends(get_db)):
    return db.query(JobTitle).order_by(JobTitle.id.desc()).all()


@router.get(
    "/{job_title_id}",
    response_model=JobTitleOut,
)
def get_job_title_by_id(
    job_title_id: int,
    db: Session = Depends(get_db),
):
    job_title = (
        db.query(JobTitle)
        .filter(JobTitle.id == job_title_id)
        .first()
    )
    if not job_title:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job title not found."
        )
    return job_title