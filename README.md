# Intelligent Ontology Agent System

这是一个结合了**本体建模 (Ontology Modeling)** 与 **智能代理 (Intelligent Agent)** 的综合系统。它不仅允许用户构建和管理结构化的知识图谱，还提供了一个支持多轮对话的智能助手，能够理解自然语言问题，查询图数据库，并结合外部工具提供准确的回答。

## 🌟 核心功能

### 1. 知识图谱构建与管理 (Ontology Tool)
*   **可视化建模**: 基于 Streamlit 的 Web 界面，支持实体和关系的增删改查。
*   **AI 辅助提取**: 利用 DeepSeek LLM 从非结构化文本中自动提取实体和关系。
*   **图谱可视化**: 交互式展示知识图谱结构。
*   **多格式支持**: 支持导出 RDF (Turtle) 和 JSONL 格式。

### 2. 智能问答代理 (Agent System)
*   **多轮交互式问答**: 支持上下文记忆的自然语言对话。
*   **混合查询引擎**: 结合 SPARQL 图查询与 LLM 语义理解。
*   **智能工具调用**: 动态调用外部工具（如计算器）增强回答能力。
*   **高并发架构**: 基于 `asyncio` 的异步处理机制，支持快速响应。

---

## 📂 项目结构

```text
Ontology/
├── agent_system/               # [NEW] 智能问答代理核心模块
│   ├── generation_module.py    # 答案生成 (LLM集成)
│   ├── integration_module.py   # 代理编排与对话状态管理
│   ├── query_module.py         # SPARQL 查询引擎
│   ├── parsing_module.py       # 结果解析与自然语言转换
│   ├── tool_manager.py         # 工具调用管理
│   └── main.py                 # 交互式 CLI 入口
│
├── ontology_tool/              # 本体管理核心工具
│   ├── core/                   # 核心 CRUD 与导入导出逻辑
│   └── utils/
│       └── app.py              # Streamlit 可视化 Web 应用
│
├── memory/
│   └── ontology/
│       ├── graph.jsonl         # 核心数据库 (JSONL 格式)
│       └── schema.yaml         # 数据模型定义
│
├── tests/                      # 单元与集成测试
├── run.py                      # 系统统一启动入口
└── README.md                   # 项目文档
```

---

## 🚀 快速开始

### 1. 环境准备

确保安装 Python 3.10+。

安装依赖：
```bash
pip install streamlit streamlit-agraph python-dotenv langchain-openai langchain-core rdflib pydantic pyyaml
```

配置环境变量：
创建 `.env` 文件并填入你的 DeepSeek API Key（兼容 OpenAI 格式）：
```ini
DEEPSEEK_API_KEY=sk-xxxxxx
```

### 2. 第一步：构建知识库 (Web UI)

使用可视化界面录入或导入数据。

```bash
streamlit run ontology_tool/app.py
```

*   打开浏览器访问显示的 URL (通常是 `http://localhost:8501`)。
*   在 **"Build"** 标签页中手动添加实体（如 `Person`, `Task`），或粘贴文本让 AI 自动提取。
*   在 **"Visualize"** 标签页查看数据结构。

### 3. 第二步：与 Agent 对话 (CLI)

启动智能问答助手，查询刚才构建的知识库。

```bash
python3 run.py
```

**示例对话：**
```text
[系统]: 欢迎使用智能本体 Agent 问答系统
[用户]: 这里有哪些任务？
[Agent]: 目前系统中有以下任务：
1. "Complete README" (状态: open)
2. "Fix Bugs" (状态: in_progress)

[用户]: 谁负责 "Fix Bugs"？
[Agent]: 根据关系数据，"Alice" 被指派负责 "Fix Bugs" 任务。
```

---

## 📖 详细使用说明

### 交互式命令行 (CLI)

Agent 系统支持以下指令：
*   **普通对话**: 直接输入自然语言问题。
*   **`clear`**: 清除当前的对话历史（重置上下文）。
*   **`exit` / `quit`**: 退出系统。

### 数据模型 (Schema)

项目默认定义了通用的项目管理本体 (`memory/ontology/schema.yaml`)，包含：
*   **Person**: 人员
*   **Task**: 任务
*   **Project**: 项目
*   **Organization**: 组织
*   **Relations**: `has_task`, `assigned_to`, `part_of` 等。

你可以修改 schema 文件来适配不同的领域。

---

## 🛠️ 开发与测试

运行所有测试用例以确保系统稳定性：

```bash
python3 -m unittest discover tests
```

### 核心技术栈

*   **LLM Framework**: LangChain
*   **Ontology/Graph**: RDFLib, SPARQL
*   **Web UI**: Streamlit, Streamlit-Agraph
*   **Storage**: JSON Lines (Append-only log)
