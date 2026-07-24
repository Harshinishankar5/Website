from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy import ForeignKey

class JobTitle(Base):
    __tablename__ = "job_titles"

    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String(255), nullable=False, index=True)

    applications = relationship(
        "JobApplication",
        back_populates="job",
        cascade="all, delete-orphan",
    )


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_titles.id"), nullable=False)


    candidate_name = Column(String(255), nullable=False)
    enter_email = Column(String(255), nullable=False, index=True)
    contact_number = Column(String(20), nullable=False)

    total_experience = Column(Float, nullable=False)
    relevant_experience = Column(Float, nullable=False)

    current_location = Column(String(255), nullable=False)

    current_ctc = Column(Float, nullable=False)
    expected_ctc = Column(Float, nullable=False)

    linkedin_profile_url = Column(String(500), nullable=True)
    technical_proficiency = Column(String(1000), nullable=True)

    upload_your_latest_resume = Column(String(500), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("JobTitle", back_populates="applications")