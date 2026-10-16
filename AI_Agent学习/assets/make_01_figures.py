# -*- coding: utf-8 -*-
"""
生成 AI_Agent学习/01 篇的插图：
  assets/chatbot_vs_agent.png   ChatBot vs Agent 工作方式对比
  assets/agent_anatomy.png      Agent 四件套解剖 + 循环
  assets/agent_history.png      Agent 概念 60 年演变时间线
  assets/agent_stack.png        2026 Agent 生态分层地图
"""
import sys

import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
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


def box(ax, x, y, w, h, text, fc, ec, fs=12, bold=True, round_size=0.06):
    """画一个圆角盒子，中心在 (x, y)，text 自动换行由调用者给 \n。"""
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                boxstyle=f"round,pad=0.02,rounding_size={round_size}",
                                fc=fc, ec=ec, lw=2))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color="#111827")


def arrow(ax, x1, y1, x2, y2, color="#374151", style="-|>", lw=2.2,
          connectionstyle="arc3,rad=0.0", ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=18, lw=lw, color=color,
                                 linestyle=ls, connectionstyle=connectionstyle))


def fig_chatbot_vs_agent():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.6), dpi=150)

    # ---- 左：ChatBot ----
    ax = axes[0]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_title("ChatBot：问一句答一句，回合结束", fontsize=15, fontweight="bold", pad=12)
    box(ax, 5, 8.5, 5.2, 1.3, "用户提问\n「北京今天天气如何？」", C_GRAY, C_GRAY_E, 11)
    box(ax, 5, 5.0, 4.2, 1.6, "LLM\n（下一个词预测机）", C_BLUE, C_BLUE_E, 12)
    box(ax, 5, 1.5, 5.2, 1.3, "直接回答\n（只能靠训练时记住的知识）", C_AMBER, C_AMBER_E, 11)
    arrow(ax, 5, 7.8, 5, 5.9)
    arrow(ax, 5, 4.1, 5, 2.2)
    ax.text(5, 0.3, "没有任何工具，答不上就只能编（幻觉）", ha="center",
            fontsize=10.5, color=C_RED_E, style="italic")

    # ---- 右：Agent ----
    ax = axes[1]
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_title("Agent：思考 → 行动 → 观察，循环到达成为止", fontsize=15, fontweight="bold", pad=12)
    box(ax, 5, 8.7, 5.2, 1.1, "用户给目标\n「帮我订明天去上海最便宜的机票」", C_GRAY, C_GRAY_E, 10.5)
    box(ax, 5, 5.6, 4.4, 1.5, "大脑（LLM）\n规划 + 决策下一步", C_BLUE, C_BLUE_E, 12)
    box(ax, 8.6, 2.8, 2.6, 1.4, "行动\n调用工具", C_GREEN, C_GREEN_E, 12)
    box(ax, 1.4, 2.8, 2.6, 1.4, "观察\n读取结果", C_PURPLE, C_PURPLE_E, 12)
    box(ax, 5, 0.7, 4.6, 1.0, "目标达成 → 汇总交付", C_AMBER, C_AMBER_E, 11)
    arrow(ax, 5, 8.1, 5, 6.4)
    arrow(ax, 6.9, 5.0, 8.2, 3.6)                      # 大脑→行动
    arrow(ax, 7.4, 2.5, 2.7, 2.5)                      # 行动→观察
    arrow(ax, 1.8, 3.6, 3.6, 5.0)                      # 观察→大脑（循环）
    ax.text(2.6, 4.6, "结果不够\n继续循环", fontsize=9.5, color="#374151", ha="center")
    arrow(ax, 5, 4.8, 5, 1.25)                         # 大脑→交付
    ax.text(5.6, 3.0, "结果够了", fontsize=9.5, color="#374151")

    fig.tight_layout()
    fig.savefig(f"{ASSETS}/chatbot_vs_agent.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_agent_anatomy():
    fig, ax = plt.subplots(figsize=(11, 8), dpi=150)
    ax.set_xlim(0, 12); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_title("Agent 解剖图：一个大脑，三件套装备", fontsize=16, fontweight="bold", pad=14)

    # 中央大脑
    box(ax, 6, 5.2, 4.0, 2.2, "大脑（LLM）\n理解意图 · 推理 · 决策\n「下一步该做什么？」", C_BLUE, C_BLUE_E, 13)

    # 三件套
    box(ax, 1.7, 8.4, 3.3, 1.9, "工具 Tools\n模型的「手」\n搜索 / 数据库 / API\n代码执行 / 文件读写", C_GREEN, C_GREEN_E, 10.5)
    box(ax, 10.3, 8.4, 3.3, 1.9, "记忆 Memory\n模型的「笔记本」\n短期：对话历史\n长期：用户偏好、知识库", C_PURPLE, C_PURPLE_E, 10.5)
    box(ax, 6, 8.6, 3.3, 1.7, "规划 Planning\n模型的「作战地图」\n大目标 → 拆步骤\n定顺序、设检查点", C_AMBER, C_AMBER_E, 10.5)

    # 底部循环
    box(ax, 6, 1.4, 9.4, 1.5,
        "工作循环：思考 Thought → 行动 Action（调工具）→ 观察 Observation（读结果）→ 再思考……",
        C_GRAY, C_GRAY_E, 11.5)

    # 连线
    arrow(ax, 4.6, 6.1, 2.6, 7.5)    # 大脑 ↔ 工具
    arrow(ax, 2.8, 7.6, 4.4, 5.9, style="-|>", ls="--")
    arrow(ax, 7.4, 6.1, 9.4, 7.5)    # 大脑 ↔ 记忆
    arrow(ax, 9.2, 7.6, 7.6, 5.9, style="-|>", ls="--")
    arrow(ax, 6, 6.3, 6, 7.65)       # 大脑 ↔ 规划
    arrow(ax, 5.6, 7.65, 5.6, 6.3, style="-|>", ls="--")
    arrow(ax, 6, 4.1, 6, 2.2)        # 大脑 → 循环

    ax.text(6, 0.4, "智能主要来自大脑；工程的价值在于把工具、记忆、规划接好",
            ha="center", fontsize=10.5, color=C_GRAY_E, style="italic")

    fig.tight_layout()
    fig.savefig(f"{ASSETS}/agent_anatomy.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_agent_history():
    fig, ax = plt.subplots(figsize=(13, 5.8), dpi=150)
    ax.set_xlim(0, 14); ax.set_ylim(0, 8); ax.axis("off")
    ax.set_title("「智能体」概念 60 年：从手写规则到大模型驱动", fontsize=16, fontweight="bold", pad=14)

    # 主轴
    arrow(ax, 0.5, 4.0, 13.6, 4.0, color="#9ca3af", lw=3)

    events = [
        (1.3, True,  "1960s-80s", "符号主义专家系统\n人手写规则 if-then\n（不会学习）", C_GRAY, C_GRAY_E),
        (3.4, False, "1990s-2010s", "强化学习智能体\n与环境交互试错学策略\n（你学过的五要素！）", C_GREEN, C_GREEN_E),
        (5.3, True,  "2016", "AlphaGo\nRL + 深度网络的巅峰\n（只会下棋，不会说话）", C_GREEN, C_GREEN_E),
        (7.2, False, "2022", "ReAct 论文\n把「思考」写成文本\nLLM 开始会「边想边做」", C_BLUE, C_BLUE_E),
        (9.1, True,  "2023", "AutoGPT 爆火 +\nFunction Calling 发布\n工具调用标准化", C_BLUE, C_BLUE_E),
        (11.0, False, "2024-25", "MCP 协议统一工具接口\nClaude/GPT 原生电脑操作\nAgent 落地元年", C_PURPLE, C_PURPLE_E),
        (12.9, True, "2026", "多智能体协作普及\nA2A 协议出现\nAgent 成为基础设施", C_AMBER, C_AMBER_E),
    ]
    for x, up, year, text, fc, ec in events:
        ax.plot([x], [4.0], marker="o", ms=9, color=ec, zorder=5)
        y_text = 5.6 if up else 2.4
        box(ax, x, y_text, 1.85, 1.7, f"{year}\n{text}", fc, ec, fs=8.2, bold=False)
        arrow(ax, x, 4.0, x, y_text - 0.95 if up else y_text + 0.95, color=ec, lw=1.4)

    ax.text(7, 0.3, "主线趋势：「决策智能」从手写规则 → 试错学习 → 大模型语言推理，能力越来越通用",
            ha="center", fontsize=11, color="#374151", style="italic")
    fig.tight_layout()
    fig.savefig(f"{ASSETS}/agent_history.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_agent_stack():
    fig, ax = plt.subplots(figsize=(11, 7.6), dpi=150)
    ax.set_xlim(0, 12); ax.set_ylim(0, 10); ax.axis("off")
    ax.set_title("2026 年 Agent 开发生态分层地图", fontsize=16, fontweight="bold", pad=14)

    layers = [
        (8.3, "平台层（低代码）", "Coze 扣子 · Dify · 各厂 Agent 平台——拖拽搭建，不写代码", C_AMBER, C_AMBER_E),
        (6.4, "框架层（编排）", "LangGraph（状态图·生产主流）· CrewAI（角色分工·上手快）\nAutoGen · OpenAI Agents SDK · Pydantic AI", C_PURPLE, C_PURPLE_E),
        (4.5, "协议层（接口标准）", "MCP：模型与工具之间的统一接口（工具界的 USB）\nA2A：Agent 与 Agent 之间的对话协议", C_BLUE, C_BLUE_E),
        (2.6, "模型层（大脑）", "GPT · Claude · Qwen · DeepSeek · 本地 Ollama\n本课程默认：离线 mock 可学全部原理，真模型可选", C_GREEN, C_GREEN_E),
    ]
    for y, name, detail, fc, ec in layers:
        box(ax, 2.2, y, 3.2, 1.5, name, fc, ec, 12.5)
        box(ax, 7.4, y, 7.4, 1.5, detail, "#ffffff", ec, 10, bold=False)

    arrow(ax, 6, 1.4, 6, 1.75, color="#9ca3af")
    ax.text(6, 0.9, "越往下越基础：本课程 02~04 篇手写原理（不依赖框架），05~06 篇上框架",
            ha="center", fontsize=10.5, color=C_GRAY_E, style="italic")

    fig.tight_layout()
    fig.savefig(f"{ASSETS}/agent_stack.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    import os
    os.makedirs(ASSETS, exist_ok=True)
    fig_chatbot_vs_agent()
    print("✔ chatbot_vs_agent.png")
    fig_agent_anatomy()
    print("✔ agent_anatomy.png")
    fig_agent_history()
    print("✔ agent_history.png")
    fig_agent_stack()
    print("✔ agent_stack.png")


if __name__ == "__main__":
    main()
