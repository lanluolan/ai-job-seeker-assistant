import json
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.db.models import ResumeVersion


def get_next_version_no(db: Session) -> int:
    latest = (
        db.query(ResumeVersion)
        .order_by(ResumeVersion.version_no.desc())
        .first()
    )
    return (latest.version_no + 1) if latest else 1


def save_resume_version(
    db: Session,
    structured_resume: Dict[str, Any],
    raw_text: str = "",
    resume_name: str = "",
) -> ResumeVersion:
    # 先把旧版本全部置为非当前
    db.query(ResumeVersion).update({ResumeVersion.is_active: 0})

    version = ResumeVersion(
        version_no=get_next_version_no(db),
        resume_name=resume_name,
        structured_json=json.dumps(structured_resume, ensure_ascii=False),
        raw_text=raw_text,
        is_active=1,
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


def list_resume_versions(db: Session) -> List[Dict[str, Any]]:
    records = (
        db.query(ResumeVersion)
        .order_by(ResumeVersion.version_no.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "version_no": r.version_no,
            "resume_name": r.resume_name,
            "is_active": bool(r.is_active),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]


def get_active_resume_version(db: Session) -> Optional[Dict[str, Any]]:
    record = db.query(ResumeVersion).filter(ResumeVersion.is_active == 1).first()
    if not record:
        return None

    return {
        "id": record.id,
        "version_no": record.version_no,
        "resume_name": record.resume_name,
        "structured_resume": json.loads(record.structured_json or "{}"),
        "raw_text": record.raw_text or "",
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


def set_active_resume_version(db: Session, version_id: str) -> ResumeVersion:
    target = db.query(ResumeVersion).filter(ResumeVersion.id == version_id).first()
    if not target:
        raise ValueError("version not found")

    db.query(ResumeVersion).update({ResumeVersion.is_active: 0})
    target.is_active = 1
    db.commit()
    db.refresh(target)
    return target

def clear_active_resume_version(db: Session) -> None:
    db.query(ResumeVersion).update({ResumeVersion.is_active: 0})
    db.commit()