from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from app.db.session import Base


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(Integer, primary_key=True, index=True)
    record_type = Column(String(50), index=True)  # match / optimize / interview
    jd = Column(Text, nullable=False)
    resume = Column(Text, nullable=True)
    result_json = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AssistantAnalysis(Base):
    __tablename__ = "assistant_analyses"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_profile = Column(Text, nullable=False)
    resume = Column(Text, nullable=False)
    jd = Column(Text, nullable=False)
    top_k = Column(Integer, default=5)
    retrieved_jobs_json = Column(Text, nullable=False)
    report_json = Column(Text, nullable=False)
    markdown_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    version_no = Column(Integer, nullable=False)
    resume_name = Column(String(255), nullable=True)
    structured_json = Column(Text, nullable=False)
    raw_text = Column(Text, nullable=True)
    is_active = Column(Integer, default=1)  # 1=当前版本，0=历史版本
    created_at = Column(DateTime(timezone=True), server_default=func.now())