from fastapi import APIRouter

from app.api.v1.match import router as match_router
from app.api.v1.optimize import router as optimize_router
from app.api.v1.interview import router as interview_router
from app.api.v1.history import router as history_router
from app.api.v1.search import router as search_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.upload import router as upload_router
from app.api.v1.resume import router as resume_router

api_router = APIRouter()
api_router.include_router(match_router, prefix="/match", tags=["Match"])
api_router.include_router(optimize_router, prefix="/optimize", tags=["Optimize"])
api_router.include_router(interview_router, prefix="/interview", tags=["Interview"])
api_router.include_router(history_router, prefix="/history", tags=["History"])
api_router.include_router(search_router, prefix="/search", tags=["Search"])
api_router.include_router(assistant_router, prefix="/assistant", tags=["Assistant"])
api_router.include_router(upload_router, prefix="/upload", tags=["Upload"])
api_router.include_router(resume_router, prefix="/resume", tags=["Resume"])