# app/schemas/demo_booking.py
from pydantic import BaseModel, EmailStr
from datetime import date, time, datetime


class DemoBookingCreate(BaseModel):
    full_name: str
    product_name : str
    email_address: EmailStr
    enter_company_details: str
    enter_contact_details: str
    booking_date: date
    booking_time: time


class DemoBookingOut(BaseModel):
    id: int
    full_name: str
    product_name : str
    email_address: EmailStr
    enter_company_details: str
    enter_contact_details: str
    booking_date: date
    booking_time: time
    created_at: datetime

    class Config:
        from_attributes = True
