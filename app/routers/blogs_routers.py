from typing import List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Form,
    UploadFile,
    File,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
import os
from app.models.blogs_models import (
    BlogContentSection,
    ImagePosition,
    BlogPost,
    BlogStatus,
    BlogHeroSection
)
from app.models.blogs_models import Blogs_Demo
from app.schemas.blogs_schemas import (
    DemoRequestCreate,
    DemoRequestResponse,
)
from app.core.dependencies import require_roles
from app.core.helper import upload_to_s3
from app.database import get_db
from app.models.users import UserRole

AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

router = APIRouter(
    prefix="/blogs",
    tags=["Blogs"]
)

@router.post(
    "/",
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))],
)
def create_blog(
    title: str = Form(...),
    slug: str = Form(...),
    category: List[str] = Form(...),   # Multiple categories
    author: str = Form(None),
    status: BlogStatus = Form(BlogStatus.ACTIVE),
    db: Session = Depends(get_db)
):

    existing = (
        db.query(BlogPost)
        .filter(BlogPost.slug == slug)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Slug already exists."
        )

    blog = BlogPost(
        title=title,
        slug=slug,
        category=category,
        author=author,
        status=status
    )

    try:
        db.add(blog)
        db.commit()
        db.refresh(blog)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Unable to create blog."
        )

    return {
        "success": True,
        "message": "Blog created successfully.",
        "data": blog
    }

@router.get(
    "/",
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))], )
def list_blogs(
    db: Session = Depends(get_db)
):

    blogs = (
        db.query(BlogPost)
        .order_by(BlogPost.created_at.desc())
        .all()
    )

    return {
        "success": True,
        "count": len(blogs),
        "data": blogs
    }

@router.get(
    "/{blog_id}",
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))], )
def get_blog(
    blog_id: int,
    db: Session = Depends(get_db)
):

    blog = (
        db.query(BlogPost)
        .filter(BlogPost.id == blog_id)
        .first()
    )

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found."
        )

    return {
        "success": True,
        "data": blog
    }

@router.patch(
    "/{blog_id}",
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))], )
def update_blog(
    blog_id: int,
    title: str = Form(None),
    slug: str = Form(None),
    category: List[str] = Form(...),   # Multiple categories
    author: str = Form(None),
    status: BlogStatus = Form(None),
    db: Session = Depends(get_db)
):

    blog = (
        db.query(BlogPost)
        .filter(BlogPost.id == blog_id)
        .first()
    )

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found."
        )

    if slug and slug != blog.slug:

        exists = (
            db.query(BlogPost)
            .filter(BlogPost.slug == slug)
            .first()
        )

        if exists:
            raise HTTPException(
                status_code=409,
                detail="Slug already exists."
            )

        blog.slug = slug

    if title is not None:
        blog.title = title

    if category is not None:
        blog.category = category

    if author is not None:
        blog.author = author


    if status is not None:
        blog.status = status

    db.commit()
    db.refresh(blog)

    return {
        "success": True,
        "message": "Blog updated successfully.",
        "data": blog
    }

@router.delete(
    "/{blog_id}",
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))], )
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db)
):

    blog = (
        db.query(BlogPost)
        .filter(BlogPost.id == blog_id)
        .first()
    )

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found."
        )

    db.delete(blog)
    db.commit()

    return {
        "success": True,
        "message": "Blog deleted successfully."
    }

########################HERO SECTION##################################
@router.post(
    "/{blog_id}/hero",
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))],
)
def create_hero_section(
    blog_id: int,

    hero_title: str = Form(None),
    short_description: str = Form(None),
    author_name: str = Form(None),

    hero_banner: UploadFile = File(None),
    author_image: UploadFile = File(None),

    db: Session = Depends(get_db),
):
    blog = db.query(BlogPost).filter(
        BlogPost.id == blog_id
    ).first()

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found."
        )

    existing = db.query(BlogHeroSection).filter(
        BlogHeroSection.blog_post_id == blog_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Hero section already exists."
        )

    hero = BlogHeroSection(
        blog_post_id=blog_id,
        hero_title=hero_title,
        short_description=short_description,
        author_name=author_name,
    )

    if hero_banner:
        key = upload_to_s3(
            hero_banner,
            f"blogs/{blog_id}/hero"
        )

        hero.hero_banner_key = key
        hero.hero_banner_url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{key}"

    if author_image:
        key = upload_to_s3(
            author_image,
            f"blogs/{blog_id}/hero"
        )

        hero.author_image_key = key
        hero.author_image_url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{key}"

    db.add(hero)
    db.commit()
    db.refresh(hero)

    return {
        "success": True,
        "message": "Hero section created successfully.",
        "data": hero
    }

@router.get("/{blog_id}/hero",
            dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))], )
def get_hero_section(
    blog_id: int,
    db: Session = Depends(get_db)
):
    hero = (
        db.query(BlogHeroSection)
        .filter(BlogHeroSection.blog_post_id == blog_id)
        .first()
    )

    if not hero:
        raise HTTPException(
            status_code=404,
            detail="Hero section not found"
        )

    return {
        "success": True,
        "data": hero
    }

@router.patch(
    "/{blog_id}/hero",
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))], )
def update_hero_section(

    blog_id: int,

    badge_text: str = Form(None),
    reading_time: str = Form(None),
    hero_title: str = Form(None),
    short_description: str = Form(None),
    author_name: str = Form(None),

    hero_banner: UploadFile = File(None),
    author_image: UploadFile = File(None),

    db: Session = Depends(get_db)
):

    hero = db.query(BlogHeroSection).filter(
        BlogHeroSection.blog_post_id == blog_id
    ).first()

    if not hero:
        raise HTTPException(
            status_code=404,
            detail="Hero section not found."
        )

    if badge_text is not None:
        hero.badge_text = badge_text

    if reading_time is not None:
        hero.reading_time = reading_time

    if hero_title is not None:
        hero.hero_title = hero_title

    if short_description is not None:
        hero.short_description = short_description

    if author_name is not None:
        hero.author_name = author_name

    if hero_banner:

        key = upload_to_s3(
            hero_banner,
            f"blogs/{blog_id}/hero"
        )

        hero.hero_banner_key = key
        hero.hero_banner_url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{key}"

    if author_image:

        key = upload_to_s3(
            author_image,
            f"blogs/{blog_id}/hero"
        )

        hero.author_image_key = key
        hero.author_image_url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{key}"

    db.commit()
    db.refresh(hero)

    return {
        "success": True,
        "message": "Hero section updated successfully.",
        "data": hero
    }

@router.delete(
    "/{blog_id}/hero",
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))], )
def delete_hero_section(
    blog_id: int,
    db: Session = Depends(get_db)
):

    hero = db.query(BlogHeroSection).filter(
        BlogHeroSection.blog_post_id == blog_id
    ).first()

    if not hero:
        raise HTTPException(
            status_code=404,
            detail="Hero section not found."
        )

    db.delete(hero)
    db.commit()

    return {
        "success": True,
        "message": "Hero section deleted successfully."
    }

##############content section###################
@router.post(
    "/{blog_id}/sections",
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))], )
def create_content_section(
    blog_id: int,

    order_index: int = Form(...),
    section_title: str = Form(...),

    image_alt_text: str = Form(None),
    description: str = Form(...),
    image_caption: str = Form(None),
    image_position: ImagePosition = Form(ImagePosition.FULL_WIDTH),

    section_image: UploadFile = File(None),

    db: Session = Depends(get_db)
):

    blog = db.query(BlogPost).filter(
        BlogPost.id == blog_id
    ).first()

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found."
        )

    section = BlogContentSection(
        blog_post_id=blog_id,
        order_index=order_index,
        section_title=section_title,
        description=description,
        image_alt_text=image_alt_text,
        image_caption=image_caption,
        image_position=image_position
    )

    if section_image:

        key = upload_to_s3(
            section_image,
            f"blogs/{blog_id}/sections"
        )

        section.section_image_key = key
        section.section_image_url = (
            f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{key}"
        )

    db.add(section)
    db.commit()
    db.refresh(section)

    return {
        "success": True,
        "message": "Content section created successfully.",
        "data": section
    }

@router.get(
    "/sections/{section_id}",
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))], )
def get_content_section(
    section_id: int,
    db: Session = Depends(get_db)
):

    section = db.query(BlogContentSection).filter(
        BlogContentSection.id == section_id
    ).first()

    if not section:
        raise HTTPException(
            status_code=404,
            detail="Section not found."
        )

    return {
        "success": True,
        "data": section
    }

@router.patch(
    "/sections/{section_id}",
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))], )
def update_content_section(

    section_id: int,

    order_index: int = Form(None),
    section_title: str = Form(None),
    description: str = Form(None),

    image_alt_text: str = Form(None),
    image_caption: str = Form(None),
    image_position: ImagePosition = Form(None),

    section_image: UploadFile = File(None),

    db: Session = Depends(get_db)
):

    section = db.query(BlogContentSection).filter(
        BlogContentSection.id == section_id
    ).first()

    if not section:
        raise HTTPException(
            status_code=404,
            detail="Section not found."
        )

    if order_index is not None:
        section.order_index = order_index

    if section_title is not None:
        section.section_title = section_title

    if image_alt_text is not None:
        section.image_alt_text = image_alt_text

    if description is not None:
        section.description = description

    if image_caption is not None:
        section.image_caption = image_caption

    if image_position is not None:
        section.image_position = image_position

    if section_image:

        key = upload_to_s3(
            section_image,
            f"blogs/{section.blog_post_id}/sections"
        )

        section.section_image_key = key
        section.section_image_url = (
            f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{key}"
        )

    db.commit()
    db.refresh(section)

    return {
        "success": True,
        "message": "Content section updated successfully.",
        "data": section
    }

@router.delete(
    "/sections/{section_id}",
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))], )
def delete_content_section(
    section_id: int,
    db: Session = Depends(get_db)
):

    section = db.query(BlogContentSection).filter(
        BlogContentSection.id == section_id
    ).first()

    if not section:
        raise HTTPException(
            status_code=404,
            detail="Section not found."
        )

    db.delete(section)
    db.commit()

    return {
        "success": True,
        "message": "Content section deleted successfully."
    }

@router.delete(
    "/{blog_id}/{all}",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(require_roles(["SUPER_ADMIN", "ADMIN"]))
    ],
)
def delete_entire_blog(
    blog_id: int,
    db: Session = Depends(get_db),
):
    blog = db.query(BlogPost).filter(BlogPost.id == blog_id).first()

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found"
        )

    db.delete(blog)
    db.commit()

    return {
        "message": "Blog and all related records deleted successfully."
    }

@router.get(
    "/{blog_id}/all",
    status_code=status.HTTP_200_OK,
)
def get_blog(
    blog_id: int,
    db: Session = Depends(get_db),
):
    blog = (
        db.query(BlogPost)
        .options(
            joinedload(BlogPost.hero_section),
            joinedload(BlogPost.content_sections),
        )
        .filter(BlogPost.id == blog_id)
        .first()
    )

    if not blog:
        raise HTTPException(
            status_code=404,
            detail="Blog not found"
        )

    return blog


