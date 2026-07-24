import enum
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import JSON

from sqlalchemy import String, Text, Integer, Date, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, String, Integer, ForeignKey

from app.database import Base

class BlogStatus(str, enum.Enum):
    ACTIVE = "active"
    IN_ACTIVE = "in_active"


class ImagePosition(str, enum.Enum):
    LEFT = "left"
    RIGHT = "right"
    FULL_WIDTH = "full_width"


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    category: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    author: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    status: Mapped[BlogStatus] = mapped_column(SqlEnum(BlogStatus), default=BlogStatus.ACTIVE, nullable=False)
    # views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    hero_section: Mapped[Optional["BlogHeroSection"]] = relationship(
        back_populates="blog_post", uselist=False, cascade="all, delete-orphan"
    )
    content_sections: Mapped[List["BlogContentSection"]] = relationship(
        back_populates="blog_post", cascade="all, delete-orphan", order_by="BlogContentSection.order_index"
    )


class BlogHeroSection(Base):
    __tablename__ = "blog_hero_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blog_post_id: Mapped[int] = mapped_column(
        ForeignKey("blog_posts.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # badge_text: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # reading_time: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    hero_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    short_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hero_banner_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)   # S3 object key
    hero_banner_url = Column(String, nullable=True)  # new
    author_image_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # S3 object key
    author_image_url = Column(String, nullable=True)  # new
    author_name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    blog_post: Mapped["BlogPost"] = relationship(back_populates="hero_section")


class BlogContentSection(Base):
    __tablename__ = "blog_content_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    blog_post_id: Mapped[int] = mapped_column(
        ForeignKey("blog_posts.id", ondelete="CASCADE"),
        nullable=False,
    )

    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    section_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Rich text / HTML from editor
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    section_image_key: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    section_image_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    image_alt_text: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    image_caption: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    image_position: Mapped[ImagePosition] = mapped_column(
        SqlEnum(ImagePosition),
        default=ImagePosition.FULL_WIDTH,
        nullable=False,
    )

    blog_post: Mapped["BlogPost"] = relationship(
        back_populates="content_sections"
    )

class Blogs_Demo(Base):
    __tablename__ = "blogs_demo"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)

    company_name: Mapped[str] = mapped_column(String(200), nullable=False)

    work_email: Mapped[str] = mapped_column(String(255), nullable=False)

    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)

    business_need: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )