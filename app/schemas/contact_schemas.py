from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

from enum import Enum

class PurposeEnum(str, Enum):
    BUSINESS_ENQUIRY = "Business Enquiry"
    PARTNERSHIP = "Partnership"
    SUPPORT = "Support"
    CAREERS = "Careers"
    OTHER = "Other"

class ContactUsCreate(BaseModel):
    name: str
    email: EmailStr
    purpose: PurposeEnum
    country_code: str
    phone_number: str
    location: str
    message: str


class ContactUsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    purpose: PurposeEnum
    phone_number: str
    location: str
    message: str
    created_at: datetime