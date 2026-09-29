# AI 求职助手

基于大模型与 RAG 的求职工作台，前端使用 **React + Vite**，后端使用 **FastAPI**，数据存储使用 SQLite，岗位检索使用 FAISS。

支持简历上传（PDF / DOCX / TXT）、结构化简历编辑、简历版本管理、岗位匹配、简历优化、模拟面试、综合分析、历史记录，以及 Markdown / PDF 报告导出。

## 启动后端

在项目根目录创建 Python 虚拟环境并安装依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

在 `backend/.env` 中配置模型服务（如已有配置，继续沿用）：

```dotenv
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://your-provider.example/v1
OPENAI_MODEL=your-model-name
EMBEDDING_API_KEY=EMPTY
EMBEDDING_BASE_URL=http://127.0.0.1:8080/v1
EMBEDDING_MODEL=text-embeddings-inference
```

`OPENAI_BASE_URL` 可省略以使用客户端默认地址。综合分析需要可用的 Embedding 服务，默认使用 Qwen3 Embedding。GPU 环境可使用 [Text Embeddings Inference](https://github.com/huggingface/text-embeddings-inference) 启动服务：

```powershell
docker run --gpus all -p 8080:80 ghcr.io/huggingface/text-embeddings-inference:cuda-1.9 --model-id Qwen/Qwen3-Embedding-0.6B
```

Embedding 服务的模型需与 `backend/data/vector_index` 的向量索引一致。更换 Embedding 模型后，在 `backend` 目录执行 `python scripts/ingest_jobs.py` 重建索引。

```powershell
cd backend
uvicorn app.main:app --reload
```

接口文档：<http://127.0.0.1:8000/docs>。

## 启动 React 前端

安装 Node.js 22.12 或更高版本，另开终端，在项目根目录执行：

```powershell
cd frontend
npm install
npm run dev
```

打开 <http://127.0.0.1:5173>。前端通过 Vite 把 `/api` 请求代理到 `http://127.0.0.1:8000`，无需单独配置开发环境 CORS。

如果后端地址不同，将 `frontend/.env.example` 复制为 `frontend/.env.local`，修改 `API_PROXY_TARGET` 后重启前端。模型密钥仅保存在后端，不要放入前端环境变量。

## 使用 Docker Compose

也可以用 Docker 提供 Python 和 Node.js 运行环境，不必在电脑上安装它们。安装并启动 Docker Desktop 后，在项目根目录复制后端配置模板：

```powershell
Copy-Item backend/.env.example backend/.env
```

编辑 `backend/.env`，填入大模型服务商提供的密钥、API 地址和模型名，然后在项目根目录启动：

```powershell
docker compose up --build
```

打开 <http://127.0.0.1:5173>。前端和后端的代码目录会挂载进容器，修改代码后服务会自动重载；SQLite 数据库保存在 `backend/ai_job_assistant.db`。Compose 还会用 llama.cpp 的 CPU 容器启动 `Qwen3-Embedding-0.6B-GGUF:Q8_0`，OpenAI 兼容服务地址为 <http://127.0.0.1:11434/v1>。这是 Q8 量化的千问 0.6B Embedding 模型，约 639 MB，首次启动会自动下载，之后缓存在 Docker 卷 `embedding_models` 中。

如果只修改了前端依赖，在项目根目录执行 `docker compose run --rm frontend npm install`，然后重新运行 `docker compose up`。停止开发环境使用 `docker compose down`；前端 Node.js 依赖和模型文件分别保存在 Compose 卷中。CPU 推理首次加载和每次冷启动会比 GPU 慢，但不需要 NVIDIA 显卡。模型加载完成后，可访问 <http://127.0.0.1:11434/health> 检查服务状态。

## 使用方式

1. 在「我的简历」上传文件并提取文字，或直接粘贴简历。
2. 生成结构化简历，可编辑 JSON 并预览，再保存为新版本。
3. 岗位匹配、优化、面试和综合分析使用页面中当前的简历草稿，未保存也可分析。修改简历原文后，旧的结构化内容会清除，可重新生成。
4. 激活历史简历版本会加载该版本并替换页面草稿；取消激活不会删除任何版本。
5. 在「综合分析」或「历史记录」中下载报告。刷新页面会加载服务端激活的版本，尚未保存的草稿和页面分析结果不会保留；已完成的分析可在历史记录中查看。

## 验证与构建

在 `frontend` 目录执行：

```powershell
npm test
npm run build
npm run preview
```

预览地址为 <http://127.0.0.1:4173>，仍需要后端运行。生产构建输出到 `frontend/dist`。部署时由静态服务器托管此目录，并将同源 `/api/` 反向代理至 FastAPI；Vite 开发和预览代理不会包含在构建产物中。

构建工具说明见 [Vite 官方指南](https://vite.dev/guide/)。
