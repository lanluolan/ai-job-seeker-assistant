from typing import Any, Dict

from app.services.llm_service import call_llm, safe_json_loads


def parse_resume_structured(resume_text: str) -> Dict[str, Any]:
    prompt = f"""
你是一个简历信息抽取助手。请把下面的简历文本抽取成严格 JSON。

要求：
1. 不要编造任何不存在的信息
2. 只输出 JSON，不要输出额外解释
3. 字段尽量完整
4. 如果没有某字段，填空字符串或空数组
5. 技能只保留关键词，不要长句

JSON 格式如下：
{{
  "name": "",
  "email": "",
  "phone": "",
  "education": [
    {{
      "school": "",
      "degree": "",
      "major": "",
      "start_date": "",
      "end_date": ""
    }}
  ],
  "skills": ["Python", "FastAPI"],
  "projects": [
    {{
      "name": "",
      "role": "",
      "description": "",
      "tech_stack": ["Python", "RAG"]
    }}
  ],
  "experiences": [
    {{
      "company": "",
      "title": "",
      "start_date": "",
      "end_date": "",
      "description": ""
    }}
  ],
  "summary": ""
}}

简历文本：
{resume_text}
"""

    result = call_llm(
        prompt,
        system="你是一个严谨的简历结构化抽取助手，只输出 JSON。"
    )
    parsed = safe_json_loads(result)

    if not isinstance(parsed, dict):
        return {
            "name": "",
            "email": "",
            "phone": "",
            "education": [],
            "skills": [],
            "projects": [],
            "experiences": [],
            "summary": "",
            "raw_text": resume_text,
        }

    return parsed