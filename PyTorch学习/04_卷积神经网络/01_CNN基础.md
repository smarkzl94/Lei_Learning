# 07 - CNN 基础

## 🎯 学习目标
- 理解卷积、池化的工作原理与直觉
- 掌握卷积输出尺寸计算
- 理解经典 CNN 结构演进：LeNet → AlexNet → VGG → ResNet
- 能用 PyTorch 搭建一个完整 CNN

---

## 📚 核心知识点

### 1. 为什么用卷积（对比全连接）

| | 全连接 | 卷积 |
|---|--------|------|
| 连接方式 | 每个神经元连所有输入 | 只看局部小窗口（感受野） |
| 参数量 | 爆炸（784→256 就 20 万） | 卷积核共享权重，极小 |
| 平移 | 猫在左上 vs 右下要重新学 | 平移不变性，在哪都能认 |

**直觉**：卷积核 = 特征探测器（边缘、纹理、形状），在图上滑动扫描。

### 2. 卷积层 Conv2d

```python
nn.Conv2d(in_channels=3, out_channels=64, kernel_size=3, stride=1, padding=1)
```

- `in_channels`：输入通道（RGB 图 = 3，上一层特征图 = 上一层 out_channels）
- `out_channels`：卷积核个数 = 输出特征图数量
- `padding=1`：3×3 卷积配 padding=1 尺寸不变（经典搭配）

**输出尺寸公式（必背）**：

```
out = floor((in + 2×padding − kernel) / stride) + 1
```

| 输入 | 配置 | 输出 |
|------|------|------|
| 224×224 | k=3, s=1, p=1 | **224×224**（不变） |
| 224×224 | k=3, s=2, p=1 | 112×112（减半） |
| 224×224 | k=7, s=2, p=3 | 112×112 |

### 3. 池化 Pooling

```python
nn.MaxPool2d(kernel_size=2, stride=2)   # 尺寸减半，取最大值（最常用）
nn.AdaptiveAvgPool2d((1, 1))            # 不管输入多大 → 1×1（分类头标配）
```

作用：降尺寸、扩感受野、增强平移鲁棒性。现代网络常用 stride=2 卷积替代池化。

### 4. 标准卷积块（现代模板）

```python
block = nn.Sequential(
    nn.Conv2d(in_c, out_c, 3, padding=1, bias=False),  # 接 BN 时 bias 多余
    nn.BatchNorm2d(out_c),     # 稳定训练、加速收敛
    nn.ReLU(inplace=True),
)
```

> 顺序：**Conv → BN → ReLU**。BN 让训练对初始化不敏感，可以放心用大学习率。

### 5. 经典网络演进（面试高频）

| 网络 | 年份 | 核心贡献 |
|------|------|----------|
| LeNet-5 | 1998 | 第一个实用 CNN（手写数字） |
| AlexNet | 2012 | ReLU + Dropout + GPU 训练，引爆深度学习 |
| VGG | 2014 | 全部用 3×3 小卷积堆深度 |
| ResNet | 2015 | **残差连接**解决梯度消失，可训 152 层 |
| EfficientNet | 2019 | 深度/宽度/分辨率联合缩放 |

**ResNet 残差块（最重要）**：

```python
class ResBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, 3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, 3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        identity = x                        # 捷径
        out = torch.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        return torch.relu(out + identity)   # ← 核心：加上输入
```

为什么有效：梯度可以沿 `identity` 捷径直接回传，深层网络不再梯度消失。

### 6. 完整 CNN 示例

```python
class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),  # 224→112
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), # 112→56
            nn.Conv2d(64, 128, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),# 56→28
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),   # (B,128,1,1)，任何输入尺寸都能接
            nn.Flatten(),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))
```

**设计套路**：特征提取部分通道数翻倍(32→64→128)、尺寸减半(池化)；分类头用 AdaptiveAvgPool + Linear。

### 7. 特征图尺寸流转（手算练习）

输入 `(1, 3, 224, 224)` 经过上面的 SimpleCNN：

```
(1,3,224,224) → conv+pool → (1,32,112,112)
              → conv+pool → (1,64,56,56)
              → conv+pool → (1,128,28,28)
              → AdaptiveAvgPool → (1,128,1,1)
              → flatten → (1,128) → Linear → (1,10)
```

---

## 💻 实战练习

```python
# 验证输出尺寸公式
x = torch.randn(1, 3, 224, 224)
conv = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3)
print(conv(x).shape)   # (1, 64, 112, 112) ← (224+6-7)/2+1=112

model = SimpleCNN()
print(model(x).shape)  # (1, 10)
```

## ⚠️ 常见坑

1. 通道数接不上：下一层 `in_channels` 必须等于上一层 `out_channels`
2. 池化太多把特征图缩到 0×0 → AdaptiveAvgPool 可避免
3. 忘了 BN 后 Conv 可以关 `bias=False`（不报错但浪费）
4. 小数据集从头训练深网络 → 过拟合，应迁移学习（见 08 章）

---

## 📝 小结

- 卷积 = 共享权重的局部特征探测；Conv→BN→ReLU 是标准块
- 尺寸公式 `out=(in+2p−k)/s+1`，3×3/p=1 尺寸不变
- 残差连接 `out + x` 让深层网络可训练
- 下一步：08 图像分类实战，用迁移学习快速拿下分类任务
