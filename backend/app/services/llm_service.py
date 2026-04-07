import os
import json
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "mimo-v2-flash")

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL or None,
)

def call_llm(prompt: str, system: str = "你是一个专业的AI求职助手。") -> str:
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or ""

def safe_json_loads(text: str) -> Dict[str, Any]:
    """
    尝试把模型输出解析成 JSON。
    如果模型返回了多余文本，这里会尽量截取 JSON 部分。
    """
    text = text.strip()

    # 先直接解析
    try:
        return json.loads(text)
    except Exception:
        pass

    # 尝试截取第一个 { 到最后一个 }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        chunk = text[start : end + 1]
        try:
            return json.loads(chunk)
        except Exception:
            pass

    return {"raw_text": text}