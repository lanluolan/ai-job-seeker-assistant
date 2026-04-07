from typing import Any, Dict, Optional, Tuple

from sqlalchemy.orm import Session

from app.services.resume_version_service import get_active_resume_version


def resolve_resume_context(
    db: Session,
    resume_text: str = "",
    structured_resume: Optional[Dict[str, Any]] = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    优先级：
    1. 接口显式传入的 structured_resume / resume_text
    2. 数据库里的当前激活简历版本
    3. 空
    """
    structured_resume = structured_resume or {}
    resume_text = resume_text or ""

    if structured_resume or resume_text.strip():
        return resume_text, structured_resume

    active = get_active_resume_version(db)
    if active:
        return active.get("raw_text", "") or "", active.get("structured_resume", {}) or {}

    return "", {}