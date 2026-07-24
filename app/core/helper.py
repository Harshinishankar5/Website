import uuid
import boto3
import os
from dotenv import load_dotenv

from app.models.blogs_models import BlogPost, BlogContentSection
from fastapi import HTTPException
from sqlalchemy.orm import Session
from fastapi import UploadFile

load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)

AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

def get_s3_url(key: str) -> str:
    region = os.getenv("AWS_REGION")
    return f"https://{AWS_BUCKET_NAME}.s3.{region}.amazonaws.com/{key}"

def upload_to_s3(file: UploadFile, folder: str) -> str:
    extension = os.path.splitext(file.filename)[1]
    key = f"{folder}/{uuid.uuid4().hex}{extension}"
    print("AWS_BUCKET_NAME:", AWS_BUCKET_NAME)
    print("Type:", type(AWS_BUCKET_NAME))
    print("AWS_REGION:", os.getenv("AWS_REGION"))
    print("AWS_ACCESS_KEY_ID:", os.getenv("AWS_ACCESS_KEY_ID"))

    s3.upload_fileobj(
        file.file,
        AWS_BUCKET_NAME,
        key,
        ExtraArgs={
            "ContentType": file.content_type
        }
    )

    return key

def get_blog_or_404(db: Session, blog_id: int) -> BlogPost:
    blog = db.query(BlogPost).filter(BlogPost.id == blog_id).first()

    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found.")

    return blog


def get_content_section_or_404(db: Session, section_id: int) -> BlogContentSection:
    section = (
        db.query(BlogContentSection)
        .filter(BlogContentSection.id == section_id)
        .first()
    )

    if not section:
        raise HTTPException(status_code=404, detail="Content section not found.")

    return section




