import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.orm import Session

from app.db.models import AssistantAnalysis
from app.services.match_service import build_structured_resume_text
from app.services.rag_service import search_jobs
from app.services.llm_service import safe_json_loads
from app.services.report_service import build_markdown_report

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
ASSISTANT_MODEL = os.getenv("OPENAI_MODEL", "mimo-v2-flash")

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL or None,
)

def analyze_career_profile(
    user_profile: str,
    resume_text: str,
    jd: str,
    top_k: int = 5,
    structured_resume: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    structured_resume = structured_resume or {}
    structured_text = build_structured_resume_text(structured_resume)
    resume_block = structured_text if structured_text.strip() else resume_text

    retrieved_jobs = search_jobs(user_profile, top_k=top_k)

    job_context = "\n\n".join(
        [
            f"岗位{i+1}：{item['title']} / {item['company']}\n"
            f"岗位描述：{item['jd_text']}\n"
            f"相似度：{item['score']}"
            for i, item in enumerate(retrieved_jobs)
        ]
    )

    prompt = f"""
你是一个专业的AI求职助手，请根据用户背景、简历、目标岗位JD和候选岗位，输出一份完整的求职分析报告。

要求：
1. 不要编造不存在的信息
2. 输出必须是JSON格式
3. 语言要清晰、具体、可执行
4. 既要分析目标岗位匹配度，也要给出岗位推荐建议
5. 如果简历信息比较少，请保守判断

JSON格式如下：
{{
  "summary": "整体结论",
  "match_analysis": {{
    "score": 85,
    "matched_skills": ["Python", "FastAPI"],
    "missing_skills": ["RAG", "向量数据库"],
    "analysis": "匹配分析说明",
    "suggestions": ["建议1", "建议2"]
  }},
  "job_recommendations": [
    {{
      "title": "岗位名称",
      "company": "公司名",
      "match_reason": "为什么推荐",
      "gap": ["缺口1", "缺口2"],
      "suggestion": "补足建议"
    }}
  ],
  "action_plan": [
    "第一步怎么做",
    "第二步怎么做",
    "第三步怎么做"
  ]
}}

用户背景：
{user_profile}

目标岗位JD：
{jd}

候选人简历：
{resume_block}

检索到的相似岗位：
{job_context}
"""

    resp = client.chat.completions.create(
        model=ASSISTANT_MODEL,
        messages=[
            {"role": "system", "content": "你是一个专业、务实、能给出可执行建议的AI求职顾问。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    text = resp.choices[0].message.content or ""
    parsed = safe_json_loads(text)

    markdown_report = build_markdown_report(
        parsed if isinstance(parsed, dict) else {},
        retrieved_jobs,
    )

    return {
        "retrieved_jobs": retrieved_jobs,
        "report": parsed,
        "markdown_report": markdown_report,
    }


def save_assistant_analysis(
    db: Session,
    user_profile: str,
    resume_text: str,
    jd: str,
    top_k: int,
    result: Dict[str, Any],
    structured_resume: Dict[str, Any] | None = None,
) -> AssistantAnalysis:
    record = AssistantAnalysis(
        user_profile=user_profile,
        resume=resume_text or json.dumps(structured_resume or {}, ensure_ascii=False),
        jd=jd,
        top_k=top_k,
        retrieved_jobs_json=json.dumps(result.get("retrieved_jobs", []), ensure_ascii=False),
        report_json=json.dumps(result.get("report", {}), ensure_ascii=False),
        markdown_report=result.get("markdown_report", ""),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record