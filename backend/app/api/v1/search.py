from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.schemas.common import APIResponse
from app.services.rag_service import recommend_jobs, search_jobs

router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(..., description="检索查询")
    top_k: int = Field(5, ge=1, le=20)


class RecommendRequest(BaseModel):
    user_profile: str = Field(..., description="用户背景")
    top_k: int = Field(5, ge=1, le=20)


@router.post("/jobs", response_model=APIResponse)
def search_similar_jobs(data: SearchRequest):
    results = search_jobs(data.query, top_k=data.top_k)
    return APIResponse(data=results)


@router.post("/recommend", response_model=APIResponse)
def recommend_similar_jobs(data: RecommendRequest):
    results = recommend_jobs(data.user_profile, top_k=data.top_k)
    return APIResponse(data=results)