from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base

class BookAppointment(Base):
    __tablename__ = "book_appointment"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)

    service_type = Column(String(100), nullable=False)
    message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

