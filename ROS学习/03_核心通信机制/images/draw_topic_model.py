# -*- coding: utf-8 -*-
"""绘制 ROS Topic 发布/订阅通信模型图，供 01_话题Topic.md 嵌入"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.executable).parent.parent.parent))
from daimon_runtime import setup_plot
setup_plot()
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(10, 5.2), dpi=150)
ax.set_xlim(0, 100); ax.set_ylim(0, 52); ax.axis("off")
fig.patch.set_facecolor("white")

C_PUB = "#f59e0b"; C_SUB = "#38bdf8"; C_TOPIC = "#a78bfa"
C_BOX = "#1e293b"; C_TEXT = "#e2e8f0"; C_MUTED = "#94a3b8"; C_LINE = "#334155"

def box(x, y, w, h, title, sub, edge, dashed=False, title_color=C_TEXT, sub_color=C_MUTED):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.6",
                       fc=C_BOX, ec=edge, lw=2, ls="--" if dashed else "-")
    ax.add_patch(b)
    ax.text(x + w/2, y + h*0.62, title, ha="center", va="center",
            fontsize=12, fontweight="bold", color=title_color)
    ax.text(x + w/2, y + h*0.28, sub, ha="center", va="center",
            fontsize=9, color=sub_color, family="sans-serif")

def arrow(p1, p2, color, label=None, lx=0, ly=0):
    a = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=18,
                        lw=2.2, color=color, shrinkA=2, shrinkB=2)
    ax.add_patch(a)
    if label:
        ax.text((p1[0]+p2[0])/2 + lx, (p1[1]+p2[1])/2 + ly, label,
                fontsize=10, color=color, fontweight="bold", ha="center")

# 左侧 Publishers
box(4, 34, 22, 10, "Publisher A", "发布者（可多个）", C_PUB)
box(4, 18, 22, 10, "Publisher B", "发布者（可多个）", C_PUB)

# 中间 Topic
box(38, 20, 24, 22, "/chatter", "", C_TOPIC, dashed=True,
    title_color=C_TOPIC)
ax.text(50, 31.2, "消息类型", ha="center", fontsize=8.5, color="#64748b")
ax.text(50, 28.4, "std_msgs/msg/String", ha="center", fontsize=9, color=C_TOPIC, family="sans-serif")
ax.text(50, 25.4, "队列缓冲（默认10条）", ha="center", fontsize=8.5, color="#64748b")
ax.text(50, 22.6, "Topic（消息通道）", ha="center", fontsize=8.5, color=C_MUTED)

# 右侧 Subscribers
box(74, 38, 22, 10, "Subscriber X", "订阅者（可多个）", C_SUB)
box(74, 22, 22, 10, "Subscriber Y", "订阅者（可多个）", C_SUB)
box(74, 5, 22, 10, "观察工具", "ros2 topic echo", "#475569", dashed=True,
    sub_color=C_MUTED)
ax.text(85, 1.8, "（echo 也是 Subscriber）", ha="center", fontsize=8, color=C_MUTED)

# 箭头 Pub -> Topic
arrow((26.5, 39), (37.5, 33.5), C_PUB, "发布 publish()", lx=0, ly=3)
arrow((26.5, 23), (37.5, 27), C_PUB)
# 箭头 Topic -> Sub
arrow((62.5, 33.5), (73.5, 42), C_SUB, "订阅（回调触发）", lx=-5, ly=3.2)
arrow((62.5, 28), (73.5, 26.5), C_SUB)
arrow((62.5, 23), (73.5, 10.5), C_SUB)

# 底部特性标签
tags = [("单向：只从 Pub → Sub", 12), ("异步：发布不等订阅", 36),
        ("解耦：互不知道对方", 60), ("多对多：N 发 M 收", 84)]
for text, cx in tags:
    t = FancyBboxPatch((cx-10.5, -6.5), 21, 5.4, boxstyle="round,pad=0.4,rounding_size=2.4",
                       fc=C_BOX, ec=C_LINE, lw=1.2)
    ax.add_patch(t)
    ax.text(cx, -3.8, text, ha="center", va="center", fontsize=9.5, color=C_MUTED)

ax.set_ylim(-9, 52)
out = Path(r"D:\Lei_learning\ROS学习\03_核心通信机制\images\topic_pub_sub_model.png")
fig.savefig(out, bbox_inches="tight", facecolor="white")
print("saved:", out)
