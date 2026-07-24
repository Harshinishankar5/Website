from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import  super_admin_required
from app.database import get_db
from app.models.book_appointment import BookAppointment
from app.schemas.book_appointment import BookAppointmentCreate

router = APIRouter(
    prefix="/book-appointment",
    tags=["Book Appointment"]
)

@router.post("/")
def book_appointment_create(
    payload: BookAppointmentCreate,
    db: Session = Depends(get_db)
):
    if not payload.phone_number.isdigit():
        raise HTTPException(
            status_code=400,
            detail="Phone number must contain only digits."
        )

    full_phone_number = f"{payload.country_code} {payload.phone_number}"

    appointment = BookAppointment(
        name=payload.name.strip(),
        email=payload.email,
        phone_number=full_phone_number,
        service_type=payload.service_type.strip(),
        message=payload.message.strip() if payload.message else None
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return {
        "success": True,
        "message": "Appointment request submitted successfully",
        "id": appointment.id
    }

@router.get("/{appointment_id}")
def get_all_appointments(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    appointment = (
        db.query(BookAppointment)
        .filter(BookAppointment.id == appointment_id)
        .first()
    )

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    return {
        "success": True,
        "data": appointment
    }

@router.get("/")
def get_book_appointments_by_id(
    db: Session = Depends(get_db)
):
    appointments = db.query(BookAppointment).all()

    return {
        "success": True,
        "count": len(appointments),
        "data": appointments
    }