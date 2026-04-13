import os
import json
from typing import Any, Dict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "mimo-v2-flash")

llm = ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=0.3,
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL or None,
)

def call_llm(prompt: str, system: str = "你是一个专业的AI求职助手。") -> str:
    msg = llm.invoke([
        SystemMessage(content=system),
        HumanMessage(content=prompt),
    ])
    return msg.content if isinstance(msg.content, str) else str(msg.content)

def safe_json_loads(text: str) -> Dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        chunk = text[start:end + 1]
        try:
            return json.loads(chunk)
        except Exception:
            pass
    return {"raw_text": text}