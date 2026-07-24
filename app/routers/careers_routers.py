from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.core.dependencies import super_admin_required
from app.models.careers_models import (
    Job, JobHeroSection, JobResponsibility,
    JobRequirement, ApplicationFormField, JobResumeSettings
)
from app.schemas.careers_schemas import (
    JobCreate, JobUpdate, JobResponse, JobListResponse,
    JobHeroSectionCreate, JobHeroSectionUpdate, JobHeroSectionResponse,
    JobResponsibilityCreate, JobResponsibilityUpdate, JobResponsibilityResponse,
    JobRequirementCreate, JobRequirementResponse,
    ApplicationFormFieldCreate, ApplicationFormFieldUpdate, ApplicationFormFieldResponse,
    JobResumeSettingsCreate, JobResumeSettingsUpdate, JobResumeSettingsResponse, JobDescriptionCreate,
    JobDescriptionUpdate, JobDescriptionResponse, PreferredQualificationCreate,
    PreferredQualificationUpdate, PreferredQualificationResponse, JobCompleteResponse,
)
from app.database import get_db

router = APIRouter(prefix="/jobs", tags=["careers"])


# ───------------------- Helper ──────────────────────────────

def get_job_or_404(job_id: int, db: Session) -> Job:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ══════════════════════════════════════════════════════════════════════════════
# JOBS
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED,
                dependencies=[Depends(super_admin_required)])
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    job = Job(**payload.model_dump())

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.get("/", response_model=List[JobListResponse],dependencies=[Depends(super_admin_required)])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).all()


@router.get("/{job_id}", response_model=JobResponse,dependencies=[Depends(super_admin_required)])
def get_job(job_id: int, db: Session = Depends(get_db)):
    return get_job_or_404(job_id, db)


@router.patch("/{job_id}", response_model=JobResponse,dependencies=[Depends(super_admin_required)])
def update_job(job_id: int, payload: JobUpdate, db: Session = Depends(get_db)):
    job = get_job_or_404(job_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT,dependencies=[Depends(super_admin_required)])
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = get_job_or_404(job_id, db)
    db.delete(job)
    db.commit()


# ══════════════════════════════════════════════════════════════════════════════
# HERO SECTION
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/{job_id}/hero-section", response_model=JobHeroSectionResponse, status_code=201,dependencies=[Depends(super_admin_required)])
def create_hero_section(job_id: int, payload: JobHeroSectionCreate, db: Session = Depends(get_db)):
    get_job_or_404(job_id, db)
    if db.query(JobHeroSection).filter(JobHeroSection.job_id == job_id).first():
        raise HTTPException(status_code=400, detail="Hero section already exists for this job")
    hero = JobHeroSection(job_id=job_id, **payload.model_dump())
    db.add(hero)
    db.commit()
    db.refresh(hero)
    return hero


@router.get("/{job_id}/hero-section", response_model=JobHeroSectionResponse,dependencies=[Depends(super_admin_required)])
def get_hero_section(job_id: int, db: Session = Depends(get_db)):
    get_job_or_404(job_id, db)
    hero = db.query(JobHeroSection).filter(JobHeroSection.job_id == job_id).first()
    if not hero:
        raise HTTPException(status_code=404, detail="Hero section not found")
    return hero


@router.patch("/{job_id}/hero-section", response_model=JobHeroSectionResponse,dependencies=[Depends(super_admin_required)])
def update_hero_section(job_id: int, payload: JobHeroSectionUpdate, db: Session = Depends(get_db)):
    get_job_or_404(job_id, db)
    hero = db.query(JobHeroSection).filter(JobHeroSection.job_id == job_id).first()
    if not hero:
        raise HTTPException(status_code=404, detail="Hero section not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(hero, field, value)
    db.commit()
    db.refresh(hero)
    return hero

# ══════════════════════════════════════════════════════════════════════════════
# DESCRIPTION
# ══════════════════════════════════════════════════════════════════════════════
@router.post(
    "/{job_id}/description",
    response_model=JobDescriptionResponse,
    status_code=201,
dependencies=[Depends(super_admin_required)]
)
def create_job_description(
    job_id: int,
    payload: JobDescriptionCreate,
    db: Session = Depends(get_db)
):
    job = get_job_or_404(job_id, db)

    job.job_description = payload.job_description

    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "job_description": job.job_description
    }


@router.get(
    "/{job_id}/description",
    response_model=JobDescriptionResponse,
dependencies=[Depends(super_admin_required)]
)
def get_job_description(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = get_job_or_404(job_id, db)

    return {
        "job_id": job.id,
        "job_description": job.job_description
    }


@router.patch(
    "/{job_id}/description",
    response_model=JobDescriptionResponse,
dependencies=[Depends(super_admin_required)]
)
def update_job_description(
    job_id: int,
    payload: JobDescriptionUpdate,
    db: Session = Depends(get_db)
):
    job = get_job_or_404(job_id, db)

    if payload.job_description is not None:
        job.job_description = payload.job_description

    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "job_description": job.job_description
    }

# ══════════════════════════════════════════════════════════════════════════════
# PREFERRED QUALIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/{job_id}/qualifications",
    response_model=PreferredQualificationResponse,
    status_code=201,
dependencies=[Depends(super_admin_required)]
)
def create_preferred_qualifications(
    job_id: int,
    payload: PreferredQualificationCreate,
    db: Session = Depends(get_db)
):
    job = get_job_or_404(job_id, db)

    job.preferred_qualifications = payload.preferred_qualifications

    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "preferred_qualifications": job.preferred_qualifications
    }


@router.get(
    "/{job_id}/qualifications",
    response_model=PreferredQualificationResponse,
dependencies=[Depends(super_admin_required)]
)
def get_preferred_qualifications(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = get_job_or_404(job_id, db)

    return {
        "job_id": job.id,
        "preferred_qualifications": job.preferred_qualifications
    }


@router.patch(
    "/{job_id}/qualifications",
    response_model=PreferredQualificationResponse,
dependencies=[Depends(super_admin_required)]
)
def update_preferred_qualifications(
    job_id: int,
    payload: PreferredQualificationUpdate,
    db: Session = Depends(get_db)
):
    job = get_job_or_404(job_id, db)

    if payload.preferred_qualifications is not None:
        job.preferred_qualifications = payload.preferred_qualifications

    db.commit()
    db.refresh(job)

    return {
        "job_id": job.id,
        "preferred_qualifications": job.preferred_qualifications
    }

# ══════════════════════════════════════════════════════════════════════════════
# RESPONSIBILITIES
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/{job_id}/responsibilities",
             response_model=JobResponsibilityResponse,
             status_code=201,
             dependencies=[Depends(super_admin_required)])
def add_responsibility(job_id: int, payload: JobResponsibilityCreate, db: Session = Depends(get_db)):
    get_job_or_404(job_id, db)
    r = JobResponsibility(job_id=job_id, **payload.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.get("/{job_id}/responsibilities",
            response_model=List[JobResponsibilityResponse],
            dependencies=[Depends(super_admin_required)])
def list_responsibilities(job_id: int, db: Session = Depends(get_db)):
    get_job_or_404(job_id, db)
    return (
        db.query(JobResponsibility)
        .filter(JobResponsibility.job_id == job_id)
        .order_by(JobResponsibility.display_order)
        .all()
    )


@router.patch("/{job_id}/responsibilities/{resp_id}",
              response_model=JobResponsibilityResponse,
              dependencies=[Depends(super_admin_required)])
def update_responsibility(job_id: int, resp_id: int, payload: JobResponsibilityUpdate, db: Session = Depends(get_db)):
    get_job_or_404(job_id, db)
    r = db.query(JobResponsibility).filter(
        JobResponsibility.id == resp_id,
        JobResponsibility.job_id == job_id
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Responsibility not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(r, field, value)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{job_id}/responsibilities/{resp_id}",
               status_code=204,
               dependencies=[Depends(super_admin_required)])
def delete_responsibility(job_id: int, resp_id: int, db: Session = Depends(get_db)):
    get_job_or_404(job_id, db)
    r = db.query(JobResponsibility).filter(
        JobResponsibility.id == resp_id,
        JobResponsibility.job_id == job_id
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Responsibility not found")
    db.delete(r)
    db.commit()


# ══════════════════════════════════════════════════════════════════════════════
# REQUIREMENTS (Skills)
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/{job_id}/requirements",
             response_model=JobRequirementResponse,
             status_code=201,
             dependencies=[Depends(super_admin_required)])
def add_requirement(job_id: int, payload: JobRequirementCreate, db: Session = Depends(get_db)):
    get_job_or_404(job_id, db)
    req = JobRequirement(job_id=job_id, **payload.model_dump())
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get("/{job_id}/requirements", response_model=List[JobRequirementResponse]
            ,dependencies=[Depends(super_admin_required)])
def list_requirements(job_id: int, db: Session = Depends(get_db)):
    get_job_or_404(job_id, db)
    return db.query(JobRequirement).filter(JobRequirement.job_id == job_id).all()


@router.delete("/{job_id}/requirements/{req_id}",
               status_code=204,dependencies=[Depends(super_admin_required)])
def delete_requirement(job_id: int, req_id: int, db: Session = Depends(get_db)):
    get_job_or_404(job_id, db)
    req = db.query(JobRequirement).filter(
        JobRequirement.id == req_id,
        JobRequirement.job_id == job_id
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    db.delete(req)
    db.commit()


# ══════════════════════════════════════════════════════════════════════════════
# APPLICATION FORM FIELDS
# ══════════════════════════════════════════════════════════════════════════════

# @router.post("/{job_id}/form-fields",
#              response_model=ApplicationFormFieldResponse,
#              status_code=201,
#              dependencies=[Depends(super_admin_required)])
# def add_form_field(job_id: int, payload: ApplicationFormFieldCreate, db: Session = Depends(get_db)):
#     get_job_or_404(job_id, db)
#     field = ApplicationFormField(job_id=job_id, **payload.model_dump())
#     db.add(field)
#     db.commit()
#     db.refresh(field)
#     return field
#
#
# @router.get("/{job_id}/form-fields", response_model=List[ApplicationFormFieldResponse],
#             dependencies=[Depends(super_admin_required)])
# def list_form_fields(job_id: int, db: Session = Depends(get_db)):
#     get_job_or_404(job_id, db)
#     return (
#         db.query(ApplicationFormField)
#         .filter(ApplicationFormField.job_id == job_id)
#         .order_by(ApplicationFormField.display_order)
#         .all()
#     )
#
#
# @router.patch("/{job_id}/form-fields/{field_id}", response_model=ApplicationFormFieldResponse,
#               dependencies=[Depends(super_admin_required)])
# def update_form_field(job_id: int, field_id: int, payload: ApplicationFormFieldUpdate, db: Session = Depends(get_db)):
#     get_job_or_404(job_id, db)
#     field = db.query(ApplicationFormField).filter(
#         ApplicationFormField.id == field_id,
#         ApplicationFormField.job_id == job_id
#     ).first()
#     if not field:
#         raise HTTPException(status_code=404, detail="Form field not found")
#     for key, value in payload.model_dump(exclude_unset=True).items():
#         setattr(field, key, value)
#     db.commit()
#     db.refresh(field)
#     return field
#
#
# @router.delete("/{job_id}/form-fields/{field_id}", status_code=204,
#                dependencies=[Depends(super_admin_required)])
# def delete_form_field(job_id: int, field_id: int, db: Session = Depends(get_db)):
#     get_job_or_404(job_id, db)
#     field = db.query(ApplicationFormField).filter(
#         ApplicationFormField.id == field_id,
#         ApplicationFormField.job_id == job_id
#     ).first()
#     if not field:
#         raise HTTPException(status_code=404, detail="Form field not found")
#     db.delete(field)
#     db.commit()
#

# ══════════════════════════════════════════════════════════════════════════════
# RESUME SETTINGS
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/{job_id}/resume-settings", response_model=JobResumeSettingsResponse,
             status_code=201,
             dependencies=[Depends(super_admin_required)])
def create_resume_settings(job_id: int, payload: JobResumeSettingsCreate, db: Session = Depends(get_db)):
    get_job_or_404(job_id, db)
    if db.query(JobResumeSettings).filter(JobResumeSettings.job_id == job_id).first():
        raise HTTPException(status_code=400, detail="Resume settings already exist for this job")
    settings = JobResumeSettings(job_id=job_id, **payload.model_dump())
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings


@router.get("/{job_id}/resume-settings",
            response_model=JobResumeSettingsResponse,
            dependencies=[Depends(super_admin_required)])
def get_resume_settings(job_id: int, db: Session = Depends(get_db)):
    get_job_or_404(job_id, db)
    settings = db.query(JobResumeSettings).filter(JobResumeSettings.job_id == job_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Resume settings not found")
    return settings


@router.patch("/{job_id}/resume-settings",
              response_model=JobResumeSettingsResponse,
              dependencies=[Depends(super_admin_required)])
def update_resume_settings(job_id: int, payload: JobResumeSettingsUpdate, db: Session = Depends(get_db)):
    get_job_or_404(job_id, db)
    settings = db.query(JobResumeSettings).filter(JobResumeSettings.job_id == job_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Resume settings not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings


@router.get(
    "/{job_id}/all",
    response_model=JobCompleteResponse,
    dependencies=[Depends(super_admin_required)]
)
def get_job_all(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = (
        db.query(Job)
        .options(
            joinedload(Job.hero_section),
            joinedload(Job.responsibilities),
            joinedload(Job.requirements),
            joinedload(Job.resume_settings),
            joinedload(Job.application_form_fields),   # if required
        )
        .filter(Job.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return {
        "job": job,
        "hero_section": job.hero_section,
        "description": {
            "job_id": job.id,
            "job_description": job.job_description,
        },
        "preferred_qualifications": {
            "job_id": job.id,
            "preferred_qualifications": job.preferred_qualifications,
        },
        "responsibilities": job.responsibilities,
        "requirements": job.requirements,
        "resume_settings": job.resume_settings,
        "form_fields": job.application_form_fields,
    }


@router.delete(
    "/{job_id}/complete",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(super_admin_required)]
)
def delete_complete_job(job_id: int, db: Session = Depends(get_db)):
    job = get_job_or_404(job_id, db)

    # Delete Hero Section
    db.query(JobHeroSection).filter(
        JobHeroSection.job_id == job_id
    ).delete(synchronize_session=False)

    # Delete Responsibilities
    db.query(JobResponsibility).filter(
        JobResponsibility.job_id == job_id
    ).delete(synchronize_session=False)

    # Delete Requirements
    db.query(JobRequirement).filter(
        JobRequirement.job_id == job_id
    ).delete(synchronize_session=False)

    # Delete Resume Settings
    db.query(JobResumeSettings).filter(
        JobResumeSettings.job_id == job_id
    ).delete(synchronize_session=False)

    # If ApplicationFormField is enabled
    db.query(ApplicationFormField).filter(
        ApplicationFormField.job_id == job_id
    ).delete(synchronize_session=False)

    # Finally delete the Job
    db.delete(job)

    db.commit()