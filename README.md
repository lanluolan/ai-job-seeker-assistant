AI 求职助手（基于大模型 + RAG）

简介
基于大模型（LLM）与 RAG 检索构建的智能求职助手，提供简历解析、岗位匹配、简历优化、面试生成、岗位推荐与结构化简历管理等功能，并支持报告导出。

技术栈
- Python
- FastAPI
- Streamlit
- OpenAI API（或其他 LLM 提供者）
- FAISS（向量检索）
- SQLite
- LangChain（可选）

核心功能
1. 简历解析：支持 PDF / DOCX / TXT 上传，使用 LLM 提取结构化信息（教育、技能、项目、经历等）。
2. 简历版本与管理：支持结构化简历体系、版本管理与多版本切换。
3. 岗位匹配与优化：基于 LLM 输出匹配度、缺失技能与优化建议。
4. RAG 检索：基于 FAISS 的岗位语义搜索与相似岗位推荐。
5. 求职分析报告：整合用户背景、简历与岗位信息，生成完整求职报告。
6. 报告导出：支持 Markdown / PDF 导出，便于分享与展示。
7. 前后端分离：使用 FastAPI 提供后端接口，Streamlit 提供前端展示与交互。

快速开始
1. 克隆仓库并进入项目目录

2. 创建与激活虚拟环境，安装依赖（示例）

```bash
python -m venv venv
# Windows
venv\\Scripts\\activate
pip install -r requirements.txt
```

3. 运行后端

```bash
uvicorn backend.app.main:app --reload
```

4. 运行前端

```bash
streamlit run frontend/app.py
```

许可证
此项目遵循 MIT 许可证（如适用，请根据需要添加或修改）。