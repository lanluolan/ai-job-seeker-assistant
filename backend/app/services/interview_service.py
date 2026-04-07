from typing import Any, Dict

from app.services.llm_service import call_llm, safe_json_loads
from app.services.match_service import build_structured_resume_text


def generate_interview_questions(
    jd: str,
    resume_text: str = "",
    structured_resume: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    structured_resume = structured_resume or {}
    structured_text = build_structured_resume_text(structured_resume)

    resume_block = structured_text if structured_text.strip() else resume_text

    prompt = f"""
你是一个资深面试官，请根据以下岗位JD和候选人简历生成模拟面试题。

要求：
1. 覆盖技术题、项目题、行为题
2. 尽量贴合候选人的真实经历
3. 给出参考答案要点
4. 输出必须是JSON，不要输出多余解释

JSON格式如下：
{{
  "questions": [
    {{
      "type": "technical",
      "question": "问题内容",
      "answer_points": ["答案要点1", "答案要点2"]
    }},
    {{
      "type": "project",
      "question": "问题内容",
      "answer_points": ["答案要点1", "答案要点2"]
    }},
    {{
      "type": "behavioral",
      "question": "问题内容",
      "answer_points": ["答案要点1", "答案要点2"]
    }}
  ]
}}

岗位JD：
{jd}

候选人简历：
{resume_block}
"""

    result = call_llm(prompt)
    return safe_json_loads(result)