import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.schemas.common import APIResponse
from app.services.resume_parse_service import parse_resume_structured
from app.services.resume_version_service import (
    save_resume_version,
    list_resume_versions,
    get_active_resume_version,
    set_active_resume_version,
    clear_active_resume_version,
)


router = APIRouter()


class ResumeParseRequest(BaseModel):
    resume_text: str = Field(..., description="简历原文")


class SaveResumeVersionRequest(BaseModel):
    resume_text: str = Field("", description="原始简历文本")
    structured_resume: dict = Field(..., description="结构化简历")
    resume_name: str = Field("", description="简历名称")


@router.post("/structure", response_model=APIResponse)
def structure_resume(data: ResumeParseRequest):
    result = parse_resume_structured(data.resume_text)
    return APIResponse(data=result)


@router.post("/version/save", response_model=APIResponse)
def save_version(data: SaveResumeVersionRequest, db: Session = Depends(get_db)):
    version = save_resume_version(
        db=db,
        structured_resume=data.structured_resume,
        raw_text=data.resume_text,
        resume_name=data.resume_name,
    )
    return APIResponse(
        data={
            "id": version.id,
            "version_no": version.version_no,
            "is_active": bool(version.is_active),
            "created_at": version.created_at.isoformat() if version.created_at else None,
        }
    )


@router.get("/version/list", response_model=APIResponse)
def version_list(db: Session = Depends(get_db)):
    return APIResponse(data=list_resume_versions(db))


@router.get("/version/active", response_model=APIResponse)
def active_version(db: Session = Depends(get_db)):
    active = get_active_resume_version(db)
    return APIResponse(data=active)


@router.post("/version/activate/{version_id}", response_model=APIResponse)
def activate_version(version_id: str, db: Session = Depends(get_db)):
    try:
        version = set_active_resume_version(db, version_id)
        return APIResponse(
            data={
                "id": version.id,
                "version_no": version.version_no,
                "is_active": bool(version.is_active),
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.post("/version/clear-active", response_model=APIResponse)
def clear_active_version(db: Session = Depends(get_db)):
    clear_active_resume_version(db)
    return APIResponse(data={"success": True})