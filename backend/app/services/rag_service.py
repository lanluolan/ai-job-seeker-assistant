import os
from functools import lru_cache
from typing import Any, Dict, List

from dotenv import load_dotenv

from app.rag.retriever import JobRetriever
from app.rag.vector_store import FaissVectorStore
from app.services.llm_service import call_llm

load_dotenv()

INDEX_PATH = os.getenv("RAG_INDEX_PATH", "data/vector_index/jobs.faiss")
METADATA_PATH = os.getenv("RAG_METADATA_PATH", "data/vector_index/jobs_meta.json")

@lru_cache(maxsize=1)
def get_retriever() -> JobRetriever:
    store = FaissVectorStore(index_path=INDEX_PATH, metadata_path=METADATA_PATH)
    store.load()
    return JobRetriever(store)


def search_jobs(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    retriever = get_retriever()
    return retriever.search(query=query, top_k=top_k)


def recommend_jobs(user_profile: str, top_k: int = 5) -> Dict[str, Any]:
    retrieved = search_jobs(user_profile, top_k=top_k)

    context = "\n\n".join(
        [
            f"岗位{i+1}:{item['title']} / {item['company']}\n"
            f"岗位描述：{item['jd_text']}\n"
            f"相似度：{item['score']}"
            for i, item in enumerate(retrieved)
        ]
    )

    prompt = f"""
        你是一个资深AI求职顾问。请根据用户背景和候选岗位，输出推荐结果。

        要求：
            1. 结合用户背景判断匹配原因
            2. 输出必须是JSON格式
            3. 不要编造不存在的信息
            4. 推荐理由要具体

        JSON格式:
        {{
            "summary": "整体结论",
            "recommendations": [
                {{
                    "title": "岗位名称",
                    "company": "公司名",
                    "match_reason": "为什么匹配",
                    "gap": ["缺口1", "缺口2"],
                    "suggestion": "如何补足"
                }}
            ]
        }}

        用户背景：
        {user_profile}

        候选岗位：
        {context}
    """

    text = call_llm(prompt, system="你是一个专业、务实、能给出可执行建议的AI求职顾问。")

    return {
        "retrieved_jobs": retrieved,
        "recommendation_text": text,
    }