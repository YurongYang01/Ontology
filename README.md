# Ontology Project

这是一个基于 Python 的本体（Ontology）管理系统，用于构建和管理结构化的知识图谱。它允许用户定义实体（Entity）、属性（Properties）以及实体之间的关系（Relation），并将数据持久化存储为 JSONL 格式。

## 核心功能

*   **实体管理**：创建、更新、查询、删除各类实体（如 Person, Project, Task 等）。
*   **关系管理**：建立实体之间的关联（如 `has_task`, `assigned_to` 等）。
*   **持久化存储**：所有数据以 Append-only 的方式存储在 `memory/ontology/graph.jsonl` 中，支持历史追溯。
*   **Schema 定义**：通过 `memory/ontology/schema.yaml` 定义灵活的实体类型和约束。
*   **CLI 命令行工具**：提供便捷的命令行接口进行所有操作。

## 项目结构

```
Ontology/
├── memory/
│   └── ontology/
│       ├── graph.jsonl       # 存储实体和关系数据的数据库文件
│       ├── schema.yaml       # 定义实体类型、属性和关系的 Schema
│       └── tool_graph.jsonl  # (可选) 工具相关的图数据
├── ontology_tool/            # 核心逻辑包
│   ├── core/
│   │   ├── manager.py        # 核心管理器，处理 CRUD 操作
│   │   ├── exporter.py       # 数据导出逻辑
│   │   ├── extractor.py      # 数据提取逻辑
│   │   └── importer.py       # 数据导入逻辑
    │   └── utils/
    │       └── app.py            # Streamlit 可视化 Web 应用
    ├── scripts/
    │   └── ontology.py           # 命令行入口脚本
└── README.md                 # 项目文档
```

## 快速开始

### 1. 环境准备

确保已安装 Python 3。

建议安装以下依赖以支持可视化和 AI 功能：
```bash
pip install streamlit streamlit-agraph python-dotenv langchain-core langchain-openai pydantic pyyaml
```

### 2. 使用可视化界面 (Web UI)

本项目提供了一个基于 Streamlit 的图形化界面，支持手动录入、AI 提取和图谱可视化。

```bash
streamlit run ontology_tool/utils/app.py
```

*   **Build**: 手动创建实体/关系，或通过 DeepSeek AI 从文本中提取。
*   **Visualize**: 交互式查看知识图谱。
*   **Export**: 导出 RDF 或 JSONL 数据。

注意：Web 应用默认使用独立的数据库文件 `memory/ontology/tool_graph.jsonl`。

### 3. 使用命令行工具

主要的操作入口是 `scripts/ontology.py`。

#### 创建实体

```bash
# 创建一个 Person 实体
python scripts/ontology.py create --type Person --props '{"name":"Alice", "email":"alice@example.com"}'

# 创建一个 Task 实体
python scripts/ontology.py create --type Task --props '{"title":"Complete README", "status":"open"}'
```

#### 查询实体

```bash
# 列出所有 Person 类型的实体
python scripts/ontology.py list --type Person

# 根据 ID 获取特定实体 (假设 ID 为 p_1234abcd)
python scripts/ontology.py get --id p_1234abcd

# 根据属性查询实体
python scripts/ontology.py query --type Task --where '{"status":"open"}'
```

#### 建立关系

```bash
# 将任务关联到人员 (假设 Project ID 为 proj_001, Task ID 为 task_001)
python scripts/ontology.py relate --from proj_001 --rel has_task --to task_001
```

#### 查询关系

```bash
# 查看某个实体相关的关系
python scripts/ontology.py related --id proj_001 --rel has_task
```

#### 删除实体

```bash
python scripts/ontology.py delete --id p_1234abcd
```

## 数据模型 (Schema)

项目使用 `memory/ontology/schema.yaml` 定义数据模型。核心实体类型包括：

*   **Person**: 人员信息 (name, email, etc.)
*   **Organization**: 组织机构
*   **Project**: 项目 (name, status, owner, etc.)
*   **Task**: 任务 (title, status, priority, etc.)
*   **Goal**: 目标
*   **Event**: 日程事件
*   **Location**: 地点
*   **Document / Message / Note**: 信息类实体
*   **Account / Device**: 资源类实体

更多详细定义请参考 `memory/ontology/schema.yaml` 文件。

## 数据存储

数据默认存储在 `memory/ontology/graph.jsonl`。每一行是一个 JSON 对象，记录了一次操作（create, update, delete, relate 等），系统通过重放这些操作来构建当前的图谱状态。
