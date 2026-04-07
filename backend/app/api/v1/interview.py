import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.models import AnalysisRecord
from app.schemas.common import APIResponse
from app.services.interview_service import generate_interview_questions
from app.services.resume_context_service import resolve_resume_context

router = APIRouter()


class InterviewRequest(BaseModel):
    jd: str = Field(..., description="岗位JD")
    resume_text: str = Field("", description="原始简历文本")
    structured_resume: dict | None = Field(None, description="结构化简历")


@router.post("/interview", response_model=APIResponse)
def generate_interview_questions_api(data: InterviewRequest, db: Session = Depends(get_db)):
    resume_text, structured_resume = resolve_resume_context(
        db=db,
        resume_text=data.resume_text,
        structured_resume=data.structured_resume,
    )

    if not resume_text.strip() and not structured_resume:
        return APIResponse(success=False, message="没有可用的简历，请先上传并保存当前简历版本。", data=None)

    result_data = generate_interview_questions(
        jd=data.jd,
        resume_text=resume_text,
        structured_resume=structured_resume,
    )

    record = AnalysisRecord(
        record_type="interview",
        jd=data.jd,
        resume=resume_text or json.dumps(structured_resume or {}, ensure_ascii=False),
        result_json=json.dumps(result_data, ensure_ascii=False),
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return APIResponse(
        data={
            "id": record.id,
            "result": result_data,
        }
    )