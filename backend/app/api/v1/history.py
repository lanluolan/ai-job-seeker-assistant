import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.deps import get_db
from app.db.models import AnalysisRecord
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/history", response_model=APIResponse)
def get_history(db: Session = Depends(get_db)):
    records = (
        db.query(AnalysisRecord)
        .order_by(desc(AnalysisRecord.created_at))
        .all()
    )

    data = [
        {
            "id": r.id,
            "record_type": r.record_type,
            "jd": r.jd,
            "resume": r.resume,
            "result": json.loads(r.result_json),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]

    return APIResponse(data=data)