from typing import Any, Dict

from app.services.llm_service import call_llm, safe_json_loads
from app.services.match_service import build_structured_resume_text


def optimize_resume(
    jd: str,
    resume_text: str = "",
    structured_resume: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    structured_resume = structured_resume or {}
    structured_text = build_structured_resume_text(structured_resume)

    resume_block = structured_text if structured_text.strip() else resume_text

    prompt = f"""
请根据以下岗位JD，对候选人简历进行优化。

要求：
1. 不要编造不存在的经历
2. 优先保留真实信息
3. 尽量让简历更贴合JD
4. 如果信息不足，给出补充建议
5. 输出必须是JSON，不要输出多余解释

JSON格式如下：
{{
  "optimized_resume": "优化后的简历内容",
  "change_log": [
    "修改点1",
    "修改点2"
  ],
  "suggestions": [
    "建议1",
    "建议2"
  ],
  "missing_info": [
    "需要补充的信息1",
    "需要补充的信息2"
  ]
}}

岗位JD：
{jd}

候选人简历：
{resume_block}
"""

    result = call_llm(prompt)
    return safe_json_loads(result)