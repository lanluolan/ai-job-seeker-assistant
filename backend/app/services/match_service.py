import json
from typing import Any, Dict

from app.services.llm_service import call_llm, safe_json_loads


def build_structured_resume_text(structured_resume: Dict[str, Any]) -> str:
    if not structured_resume:
        return ""

    parts = []

    name = structured_resume.get("name")
    if name:
        parts.append(f"姓名: {name}")

    email = structured_resume.get("email")
    if email:
        parts.append(f"邮箱: {email}")

    phone = structured_resume.get("phone")
    if phone:
        parts.append(f"电话: {phone}")

    education = structured_resume.get("education", []) or []
    if education:
        parts.append("教育经历:")
        for edu in education:
            school = edu.get("school", "")
            degree = edu.get("degree", "")
            major = edu.get("major", "")
            start_date = edu.get("start_date", "")
            end_date = edu.get("end_date", "")
            parts.append(f"- {school} | {major} | {degree} | {start_date} ~ {end_date}")

    skills = structured_resume.get("skills", []) or []
    if skills:
        parts.append("技能栈:")
        parts.append(", ".join(skills))

    projects = structured_resume.get("projects", []) or []
    if projects:
        parts.append("项目经历:")
        for proj in projects:
            name = proj.get("name", "")
            role = proj.get("role", "")
            desc = proj.get("description", "")
            tech_stack = proj.get("tech_stack", []) or []
            parts.append(f"- 项目名: {name}")
            if role:
                parts.append(f"  角色: {role}")
            if desc:
                parts.append(f"  描述: {desc}")
            if tech_stack:
                parts.append(f"  技术栈: {', '.join(tech_stack)}")

    experiences = structured_resume.get("experiences", []) or []
    if experiences:
        parts.append("工作/实习经历:")
        for exp in experiences:
            company = exp.get("company", "")
            title = exp.get("title", "")
            desc = exp.get("description", "")
            start_date = exp.get("start_date", "")
            end_date = exp.get("end_date", "")
            parts.append(f"- {company} | {title} | {start_date} ~ {end_date}")
            if desc:
                parts.append(f"  描述: {desc}")

    summary = structured_resume.get("summary")
    if summary:
        parts.append(f"自我评价: {summary}")

    return "\n".join(parts)


def analyze_match(jd: str, resume_text: str = "", structured_resume: Dict[str, Any] | None = None) -> Dict[str, Any]:
    structured_resume = structured_resume or {}
    structured_text = build_structured_resume_text(structured_resume)

    resume_block = structured_text if structured_text.strip() else resume_text

    prompt = f"""
你是一个资深AI招聘分析师，请分析以下岗位JD和候选人简历的匹配情况。

要求：
1. 不要编造简历中不存在的信息
2. 输出必须是JSON格式，不要输出多余解释
3. 匹配度使用0到100的整数
4. 匹配点、缺失点、建议都要尽量具体
5. 如果简历信息较少，请保守判断

JSON格式如下：
{{
  "score": 85,
  "matched_skills": ["Python", "FastAPI"],
  "missing_skills": ["RAG", "向量数据库"],
  "analysis": "整体评价说明",
  "suggestions": ["建议1", "建议2"]
}}

岗位JD：
{jd}

候选人简历：
{resume_block}
"""

    result = call_llm(prompt)
    return safe_json_loads(result)