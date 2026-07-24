from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class ServiceType(str, Enum):
    customer_support = "customer support"
    Back_office_operations = "back-office operations"
    sales_and_telemarketing = "sales and telemarketing"
    Hr_and_Recruitment = "hr and recruitment"
    Document_automation = "document automation"
    Other = "other"


class BookAppointmentCreate(BaseModel):
    name: str
    email: EmailStr
    country_code: str
    phone_number: str
    service_type: str
    message: Optional[str] = None


class BookAppointmentResponse(BaseModel):
    id: int
    message: str

    class Config:
        from_attributes = True