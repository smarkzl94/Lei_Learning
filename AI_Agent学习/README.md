# AI Agent 开发专题

> 前置：已完成 PyTorch 主线 00~05 章 + Transformer 专题（懂自注意力、会搭训练循环）。
> 目标：从"会训练模型"升级到"会让模型干活"——手写 Agent 循环 → 用框架 → 多智能体 → 上线。

## 🗺 课程地图

| 篇 | 主题 | 核心问题 | 配套实战 |
|---|---|---|---|
| 01 | 什么是 AI Agent | Agent 和聊天机器人差在哪？大脑/工具/记忆/规划四件套 | — |
| 02 | Prompt 工程与结构化输出 | 怎么让模型稳定输出能解析的 JSON？ | agent01_json_output.py |
| 03 | 工具调用：Function Calling 与 ReAct | 模型怎么"决定"调哪个工具？手写最小 Agent 循环 | agent02_react_loop.py |
| 04 | RAG 检索增强 | 模型不知道的事，怎么现查现用？ | agent03_mini_rag.py |
| 05 | 记忆与规划 | 长任务怎么拆解、状态怎么存？LangGraph 状态图 | agent04_langgraph.py |
| 06 | 多智能体协作与 MCP 生态 | CrewAI 角色分工；MCP 为什么是"工具界的 USB" | agent05_crew.py |
| 07 | 评测、安全与上线 | 怎么知道 Agent 靠不靠谱？成本/护栏/监控 | 毕业项目：个人助理 Agent |

## 🛠 环境说明

- 教程代码分两种模式：**离线 mock（零依赖，必跑）** + **真实 API（可选）**
- 离线模式用手写的 mock LLM 演示原理——Agent 的核心逻辑不依赖任何框架
- 真实模式可选：DeepSeek / 通义千问 API（国内直连、便宜），或本地 Ollama
- 框架篇（05~06）需要时安装：`pip install langgraph crewai`

## 📌 学习规矩（与 PyTorch 课程相同）

1. 每篇按「讲解 → 类比 → 手算/代码验证 → 小测验 → 实操」推进
2. 问答沉淀回本篇文档的「💬 课堂问答沉淀」
3. 定期归档 GitHub + Notion
