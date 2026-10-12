# -*- coding: utf-8 -*-
"""强化学习核心循环图：智能体 ↔ 环境"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

OUT = r"D:\Lei_learning\PyTorch学习\00_理论基础\assets"

C_MAIN = "#2f6fdd"; C_GRAY = "#6b7280"; C_GREEN = "#059669"
C_BG1 = "#f4f7ff"; C_BG2 = "#ecfdf5"

fig, ax = plt.subplots(figsize=(8.6, 4.8), dpi=160)
ax.set_xlim(0, 12); ax.set_ylim(0, 6.6); ax.axis("off")

ax.text(6, 6.25, "强化学习的核心循环", ha="center", fontsize=15,
        fontweight="bold", color="#111827")

def box(x, y, w, h, title, sub, fc, ec):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                                fc=fc, ec=ec, lw=2))
    ax.text(x + w/2, y + h*0.64, title, ha="center", va="center",
            fontsize=15, fontweight="bold", color="#111827")
    ax.text(x + w/2, y + h*0.28, sub, ha="center", va="center",
            fontsize=9.5, color=C_GRAY)

# 智能体（左）、环境（右）
box(0.9, 2.5, 3.4, 1.7, "智能体", "做决策、要学习的那一方\n（狗 / AI 棋手 / AI 玩家）", C_BG1, C_MAIN)
box(7.7, 2.5, 3.4, 1.7, "环境", "智能体所处的世界\n（你和房间 / 棋盘和对手 / 关卡）", C_BG2, C_GREEN)

# 上方弧箭头：动作（智能体 → 环境）
ax.add_patch(FancyArrowPatch((4.35, 3.85), (7.65, 3.85),
             connectionstyle="arc3,rad=-0.35", arrowstyle="-|>",
             mutation_scale=20, lw=2.2, color=C_MAIN))
ax.text(6, 5.15, "动作（做什么）", ha="center", fontsize=12,
        fontweight="bold", color=C_MAIN)
ax.text(6, 4.78, "坐下 / 落子 / 向左跳", ha="center", fontsize=9, color=C_GRAY)

# 下方弧箭头：新状态 + 奖励（环境 → 智能体）
ax.add_patch(FancyArrowPatch((7.65, 2.85), (4.35, 2.85),
             connectionstyle="arc3,rad=-0.35", arrowstyle="-|>",
             mutation_scale=20, lw=2.2, color=C_GREEN))
ax.text(6, 1.62, "新状态 + 奖励（变成什么样 + 得几分）", ha="center",
        fontsize=12, fontweight="bold", color=C_GREEN)
ax.text(6, 1.25, "你又说了一声「坐」+ 零食 / 新棋局 + 输赢 / 新画面 + 金币",
        ha="center", fontsize=9, color=C_GRAY)

ax.text(6, 0.42, "这个循环一圈圈转下去，智能体要学的只有一件事：策略 —— 看到什么状态，该做什么动作",
        ha="center", fontsize=9.5, color=C_GRAY)

fig.savefig(os.path.join(OUT, "rl_agent_env_loop.png"), bbox_inches="tight",
            facecolor="white")
plt.close(fig)
print("done")
