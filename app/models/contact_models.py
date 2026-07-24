from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum
from app.database import Base
from sqlalchemy import String, Text, DateTime, Enum as SQLEnum

class PurposeEnum(str,Enum):
    BUSINESS_ENQUIRY = "Business Enquiry"
    PARTNERSHIP = "Partnership"
    SUPPORT = "Support"
    CAREERS = "Careers"
    OTHER = "Other"

class ContactUs(Base):
    __tablename__ = "contact_us"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False)

    email: Mapped[str] = mapped_column(String(255), nullable=False)

    purpose: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)

    location: Mapped[str] = mapped_column(String(255), nullable=False)

    message: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )