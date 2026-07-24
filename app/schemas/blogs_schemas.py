from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator, EmailStr

from app.models.blogs_models import BlogStatus, ImagePosition


# ---------------------------------------------------------------------------
# Description Block  ("Add Description Block")
# ---------------------------------------------------------------------------
class DescriptionBlockIn(BaseModel):
    content: str
    order_index: int = 0


class DescriptionBlockOut(DescriptionBlockIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------------------------------------------------------------------------
# Content Section  ("Content Builder" -> Introduction, etc.)
# ---------------------------------------------------------------------------
class ContentSectionIn(BaseModel):
    section_title: str
    order_index: int = 0
    image_alt_text: Optional[str] = None
    image_caption: Optional[str] = None
    image_position: ImagePosition = ImagePosition.FULL_WIDTH
    description_blocks: List[DescriptionBlockIn] = []
    # section_image_key is NOT part of this payload - it's set via the
    # dedicated image upload endpoint once the section already exists.


class ContentSectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_index: int
    section_title: str
    section_image_key: Optional[str] = None
    image_alt_text: Optional[str] = None
    image_caption: Optional[str] = None
    image_position: ImagePosition
    description_blocks: List[DescriptionBlockOut] = []


# ---------------------------------------------------------------------------
# Hero Section
# ---------------------------------------------------------------------------
class HeroSectionIn(BaseModel):
    badge_text: Optional[str] = None
    reading_time: Optional[str] = None
    hero_title: Optional[str] = None
    short_description: Optional[str] = None
    author_name: Optional[str] = None


class HeroSectionOut(BaseModel):
    badge_text: Optional[str]
    reading_time: Optional[str]
    hero_title: Optional[str]
    short_description: Optional[str]
    author_name: Optional[str]


# ---------------------------------------------------------------------------
# Blog Information
# ---------------------------------------------------------------------------
class BlogInformationIn(BaseModel):
    title: str
    slug: str
    categories: List[str]
    author: Optional[str] = None

    @field_validator("slug")
    @classmethod
    def slug_must_be_url_safe(cls, v: str) -> str:
        if " " in v:
            raise ValueError("slug cannot contain spaces")
        return v.lower()


# ---------------------------------------------------------------------------
class BlogPublishRequest(BaseModel):
    blog_information: BlogInformationIn
    hero_section: HeroSectionIn
    content_sections: List[ContentSectionIn]


class BlogPostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    category: Optional[str] = None
    author: Optional[str] = None
    status: BlogStatus
    created_at: datetime
    updated_at: datetime
    hero_section: Optional[HeroSectionOut] = None
    content_sections: List[ContentSectionOut] = []

class DemoRequestCreate(BaseModel):
    full_name: str
    company_name: str
    work_email: EmailStr
    country_code: str
    phone_number: str
    business_need: str


class DemoRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    company_name: str
    work_email: EmailStr
    phone_number: str
    business_need: str
    created_at: datetime