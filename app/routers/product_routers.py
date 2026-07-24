# app/routers/demo_booking.py
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.database import get_db
from app.models.products import Products
from app.schemas.products_schemas import DemoBookingCreate, DemoBookingOut

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/create-booking")
def create_booking(payload: DemoBookingCreate, db: Session = Depends(get_db)):
    # Combine booking date and time
    booking_datetime = datetime.combine(
        payload.booking_date,
        payload.booking_time
    )

    # Prevent booking in the past
    if booking_datetime <= datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Cannot book a past date and time."
        )

    # Check if slot is already booked
    existing = db.query(Products).filter(
        and_(
            Products.booking_date == payload.booking_date,
            Products.booking_time == payload.booking_time,
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="This slot is already booked."
        )

    booking = Products(**payload.dict())
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return {
        "success": True,
        "data": DemoBookingOut.from_orm(booking)
    }


@router.get("/list-bookings")
def list_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Products).order_by(
        Products.booking_date, Products.booking_time
    ).all()
    return {"success": True, "data": [DemoBookingOut.from_orm(b) for b in bookings]}


@router.get("/get/{booking_id}")
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Products).filter(Products.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"success": True, "data": DemoBookingOut.from_orm(booking)}


@router.get("/available-slots/{year}/{month}")
def get_booked_slots(year: int, month: int, db: Session = Depends(get_db)):
    booked = db.query(Products.booking_date, Products.booking_time).filter(
        and_(
            func.year(Products.booking_date) == year,
            func.month(Products.booking_date) == month,
        )
    ).all()
    return {"success": True, "data": [{"date": b[0], "time": b[1]} for b in booked]}