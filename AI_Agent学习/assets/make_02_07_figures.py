# -*- coding: utf-8 -*-
"""
生成 AI_Agent学习 02~07 篇的插图：
  assets/prompt_anatomy.png      02 篇：Prompt 结构解剖
  assets/react_loop_detail.png   03 篇：Function Calling 消息时序
  assets/rag_pipeline.png        04 篇：RAG 双泳道流程
  assets/langgraph_state.png     05 篇：LangGraph 状态图
  assets/multiagent_mcp.png      06 篇：多智能体协作 + MCP 架构
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

ASSETS = "assets"
C_BLUE = "#dbeafe"; C_BLUE_E = "#2563eb"
C_GREEN = "#dcfce7"; C_GREEN_E = "#16a34a"
C_AMBER = "#fef3c7"; C_AMBER_E = "#d97706"
C_PURPLE = "#ede9fe"; C_PURPLE_E = "#7c3aed"
C_GRAY = "#f3f4f6"; C_GRAY_E = "#6b7280"
C_RED = "#fee2e2"; C_RED_E = "#dc2626"


def box(ax, x, y, w, h, text, fc, ec, fs=11, bold=True):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=fc, ec=ec, lw=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color="#111827")


def arrow(ax, x1, y1, x2, y2, color="#374151", lw=2.2, ls="-", rad=0.0, label=None, lfs=9.5):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=18, lw=lw, color=color,
                                 linestyle=ls, connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((x1 + x2) / 2 + 0.15, (y1 + y2) / 2, label, fontsize=lfs, color="#374151")


def fig_prompt_anatomy():
    """02 篇：一条发给模型的消息里都有什么。"""
    fig, ax = plt.subplots(figsize=(11, 7.4), dpi=150)
    ax.set_xlim(0, 12); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_title("Prompt 解剖：一条消息里的六个零件", fontsize=16, fontweight="bold", pad=14)

    parts = [
        (8.6, "① 角色设定 system", "「你是一个资深数据分析师，回答简洁专业」\n定身份、定语气、定边界", C_PURPLE, C_PURPLE_E),
        (7.0, "② 任务指令 instruction", "「把下面这段话总结成三个要点」\n一句话说清要什么，动词开头", C_BLUE, C_BLUE_E),
        (5.4, "③ 上下文 context", "背景资料、检索回来的文档、对话历史\n（RAG 喂的内容就放这里）", C_GREEN, C_GREEN_E),
        (3.8, "④ 示例 few-shot", "给 1~3 个「输入 → 输出」样例\n模型照猫画虎，格式最稳", C_AMBER, C_AMBER_E),
        (2.2, "⑤ 输出格式 format", "「用 JSON 回答，字段为 …」\nAgent 的生命线：机器要解析", C_RED, C_RED_E),
    ]
    for y, name, detail, fc, ec in parts:
        box(ax, 2.9, y, 4.4, 1.35, name, fc, ec, 12)
        box(ax, 8.3, y, 6.2, 1.35, detail, "#ffffff", ec, 10, bold=False)

    box(ax, 2.9, 0.7, 4.4, 0.9, "用户输入 user", C_GRAY, C_GRAY_E, 11)
    ax.text(8.3, 0.7, "以上五件拼成一个 Prompt 发给模型",
            ha="center", fontsize=10.5, color=C_GRAY_E, style="italic")
    fig.tight_layout()
    fig.savefig(f"{ASSETS}/prompt_anatomy.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_react_loop_detail():
    """03 篇：Function Calling 的完整消息时序。"""
    fig, ax = plt.subplots(figsize=(11.5, 7.8), dpi=150)
    ax.set_xlim(0, 13); ax.set_ylim(0, 10.5); ax.axis("off")
    ax.set_title("Function Calling 时序：模型负责「决定」，程序负责「执行」", fontsize=15, fontweight="bold", pad=14)

    # 两条泳道
    box(ax, 2.6, 9.6, 4.0, 0.8, "你的程序（Python）", C_GRAY, C_GRAY_E, 12)
    box(ax, 10.2, 9.6, 4.0, 0.8, "LLM（大脑）", C_BLUE, C_BLUE_E, 12)
    ax.plot([2.6, 2.6], [0.5, 9.2], color="#d1d5db", lw=1.5, ls="--")
    ax.plot([10.2, 10.2], [0.5, 9.2], color="#d1d5db", lw=1.5, ls="--")

    steps = [
        (8.5, "→", "用户问题 + 工具清单（JSON Schema）", C_BLUE_E),
        (7.1, "←", "模型：「我要调 search，参数 {q: 特斯拉财报}」\n（只输出决定，不真的执行！）", C_BLUE_E),
        (5.5, "·", "程序解析 JSON → 真的调用 search() → 拿到结果", C_GREEN_E),
        (4.1, "→", "把工具结果追加进对话，再次发给模型", C_GREEN_E),
        (2.7, "←", "模型：信息够了 → 输出最终答案\n（或不够 → 再要一次工具，回到第 2 步）", C_BLUE_E),
    ]
    for y, direction, text, color in steps:
        if direction == "→":
            arrow(ax, 3.4, y, 9.4, y, color=color)
        elif direction == "←":
            arrow(ax, 9.4, y, 3.4, y, color=color)
        box(ax, 6.4, y - 0.62, 11.6, 1.0 if "\n" not in text else 1.15, text,
            "#ffffff", color, 9.8, bold=False)

    ax.text(6.4, 0.35, "关键：模型永远不会自己执行工具——执行权永远在你的程序手里（安全闸门）",
            ha="center", fontsize=10.5, color=C_RED_E, style="italic")
    fig.tight_layout()
    fig.savefig(f"{ASSETS}/react_loop_detail.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_rag_pipeline():
    """04 篇：RAG 离线建索引 + 在线检索生成。"""
    fig, ax = plt.subplots(figsize=(12.5, 7.6), dpi=150)
    ax.set_xlim(0, 14); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_title("RAG 全景：离线建一次索引，在线每次都「先查后答」", fontsize=15, fontweight="bold", pad=14)

    # 上泳道：离线
    box(ax, 7, 9.1, 13.2, 0.75, "离线阶段（文档更新时跑一次）：把知识库变成可检索的向量库", C_PURPLE, C_PURPLE_E, 11.5)
    steps_off = [
        (1.8, "文档集合\nPDF / MD / 网页", C_GRAY, C_GRAY_E),
        (5.2, "切分 chunking\n按语义切成小段\n（重叠 10~20%）", C_AMBER, C_AMBER_E),
        (8.6, "Embedding 模型\n每段 → 一个向量\n（你 09 章学过的查表升级版）", C_BLUE, C_BLUE_E),
        (12.0, "向量数据库\n向量 + 原文存档\n（Chroma / Milvus）", C_GREEN, C_GREEN_E),
    ]
    for x, text, fc, ec in steps_off:
        box(ax, x, 7.3, 3.1, 1.6, text, fc, ec, 9.8, bold=False)
    for x1, x2 in [(3.4, 3.6), (6.9, 7.0), (10.3, 10.4)]:
        arrow(ax, x1, 7.3, x2 + 0.35, 7.3)

    # 下泳道：在线
    box(ax, 7, 4.9, 13.2, 0.75, "在线阶段（每次提问都跑）：检索 → 拼上下文 → 生成", C_BLUE, C_BLUE_E, 11.5)
    steps_on = [
        (1.8, "用户问题\n「报销比例多少？」", C_GRAY, C_GRAY_E),
        (5.2, "问题也向量化\n去向量库找最像的\nTop-k 段", C_BLUE, C_BLUE_E),
        (8.6, "拼接 Prompt\n问题 + 检索到的原文\n一起发给 LLM", C_AMBER, C_AMBER_E),
        (12.0, "LLM 生成\n基于给定资料回答\n附引用来源", C_GREEN, C_GREEN_E),
    ]
    for x, text, fc, ec in steps_on:
        box(ax, x, 3.1, 3.1, 1.6, text, fc, ec, 9.8, bold=False)
    for x1, x2 in [(3.4, 3.6), (6.9, 7.0), (10.3, 10.4)]:
        arrow(ax, x1, 3.1, x2 + 0.35, 3.1)

    # 向量库 → 在线检索的连接
    arrow(ax, 12.0, 6.5, 5.9, 3.9, color=C_GREEN_E, ls="--", rad=0.25)
    ax.text(9.9, 5.6, "同一个向量库", fontsize=9.5, color=C_GREEN_E)

    ax.text(7, 0.6, "效果：模型回答被「锚定」在你的资料上——知识更新不用重训模型，换文档就行",
            ha="center", fontsize=10.5, color=C_GRAY_E, style="italic")
    fig.tight_layout()
    fig.savefig(f"{ASSETS}/rag_pipeline.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_langgraph_state():
    """05 篇：LangGraph 把 Agent 循环画成状态图。"""
    fig, ax = plt.subplots(figsize=(11, 7), dpi=150)
    ax.set_xlim(0, 12); ax.set_ylim(0, 9.5); ax.axis("off")
    ax.set_title("LangGraph 核心思想：Agent 循环 = 一张状态图", fontsize=15, fontweight="bold", pad=14)

    box(ax, 2.0, 7.6, 2.6, 1.3, "START\n用户目标进来", C_GRAY, C_GRAY_E, 11)
    box(ax, 6.0, 7.6, 3.0, 1.5, "agent 节点\nLLM 思考：\n调工具 or 收工？", C_BLUE, C_BLUE_E, 11)
    box(ax, 10.0, 7.6, 2.8, 1.5, "tools 节点\n执行工具\n结果写回状态", C_GREEN, C_GREEN_E, 11)
    box(ax, 6.0, 4.6, 3.0, 1.3, "END\n输出最终答案", C_AMBER, C_AMBER_E, 11)

    arrow(ax, 3.3, 7.6, 4.5, 7.6)
    arrow(ax, 7.5, 7.6, 8.6, 7.6, label="要调工具")
    arrow(ax, 10.0, 6.8, 6.4, 6.9, rad=-0.35, color=C_GREEN_E, label="结果回来，再想")
    arrow(ax, 6.0, 6.8, 6.0, 5.3, label="信息够了")

    box(ax, 6.0, 2.2, 10.6, 2.2,
        "全局状态 State（所有节点共享的一块白板）\n"
        "{ messages: 对话记录,  tool_results: 工具结果,  step: 已走圈数 }\n"
        "每个节点读完状态 → 干自己的活 → 把更新写回状态",
        "#ffffff", C_PURPLE_E, 10.5, bold=False)
    arrow(ax, 6.0, 3.95, 6.0, 3.35, color=C_PURPLE_E, ls="--")

    ax.text(6.0, 0.5, "对比手写循环：流程从「藏在 while 里」变成「画在图上」——可视化、可持久化、可插入人审节点",
            ha="center", fontsize=10, color=C_GRAY_E, style="italic")
    fig.tight_layout()
    fig.savefig(f"{ASSETS}/langgraph_state.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_multiagent_mcp():
    """06 篇：多智能体协作模式 + MCP 解决的 N×M 问题。"""
    fig, axes = plt.subplots(1, 2, figsize=(13.5, 6.4), dpi=150)

    # 左：多智能体
    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_title("多智能体：主管 - 工人模式", fontsize=14, fontweight="bold", pad=12)
    box(ax, 5, 8.6, 4.4, 1.2, "主管 Agent\n拆任务 · 派活 · 汇总", C_BLUE, C_BLUE_E, 11)
    workers = [(1.9, "研究员\n搜索整理资料", C_GREEN, C_GREEN_E),
               (5.0, "写手\n撰写报告初稿", C_AMBER, C_AMBER_E),
               (8.1, "审核员\n挑错打分退回", C_PURPLE, C_PURPLE_E)]
    for x, text, fc, ec in workers:
        box(ax, x, 4.6, 2.7, 1.7, text, fc, ec, 10)
        arrow(ax, 5, 7.95, x, 5.5, color="#6b7280", lw=1.6)
        arrow(ax, x, 5.5, 5, 7.95, color="#6b7280", lw=1.2, ls="--", rad=0.15)
    box(ax, 5, 1.9, 8.6, 1.4, "为什么要多个？每个 Agent 上下文独立、角色单一\n——比一个「全能 Agent」更不容易乱", "#ffffff", C_GRAY_E, 10, bold=False)

    # 右：MCP
    ax = axes[1]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_title("MCP：N×M 的集成噩梦 → N+M", fontsize=14, fontweight="bold", pad=12)
    box(ax, 2.0, 8.0, 3.0, 2.4, "M 个应用\n\nClaude\nGPT\n你的程序", C_BLUE, C_BLUE_E, 10)
    box(ax, 8.0, 8.0, 3.0, 2.4, "N 个工具\n\nGitHub\n数据库\n飞书", C_GREEN, C_GREEN_E, 10)
    ax.text(5.0, 8.0, "以前：每个应用\n给每个工具\n写一套对接\n= M×N 份代码", ha="center", va="center",
            fontsize=9.5, color=C_RED_E,
            bbox=dict(boxstyle="round,pad=0.4", fc=C_RED, ec=C_RED_E))
    box(ax, 5.0, 4.4, 3.6, 1.2, "MCP 协议层\n统一接口（USB）", C_AMBER, C_AMBER_E, 11)
    arrow(ax, 2.6, 6.8, 4.2, 5.1); arrow(ax, 7.4, 6.8, 5.8, 5.1)
    box(ax, 5.0, 1.9, 8.8, 1.3, "现在：应用实现一次 MCP 客户端，工具实现一次 MCP 服务端\n= M+N 份代码，工具一次编写、处处可用", "#ffffff", C_GRAY_E, 10, bold=False)

    fig.tight_layout()
    fig.savefig(f"{ASSETS}/multiagent_mcp.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    import os
    os.makedirs(ASSETS, exist_ok=True)
    fig_prompt_anatomy();    print("✔ prompt_anatomy.png")
    fig_react_loop_detail(); print("✔ react_loop_detail.png")
    fig_rag_pipeline();      print("✔ rag_pipeline.png")
    fig_langgraph_state();   print("✔ langgraph_state.png")
    fig_multiagent_mcp();    print("✔ multiagent_mcp.png")


if __name__ == "__main__":
    main()
