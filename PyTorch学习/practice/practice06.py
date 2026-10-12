# -*- coding: utf-8 -*-
"""
practice06 - 数据增强眼见为实
画一张数字 6，用训练流水线随机增强 8 次，拼成九宫格观察效果
运行：python practice06.py  → 生成 augmentation_demo.png
"""
from PIL import Image, ImageDraw, ImageFont
from torchvision import transforms
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ---------- 1. 程序生成测试图：白底黑字的大号"6" ----------
img = Image.new("RGB", (256, 256), "white")
d = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("arial.ttf", 200)
except OSError:
    font = ImageFont.load_default()
d.text((70, 10), "6", fill="black", font=font)

# ---------- 2. 训练用增强流水线（照抄笔记标准配置） ----------
train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224),        # 随机裁剪再缩放到 224
    transforms.RandomHorizontalFlip(p=0.5),   # 50% 概率水平翻转
    transforms.ColorJitter(brightness=0.4, contrast=0.4),  # 颜色扰动
    transforms.RandomRotation(15),            # 随机旋转 ±15°
    transforms.ToTensor(),                    # PIL → Tensor，/255
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])

# ---------- 3. 原图 + 增强 8 次，拼 3×3 九宫格 ----------
fig, axes = plt.subplots(3, 3, figsize=(9, 9))

axes[0][0].imshow(img)
axes[0][0].set_title("原图", fontsize=13)
axes[0][0].axis("off")

flipped = 0
for i, ax in enumerate(axes.flat[1:], start=1):
    aug = train_transform(img)                    # 每次都是全新随机结果
    # 反归一化：把 (x-mean)/std 还原回 0~1 用于显示
    show = aug.permute(1, 2, 0) * 0.5 + 0.5
    show = show.clamp(0, 1)
    ax.imshow(show)
    ax.set_title(f"增强 #{i}", fontsize=11)
    ax.axis("off")
    # 检测这次是否被翻转了（看左上角的钩子朝哪边）
    gray = show.mean(dim=2)
    left_mass = gray[:, :112].sum().item()
    right_mass = gray[:, 112:].sum().item()
    if left_mass < right_mass:                    # 6 的重心跑到右边 = 被翻了
        flipped += 1

fig.suptitle("同一张「6」随机增强 8 次 —— 注意有些已经变成了「9」！",
             fontsize=14, fontweight="bold")
fig.tight_layout()
fig.savefig("augmentation_demo.png", dpi=110, facecolor="white")
print(f"九宫格已保存到 augmentation_demo.png")
print(f"8 次增强中约有 {flipped} 次被水平翻转（6 变成了 9）")

# ---------- 4. 对照实验：验证集风格的确定性变换 ----------
val_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])
a = val_transform(img)
b = val_transform(img)
print(f"验证集变换跑两次，结果完全一致？ {(a == b).all().item()}")
