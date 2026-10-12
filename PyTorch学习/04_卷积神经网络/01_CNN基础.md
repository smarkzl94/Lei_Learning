# 07 - CNN 基础

## 🎯 学习目标

* 理解卷积、池化的工作原理与直觉

* 掌握卷积输出尺寸计算

* 理解经典 CNN 结构演进：LeNet → AlexNet → VGG → ResNet

* 能用 PyTorch 搭建一个完整 CNN

***

## 🌱 背景：CNN 在知识体系里的位置

先摆正三个容易混淆的概念——它们属于三个不同的分类维度：

| 维度         | 问的是什么  | 例子                                                |
| ---------- | ------ | ------------------------------------------------- |
| **学习范式**   | 反馈从哪来  | 监督学习、无监督学习、强化学习                                   |
| **模型结构**   | 用什么网络学 | **CNN**、RNN、Transformer、MLP（深度学习）；决策树、SVM（经典机器学习） |
| **数据集/任务** | 用什么数据学 | **MNIST**、ImageNet、CIFAR-10                       |

* CNN / RNN 不是和机器学习并列的概念，而是**深度学习内部的网络结构**

* MNIST 不是方法，是**数据集**：7 万张 28×28 手写数字图片，图像分类的"标准练习册"

* 三者可自由组合：用 CNN 在 MNIST 上做监督分类（本章实战）；CNN 提特征 + 强化学习做决策 = DQN 玩 Atari

**CNN 要解决的核心问题**：全连接网络处理图像时参数量爆炸（224×224×3 的图接 64 个神经元就有 963 万参数），且对位置敏感——猫在左上角和右下角要分别学两遍。卷积用"小窗口扫全图 + 权重共享"同时解决这两个问题。

***

## 📚 核心知识点

### 0. 卷积到底在算什么：手算一遍

卷积核 = 一个小的权重格子（如 3×3），在输入图上逐位置滑动，每处做加权求和。以一个经典的**竖边探测核**为例（真实网络里权重是学出来的，这里用人设计的值看原理）：

```
输入图一角（像素值）      卷积核
┌ 10  10  10 ┐          ┌ -1  0  +1 ┐
│ 10  10  80 │     ⊛    │ -1  0  +1 │
└ 10  80  80 ┘          └ -1  0  +1 ┘

输出 = 10×(-1)+10×0+10×(+1)
     + 10×(-1)+10×0+80×(+1)
     + 10×(-1)+80×0+80×(+1)
     = -30 + 170 = 140   ← 特征图此处很亮
```

看核的设计就懂原理：左列乘 -1、右列乘 +1——

* 3×3 区域**左右像素接近**（平坦区）→ 正负抵消，输出 ≈ 0（暗）

* **左暗右亮**（有一道竖边）→ 输出很大（亮）

窗口扫完全图后，输出就是一张"竖边分布图"：**这个核把灰度图变成了特征图**。64 个核就是 64 种探测器各扫一遍，得到 64 张特征图。而"学习"的作用是：这些 -1/0/+1 初始是随机数，靠反向传播自己调整成有用的探测器——第 1 层学边缘，深层学出眼睛、猫脸（对应 01 章的逐层抽象）。

### 1. 为什么用卷积（对比全连接）

| <br /> | 全连接                | 卷积           |
| ------ | ------------------ | ------------ |
| 连接方式   | 每个神经元连所有输入         | 只看局部小窗口（感受野） |
| 参数量    | 爆炸（784→256 就 20 万） | 卷积核共享权重，极小   |
| 平移     | 猫在左上 vs 右下要重新学     | 平移不变性，在哪都能认  |

**直觉**：卷积核 = 特征探测器（边缘、纹理、形状），在图上滑动扫描。

**参数量对比（以 224×224×3 的图为例）**：

```
卷积层 Conv2d(3, 64, k=3)：64 × (3×3×3 + 1) = 1,792
全连接 摊平→64 神经元：    150,528 × 64 + 64  = 9,633,856   ← 差 5376 倍
```

通用公式：`Conv2d 参数量 = out_channels × (kernel² × in_channels + 1)`（+1 是偏置）。**关键性质：卷积参数与图片尺寸无关**——同一套权重扫全图（权重共享），图再大参数也不变；全连接参数则随输入维度直接爆炸。

验证方法：`sum(p.numel() for p in layer.parameters())` 让 PyTorch 自己报数。

### 2. 卷积层 Conv2d

```python
nn.Conv2d(in_channels=3, out_channels=64, kernel_size=3, stride=1, padding=1)
```

* `in_channels`：输入通道（RGB 图 = 3，上一层特征图 = 上一层 out\_channels）

* `out_channels`：卷积核个数 = 输出特征图数量

* `padding=1`：3×3 卷积配 padding=1 尺寸不变（经典搭配）

**输出尺寸公式（必背）**：

```
out = floor((in + 2×padding − kernel) / stride) + 1
```

| 输入      | 配置            | 输出              |
| ------- | ------------- | --------------- |
| 224×224 | k=3, s=1, p=1 | **224×224**（不变） |
| 224×224 | k=3, s=2, p=1 | 112×112（减半）     |
| 224×224 | k=7, s=2, p=3 | 112×112         |

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

| 网络           | 年份   | 核心贡献                           | <br />                                                                                                                          | <br /> | <br /> |
| ------------ | ---- | ------------------------------ | :------------------------------------------------------------------------------------------------------------------------------ | :----- | :----- |
| LeNet-5      | 1998 | 第一个实用 CNN                      | **特征图 28×28 经过 `MaxPool2d(2)` 后多大？如果换成 `MaxPool2d(kernel_size=3, stride=2)`（核比步长大，窗口会重叠）又是多大？再想想：窗口重叠意味着什么？**（第二问套公式算，第三问是开放思考） |        | （手写数字） |
| AlexNet      | 2012 | ReLU + Dropout + GPU 训练，引爆深度学习 | <br />                                                                                                                          | <br /> | <br /> |
| VGG          | 2014 | 全部用 3×3 小卷积堆深度                 | <br />                                                                                                                          | <br /> | <br /> |
| ResNet       | 2015 | **残差连接**解决梯度消失，可训 152 层        | <br />                                                                                                                          | <br /> | <br /> |
| EfficientNet | 2019 | 深度/宽度/分辨率联合缩放                  | <br />                                                                                                                          | <br /> | <br /> |

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

***

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

***

## 📝 小结

* 卷积 = 共享权重的局部特征探测；Conv→BN→ReLU 是标准块

* 尺寸公式 `out=(in+2p−k)/s+1`，3×3/p=1 尺寸不变

* 残差连接 `out + x` 让深层网络可训练

* 下一步：08 图像分类实战，用迁移学习快速拿下分类任务

