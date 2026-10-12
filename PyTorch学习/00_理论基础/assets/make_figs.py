# -*- coding: utf-8 -*-
"""为 00_理论基础 02 文档生成两张 PNG：训练流程图 + 交叉熵损失曲线"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np, os

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

OUT = r"D:\Lei_learning\PyTorch学习\00_理论基础\assets"
os.makedirs(OUT, exist_ok=True)

# ---------- 图 1：训练流程全景图 ----------
fig, ax = plt.subplots(figsize=(7.2, 9.2), dpi=160)
ax.set_xlim(0, 10); ax.set_ylim(0, 13); ax.axis("off")

C_MAIN = "#2f6fdd"; C_GRAY = "#6b7280"; C_BG = "#f4f7ff"; C_WARN = "#d97706"

def box(x, y, w, h, title, sub, fc=C_BG, ec=C_MAIN, title_c="#111827"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                                fc=fc, ec=ec, lw=1.6))
    ax.text(x + w/2, y + h*0.62, title, ha="center", va="center",
            fontsize=12.5, fontweight="bold", color=title_c)
    ax.text(x + w/2, y + h*0.26, sub, ha="center", va="center",
            fontsize=9.5, color=C_GRAY)

def arrow(x1, y1, x2, y2, color=C_MAIN, style="-|>", lw=1.8, cs=None):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=16, lw=lw, color=color,
                                 connectionstyle=cs or "arc3,rad=0"))

ax.text(5, 12.55, "神经网络的训练循环（全景图）", ha="center", fontsize=15, fontweight="bold", color="#111827")

box(2.6, 11.1, 4.8, 1.0, "一个神经元：w·x + b（打分）", "PyTorch：nn.Linear")
box(2.6, 9.75, 4.8, 1.0, "叠层 + ReLU（拐弯）", "PyTorch：你的 TinyNet")
box(2.6, 8.4, 4.8, 1.0, "前向：算出预测", "model(x) → logits")
box(2.6, 7.05, 4.8, 1.0, "损失函数：错多少", "连续可导的尺子：CrossEntropyLoss")
box(2.6, 5.7, 4.8, 1.0, "反向传播：每个参数分到责任", "loss.backward()")
box(2.6, 4.35, 4.8, 1.0, "梯度下降：w -= lr·grad", "下山一步：optimizer.step()")

arrow(5, 11.08, 5, 10.80)
arrow(5, 9.73, 5, 9.45)
arrow(5, 8.38, 5, 8.10)
arrow(5, 7.03, 5, 6.75)
arrow(5, 5.68, 5, 5.40)

# 回环：梯度下降 → 前向
arrow(2.5, 4.85, 1.0, 4.85, color=C_GRAY, cs="arc3,rad=0")
arrow(1.0, 4.85, 1.0, 8.9, color=C_GRAY)
arrow(1.0, 8.9, 2.5, 8.9, color=C_GRAY)
ax.text(0.72, 6.9, "mini-batch 循环\n每轮先 zero_grad()", ha="center", va="center",
        fontsize=9, color=C_GRAY, rotation=90)

# 监控框
box(2.2, 2.6, 5.6, 1.15, "监控：train loss ↓ 且 val acc ↑ = 真学会",
    "eval 模式 + torch.no_grad() 做验证", fc="#fff7ed", ec=C_WARN)
arrow(5, 4.33, 5, 3.80, color=C_WARN)

ax.text(5, 1.9, "整条链路只有两件事：算错多少（前向+损失），把错分回去改（反向+下降）",
        ha="center", fontsize=9.5, color=C_GRAY)

fig.savefig(os.path.join(OUT, "training_loop.png"), bbox_inches="tight",
            facecolor="white")
plt.close(fig)

# ---------- 图 2：交叉熵损失曲线 ----------
fig, ax = plt.subplots(figsize=(7.6, 5.6), dpi=160)
p = np.linspace(0.02, 1.0, 500)
loss = -np.log(p)
ax.plot(p, np.minimum(loss, 3.0), color=C_MAIN, lw=2.6, zorder=3)
p2 = np.linspace(0.008, 0.02, 30)
ax.plot(p2, np.minimum(-np.log(p2), 3.05), color=C_MAIN, lw=2, ls=(0, (4, 3)), zorder=3)

ax.set_xlim(0, 1.02); ax.set_ylim(0, 3.1)
ax.set_xticks([0, 0.5, 1]); ax.set_yticks([0, 0.69, 1, 2, 3])
ax.spines[["top", "right"]].set_visible(False)
ax.set_xlabel("p（模型给正确类别的概率）", fontsize=11)
ax.set_ylabel("损失  -log(p)", fontsize=11)
ax.set_title("交叉熵损失曲线：越自信地错，罚得越狠", fontsize=13.5, fontweight="bold", pad=12)
ax.grid(axis="y", color="#ececef", lw=0.8, zorder=0)

ax.annotate("p→0：自信地错，惩罚→∞", xy=(0.045, 3.0), xytext=(0.14, 2.75),
            fontsize=10.5, fontweight="bold", color="#111827",
            arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=1.2))
ax.annotate("p→1：押对且有把握，损失→0", xy=(0.97, 0.03), xytext=(0.22, 0.13),
            fontsize=10.5, fontweight="bold", color="#111827",
            arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=1.2))

# p=0.5 参考点
ax.plot([0.5], [0.69], "o", ms=6, mfc="white", mec=C_GRAY, mew=1.6, zorder=4)
ax.plot([0.5, 0.5], [0, 0.69], "--", color=C_GRAY, lw=1)
ax.plot([0, 0.5], [0.69, 0.69], "--", color=C_GRAY, lw=1)
ax.text(0.47, 0.85, "半信半疑：温和地罚 0.69", ha="right", fontsize=9.5, color=C_GRAY)

# 实验点 p=0.66
lu = -np.log(0.66)
ax.plot([0.66], [lu], "o", ms=8, color=C_MAIN, zorder=5)
ax.plot([0.66], [lu], "o", ms=15, mfc="none", mec=C_MAIN, mew=1, alpha=0.4, zorder=5)
ax.annotate("你的实验点：p=0.66 → 损失≈0.42", xy=(0.66, lu), xytext=(0.70, 1.25),
            fontsize=10, fontweight="bold", color=C_MAIN,
            arrowprops=dict(arrowstyle="->", color=C_MAIN, lw=1.2))

ax.text(0.02, -0.42, "直觉：横轴往右（越自信）曲线越平；往左（自信地错）曲线几乎垂直起飞——所以模型不敢乱押错答案。",
        transform=ax.transData, fontsize=9, color=C_GRAY, clip_on=False)

fig.savefig(os.path.join(OUT, "cross_entropy_curve.png"), bbox_inches="tight",
            facecolor="white")
plt.close(fig)

print("done:", os.listdir(OUT))
