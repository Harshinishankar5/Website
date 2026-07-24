# app/models/demo_booking.py
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, func
from app.database import Base


class Products(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    email_address = Column(String(255), nullable=False)
    enter_company_details = Column(String(1000), nullable=False)
    enter_contact_details = Column(String(1000), nullable=False)
    booking_date = Column(Date, nullable=False)
    booking_time = Column(Time, nullable=False)
    created_at = Column(DateTime, server_default=func.now())