from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.blogs_models import Blogs_Demo
from app.schemas.blogs_schemas import DemoRequestCreate, DemoRequestResponse

router = APIRouter(
    prefix="/blogs-demo",
    tags=["Blogs Demo"],
)


@router.post(
    "/",
    response_model=DemoRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_demo_request(
    data: DemoRequestCreate,
    db: Session = Depends(get_db),
):
    demo = Blogs_Demo(
        full_name=data.full_name,
        company_name=data.company_name,
        work_email=data.work_email,
        phone_number=f"{data.country_code} {data.phone_number}",
        business_need=data.business_need,
    )

    db.add(demo)
    db.commit()
    db.refresh(demo)

    return demo


@router.get(
    "/",
    response_model=List[DemoRequestResponse],
)
def get_demo_requests(
    db: Session = Depends(get_db),
):
    result = db.execute(
        select(Blogs_Demo).order_by(Blogs_Demo.created_at.desc())
    )
    return result.scalars().all()


@router.get(
    "/{request_id}",
    response_model=DemoRequestResponse,
)
def get_demo_request(
    request_id: int,
    db: Session = Depends(get_db),
):
    result = db.execute(
        select(Blogs_Demo).where(Blogs_Demo.id == request_id)
    )

    demo = result.scalar_one_or_none()

    if demo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Demo request not found",
        )

    return demo