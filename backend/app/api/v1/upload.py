from pathlib import Path
import tempfile

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.schemas.common import APIResponse
from app.utils.resume_parser import parse_resume_file

router = APIRouter()


@router.post("/resume", response_model=APIResponse)
async def upload_resume(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in [".txt", ".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="只支持 txt / pdf / docx 文件")

    tmp_dir = Path(tempfile.gettempdir())
    tmp_path = tmp_dir / file.filename

    content = await file.read()
    tmp_path.write_bytes(content)

    try:
        text = parse_resume_file(str(tmp_path))
        return APIResponse(
            data={
                "filename": file.filename,
                "text": text,
            }
        )
    finally:
        if tmp_path.exists():
            tmp_path.unlink()