from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.core.dependencies import require_roles
from app.models.users import UserRole
from app.models.blogs_models import BlogPost, BlogStatus
from app.models.careers_models import Job, JobStatusEnum
from app.models.jobs_models import JobApplication

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/analytics")
def get_analytics(db: Session = Depends(get_db)):

    total_blogs = db.query(func.count(BlogPost.id)).scalar()

    active_blogs = (
        db.query(func.count(BlogPost.id))
        .filter(BlogPost.status == BlogStatus.ACTIVE)
        .scalar()
    )

    total_jobs = db.query(func.count(Job.id)).scalar()

    open_positions = (
        db.query(func.count(Job.id))
        .filter(Job.job_status == JobStatusEnum.active)
        .scalar()
    )

    applications = db.query(func.count(JobApplication.id)).scalar()

    recent_jobs = (
        db.query(Job)
        .order_by(Job.created_at.desc())
        .limit(5)
        .all()
    )

    recent_jobs_data = [
        {
            "id": job.id,
            "title": job.job_title,
            "department": job.department,
            "location": job.job_location,
            "employment_type": job.employment_type,
            "status": job.job_status,
            "date": job.created_at.strftime("%Y-%m-%d") if job.created_at else None,
        }
        for job in recent_jobs
    ]

    recent_blogs = (
        db.query(BlogPost)
        .order_by(BlogPost.created_at.desc())
        .limit(5)
        .all()
    )

    recent_blogs_data = [
        {
            "id": blog.id,
            "title": blog.title,
            "category": blog.category,
            "author": blog.author,
            "status": blog.status,
            "date": blog.created_at.strftime("%Y-%m-%d") if blog.created_at else None,
        }
        for blog in recent_blogs
    ]

    return {
        "success": True,
        "data": {
            "total_blogs": total_blogs,
            "active_blogs": active_blogs,
            "total_jobs": total_jobs,
            "open_positions": open_positions,
            "applications": applications,
            "recent_blogs": recent_blogs_data,
            "recent_jobs": recent_jobs_data,
        }
    }


@router.get(
    "/blogs/search")
def search_blogs(
    blog_id: int = Query(None),
    blog_date: date = Query(None),
    db: Session = Depends(get_db)
):

    query = db.query(BlogPost)

    if blog_id is not None:
        query = query.filter(BlogPost.id == blog_id)

    if blog_date is not None:
        query = query.filter(func.date(BlogPost.created_at) == blog_date)

    blogs = query.order_by(BlogPost.created_at.desc()).all()

    blogs_data = [
        {
            "id": blog.id,
            "title": blog.title,
            "category": blog.category,
            "author": blog.author,
            # "views": blog.views,
            "status": blog.status,
            "date": blog.created_at.strftime("%Y-%m-%d") if blog.created_at else None,
        }
        for blog in blogs
    ]

    return {
        "success": True,
        "count": len(blogs_data),
        "data": blogs_data
    }