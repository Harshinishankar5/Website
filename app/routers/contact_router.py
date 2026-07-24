from typing import List

from fastapi import APIRouter, Depends, Form, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.contact_models import ContactUs
from app.schemas.contact_schemas import ContactUsResponse, PurposeEnum

router = APIRouter(
    prefix="/contact",
    tags=["Contact Us"]
)


@router.post(
    "/contact-us",
    response_model=ContactUsResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_contact(
    name: str = Form(...),
    email: str = Form(...),
    purpose: PurposeEnum = Form(...),
    country_code: str = Form(...),
    phone_number: str = Form(...),
    location: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    if not phone_number.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Phone number must contain only digits."
        )

    full_phone_number = f"{country_code} {phone_number}"

    contact = ContactUs(
        name=name,
        email=email,
        purpose=purpose.value,
        phone_number=full_phone_number,
        location=location,
        message=message,
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact


@router.get(
    "/contact-us",
    response_model=List[ContactUsResponse],
)
def get_contacts(
    db: Session = Depends(get_db),
):
    contacts = db.execute(
        select(ContactUs).order_by(ContactUs.created_at.desc())
    ).scalars().all()

    return contacts


@router.get(
    "/contact-us/{contact_id}",
    response_model=ContactUsResponse,
)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
):
    contact = db.execute(
        select(ContactUs).where(ContactUs.id == contact_id)
    ).scalar_one_or_none()

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact request not found",
        )

    return contact

