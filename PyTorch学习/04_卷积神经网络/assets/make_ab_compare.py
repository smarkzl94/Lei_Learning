# -*- coding: utf-8 -*-
"""方案A vs 方案B 对比图：验证准确率曲线 + 各类召回率"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, os

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

OUT = r"D:\Lei_learning\PyTorch学习\04_卷积神经网络\assets"
os.makedirs(OUT, exist_ok=True)

acc_a = [0.679, 0.723, 0.733, 0.749, 0.756, 0.739, 0.761, 0.772,
         0.762, 0.751, 0.762, 0.766, 0.762, 0.766, 0.762]
acc_b = [0.722, 0.763, 0.771, 0.783, 0.791]
CLASSES = ['飞机', '汽车', '鸟', '猫', '鹿', '狗', '青蛙', '马', '船', '卡车']
recall_a = [0.79, 0.87, 0.65, 0.64, 0.57, 0.76, 0.89, 0.83, 0.84, 0.85]
recall_b = [0.78, 0.92, 0.72, 0.59, 0.77, 0.76, 0.83, 0.86, 0.88, 0.81]

C_A = "#6b7280"; C_B = "#2f6fdd"

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=150,
                               gridspec_kw={"width_ratios": [1, 1.3]})

# 左：val_acc 曲线
ax1.plot(range(1, 16), acc_a, "o-", color=C_A, lw=2, ms=4,
         label="方案A：冻结主干，只训分类头")
ax1.plot(range(1, 6), acc_b, "s-", color=C_B, lw=2.4, ms=5,
         label="方案B：解冻layer4，分层学习率")
ax1.axhline(0.772, color=C_A, ls="--", lw=1, alpha=0.6)
ax1.axhline(0.791, color=C_B, ls="--", lw=1, alpha=0.6)
ax1.annotate("A 最佳 0.772（第8轮后横盘）", xy=(8, 0.772), xytext=(8.6, 0.72),
             fontsize=9.5, color=C_A,
             arrowprops=dict(arrowstyle="->", color=C_A, lw=1))
ax1.annotate("B 第1轮就 0.722（warm start）", xy=(1, 0.722), xytext=(2.2, 0.665),
             fontsize=9.5, color=C_B,
             arrowprops=dict(arrowstyle="->", color=C_B, lw=1))
ax1.set_xlabel("Epoch"); ax1.set_ylabel("验证准确率")
ax1.set_title("验证准确率曲线", fontsize=13, fontweight="bold")
ax1.set_ylim(0.62, 0.83); ax1.legend(fontsize=9, loc="lower right")
ax1.grid(axis="y", color="#ececef", lw=0.8)
ax1.spines[["top", "right"]].set_visible(False)

# 右：各类召回率对比
x = np.arange(len(CLASSES)); w = 0.38
ax2.bar(x - w/2, recall_a, w, color=C_A, alpha=0.85, label="方案A")
bars = ax2.bar(x + w/2, recall_b, w, color=C_B, alpha=0.9, label="方案B")
for xi, (a, b) in enumerate(zip(recall_a, recall_b)):
    if abs(b - a) >= 0.05:
        ax2.annotate(f"{b-a:+.2f}", (xi + w/2, b + 0.02), ha="center",
                     fontsize=9, fontweight="bold",
                     color="#059669" if b > a else "#dc2626")
ax2.set_xticks(x); ax2.set_xticklabels(CLASSES, fontsize=10)
ax2.set_ylabel("召回率"); ax2.set_ylim(0.4, 1.02)
ax2.set_title("各类召回率：A vs B（鹿 +0.20，猫 -0.05）", fontsize=13, fontweight="bold")
ax2.legend(fontsize=9)
ax2.grid(axis="y", color="#ececef", lw=0.8)
ax2.spines[["top", "right"]].set_visible(False)

fig.suptitle("迁移学习实战：冻结 vs 微调（CIFAR-10 子集 3000 张，ResNet18，CPU）",
             fontsize=14, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(OUT, "transfer_ab_compare.png"),
            bbox_inches="tight", facecolor="white")
print("done")
