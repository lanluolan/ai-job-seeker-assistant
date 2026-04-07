import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.models import AssistantAnalysis
from app.schemas.common import APIResponse
from app.services.assistant_service import analyze_career_profile, save_assistant_analysis
from app.services.pdf_service import build_pdf_report
from app.services.resume_context_service import resolve_resume_context

router = APIRouter()


class AssistantRequest(BaseModel):
    user_profile: str = Field(..., description="用户背景")
    resume_text: str = Field("", description="原始简历文本")
    structured_resume: Dict[str, Any] | None = Field(None, description="结构化简历")
    jd: str = Field(..., description="目标岗位JD")
    top_k: int = Field(5, ge=1, le=20)


class PdfFromResultRequest(BaseModel):
    report: Dict[str, Any] = Field(..., description="综合分析报告")
    retrieved_jobs: List[Dict[str, Any]] = Field(default_factory=list, description="检索结果")


@router.post("/analyze", response_model=APIResponse)
def analyze_assistant(data: AssistantRequest, db: Session = Depends(get_db)):
    resume_text, structured_resume = resolve_resume_context(
        db=db,
        resume_text=data.resume_text,
        structured_resume=data.structured_resume,
    )

    if not resume_text.strip() and not structured_resume:
        return APIResponse(success=False, message="没有可用的简历，请先上传并保存当前简历版本。", data=None)

    result = analyze_career_profile(
        user_profile=data.user_profile,
        resume_text=resume_text,
        jd=data.jd,
        top_k=data.top_k,
        structured_resume=structured_resume,
    )

    record = save_assistant_analysis(
        db=db,
        user_profile=data.user_profile,
        resume_text=resume_text,
        jd=data.jd,
        top_k=data.top_k,
        result=result,
        structured_resume=structured_resume,
    )

    return APIResponse(
        data={
            "analysis_id": record.id,
            **result,
        }
    )


@router.get("/report/pdf/{analysis_id}")
def generate_pdf_from_analysis_id(analysis_id: str, db: Session = Depends(get_db)):
    record = db.query(AssistantAnalysis).filter(AssistantAnalysis.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="analysis_id not found")

    report = json.loads(record.report_json or "{}")
    retrieved_jobs = json.loads(record.retrieved_jobs_json or "[]")

    tmp_dir = Path(tempfile.gettempdir())
    pdf_path = tmp_dir / f"ai_job_assistant_report_{analysis_id}.pdf"

    build_pdf_report(
        report=report if isinstance(report, dict) else {},
        retrieved_jobs=retrieved_jobs if isinstance(retrieved_jobs, list) else [],
        output_path=str(pdf_path),
    )

    return FileResponse(
        path=str(pdf_path),
        filename=f"ai_job_assistant_report_{analysis_id}.pdf",
        media_type="application/pdf",
    )


@router.get("/history", response_model=APIResponse)
def list_assistant_history(db: Session = Depends(get_db)):
    records = (
        db.query(AssistantAnalysis)
        .order_by(desc(AssistantAnalysis.created_at))
        .all()
    )

    data = [
        {
            "analysis_id": r.id,
            "user_profile": r.user_profile,
            "jd": r.jd,
            "top_k": r.top_k,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]

    return APIResponse(data=data)


@router.get("/analysis/{analysis_id}", response_model=APIResponse)
def get_assistant_analysis_detail(analysis_id: str, db: Session = Depends(get_db)):
    record = db.query(AssistantAnalysis).filter(AssistantAnalysis.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="analysis_id not found")

    data = {
        "analysis_id": record.id,
        "user_profile": record.user_profile,
        "resume": record.resume,
        "jd": record.jd,
        "top_k": record.top_k,
        "retrieved_jobs": json.loads(record.retrieved_jobs_json or "[]"),
        "report": json.loads(record.report_json or "{}"),
        "markdown_report": record.markdown_report or "",
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }

    return APIResponse(data=data)