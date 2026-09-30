# 03 - nn.Module

## 🎯 学习目标
- 理解 nn.Module 的作用与设计思想
- 掌握自定义模型的标准写法
- 熟悉常用层：Linear、Conv2d、激活、Dropout、BN
- 掌握模型参数管理与设备迁移

---

## 🧱 第 0 课：零基础补课（层是什么，nn.Module 帮你管什么）

### 0.1 层 = 帮你"保管参数"的盒子

回忆第 02 章：模型 = 公式结构 + 一堆要训练的参数（W、b）。手写训练循环时你是这么管的：

```python
W = torch.randn(784, 128, requires_grad=True)   # 自己造参数
b = torch.randn(128, requires_grad=True)
y = x @ W + b                                  # 自己写公式
```

一个"线性层"无非就是这两件事：**持有一组 W、b，做 y = xW + b 这个运算。**

但当模型有几十层、上百万参数时，手写会疯掉。于是 PyTorch 把每层封装成一个**盒子**：

```python
layer = nn.Linear(784, 128)   # 盒子自己创建好 W(128,784) 和 b(128)，都带 requires_grad=True
y = layer(x)                  # 盒子替你做 x@W.T + b
```

- W、b 不用你造，盒子内部自动创建、自动开录音
- `nn.Linear` 里**唯一需要你给的是形状**（输入 784、输出 128），参数值它随机初始化
- 每调用一次盒子，就完成一次线性变换

**所以 nn.Linear 就是你在 practice01 任务 2 手写的 `x @ W + b` 的"官方封装版"。**你已经在 01 章亲手实现过神经网络的核心运算，这层窗户纸现在捅破。

### 0.2 nn.Module = 盒子的收纳箱

盒子多了又出现新问题：参数散落在各层里，怎么统一管理（喂给 optimizer、搬去 GPU、存盘）？

**nn.Module 就是"收纳箱"**：你把盒子装进去，它自动登记所有盒子的所有参数。装进去的方式极其简单——在 `__init__` 里 `self.xxx = 层`，收纳箱自动看见。

### 0.3 激活函数：给模型加入"非线性"

如果模型只是线性层一层层叠：`y = xW₁+b₁` 再 `W₂+b₂`……数学上可以证明，**多层线性叠加等价于一层线性**——叠多少层都白叠，表达能力没增加。

激活函数（如 ReLU）就是夹在层之间的"非线性调料"：

```
x → [Linear] → z → [ReLU] → a → [Linear] → 输出
                ↑ 把负数掐成 0，正数原样通过
```

有了它，模型才能拟合弯曲的、复杂的边界（比如"图片是猫还是狗"这种非线性问题）。**没有激活函数，再深的网络也只是一个线性回归。**

### 0.4 本节只需要记住三句话

1. 层 = 保管参数的盒子，`nn.Linear` 帮你造参数、做运算
2. `nn.Module` = 收纳箱，`self.xxx = 层` 就完成登记
3. 激活函数 = 非线性调料，没有它叠多少层都白搭

---

## 📚 核心知识点

### 1. nn.Module 是什么

所有 PyTorch 模型的基类。它帮你自动完成三件事：

1. **参数注册**：`__init__` 里赋值的层/Parameter 会被自动收集（`model.parameters()` 全拿得到）
2. **状态管理**：`train()` / `eval()` 切换、`.to(device)` 设备迁移（一次性搬运所有参数）
3. **序列化**：`state_dict()` 保存/加载权重

### 2. 自定义模型的标准模板 ⭐

```python
import torch
import torch.nn as nn

class MyModel(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()              # ← 必须！否则参数无法注册
        self.fc1 = nn.Linear(784, 256)  # 在 __init__ 里定义层
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):               # 前向逻辑写在这里
        x = x.flatten(1)
        x = self.dropout(self.relu(self.fc1(x)))
        return self.fc2(x)

model = MyModel()
output = model(input)   # 直接调用实例 → 自动走 forward，不要写 model.forward(input)
```

**模板就三条规则：**

| 规则 | 原因 |
|---|---|
| `super().__init__()` 第一行必须写 | 不写的话收纳箱的登记机制没启动，参数全部丢失 |
| 层在 `__init__` 里定义 | 收纳箱只在初始化时扫描 `self.xxx`，之后才定义就登记不上 |
| 计算流程写在 `forward` | 每次调用 `model(x)` 都会执行 forward，同一组参数可反复用 |

**为什么写 `model(x)` 而不是 `model.forward(x)`？** 直接调用实例会走 PyTorch 的 `__call__`，它在调 forward 之前还要做一些内务（调用 hook、处理动态图等）。直接调 forward 会跳过这些——功能上多数时候没区别，但属于坏习惯，统一写 `model(x)`。

### 3. 常用层速查

| 层 | 作用 | 关键参数 |
|----|------|----------|
| `nn.Linear(in, out)` | 全连接 y=xWᵀ+b | 输入/输出维度 |
| `nn.Conv2d(in_c, out_c, k)` | 2D 卷积 | stride, padding |
| `nn.MaxPool2d(k)` / `AvgPool2d(k)` | 池化降采样（把 k×k 区域压成 1 个值） | kernel_size |
| `nn.ReLU()` / `GELU()` / `Sigmoid()` | 激活函数（非线性调料） | — |
| `nn.Dropout(p)` | 随机置零防过拟合 | p=丢弃概率 |
| `nn.BatchNorm2d(c)` | 批归一化加速收敛 | 通道数 |
| `nn.Embedding(n, d)` | 词嵌入（查表得到词的向量） | 词表大小, 维度 |
| `nn.LSTM(...)` / `nn.TransformerEncoder` | 序列建模 | 见序列模型章 |
| `nn.Flatten()` | 展平 | start_dim |

```python
# 卷积输出尺寸公式（背诵）：
# out = (in + 2*padding - kernel) / stride + 1
nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1)  # 尺寸不变的经典配置
```

**Dropout 是什么？** 训练时随机把一部分神经元的输出**掐成 0**（按概率 p），迫使模型不能过度依赖某几个神经元，从而防止"死记硬背训练集"（过拟合）。评估时自动关闭。

**BatchNorm 是什么？** 把每批数据的分布拉回到均值 0、方差 1 附近，让训练更稳定更快。具体原理先不用管，见到认识就行。

### 4. 容器：Sequential 与 ModuleList

```python
# 简单直线模型：Sequential 最省事
model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Dropout(0.5),
    nn.Linear(256, 10),
)

# 有分支/跳跃连接（ResNet 那种）：必须写自定义 forward
class ResBlock(nn.Module):
    def forward(self, x):
        return x + self.conv_path(x)     # 残差相加，Sequential 做不到

# 层数不固定：ModuleList（普通的 Python list 不会注册参数！）
self.layers = nn.ModuleList([nn.Linear(256, 256) for _ in range(n)])
```

**为什么普通 list 不行？** 回顾 0.2：收纳箱靠"扫描 `self.xxx`"登记参数，它只认自己的容器（ModuleList/ModuleDict）。你把层塞进 Python 原生 list，收纳箱看不见，optimizer 拿不到这些参数——它们就永远得不到训练。

### 5. 参数管理

```python
model.parameters()          # 迭代所有参数（传给 optimizer）
model.named_parameters()    # 带名字，调试/分组学习率用

# 看模型结构
print(model)
print(sum(p.numel() for p in model.parameters()))       # 总参数量
print(sum(p.numel() for p in model.parameters() if p.requires_grad))  # 可训练参数
```

**参数量估算小知识**：`nn.Linear(in, out)` 的参数 = in×out + out（权重 + 偏置）。比如 Linear(784, 256) = 784×256 + 256 = 200,960 个。面试问"你的模型多大"，口算就能答。

### 6. train() 与 eval()（重要！）

```python
model.train()   # 训练模式：Dropout 生效、BN 用当前 batch 统计
model.eval()    # 评估模式：Dropout 关闭、BN 用累积统计
```

> 这不是装饰——切换会真实改变 Dropout 和 BatchNorm 的行为。验证前忘写 `eval()` 会导致指标虚低。

**为什么 Dropout 评估时要关闭？** 想像考试：平时练习时老师随机抽掉一些条件（Dropout）逼你学扎实；真考试（验证）时当然要把条件全给你，否则成绩必然偏低。

### 7. 设备迁移与保存加载

```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = model.to(device)          # 整个模型上 GPU
# 注意：数据也要 .to(device)，两边必须一致

# 保存（推荐只存权重）
torch.save(model.state_dict(), 'model.pth')

# 加载
model = MyModel()
model.load_state_dict(torch.load('model.pth', map_location=device))
model.eval()
```

**state_dict 是什么？** 一个有序字典：`{参数名: 参数值}`。只存权重不存结构——所以加载时要先 `MyModel()` 造一个同结构的空模型，再把权重灌进去。这样存出来的文件小，且跨设备加载灵活。

### 8. 权重初始化

```python
def init_weights(m):
    if isinstance(m, nn.Linear):
        nn.init.kaiming_normal_(m.weight)   # ReLU 系用 He 初始化
        nn.init.zeros_(m.bias)

model.apply(init_weights)   # 递归应用到所有子模块
```

**为什么要专门初始化？** 回忆 `randn` 造的是标准正态（方差 1）。若每层的输出方差被不断放大，深层的值会爆炸；太小又会消失。好的初始化让信号平稳流动——`kaiming_normal_` 就是为 ReLU 设计的方差校准。平时用默认初始化即可，这招在特殊场景才用。

---

## 💻 实战练习

练习文件：`D:\DemoPy\practice\practice03.py`（5 个任务）

```python
# 核心练习：写一个两层 MLP 并验证输出形状
class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(784, 256), nn.ReLU(),
            nn.Linear(256, 64),  nn.ReLU(),
            nn.Linear(64, 10),
        )
    def forward(self, x):
        return self.net(x.flatten(1))

m = MLP()
x = torch.randn(32, 1, 28, 28)
assert m(x).shape == (32, 10)   # batch=32, 10 类
print("参数量:", sum(p.numel() for p in m.parameters()))
```

## ⚠️ 常见坑

1. 忘写 `super().__init__()` → 参数没注册，`parameters()` 是空的
2. 用 Python 普通 list 存层 → 参数不注册，必须用 `nn.ModuleList`
3. `model.forward(x)` 直接调用 → 跳过 hook，应该写 `model(x)`
4. 验证忘 `model.eval()` → Dropout 还在随机丢弃，指标不准

---

## 📝 小结

- `__init__` 定义层、`forward` 定义流程、`super().__init__()` 不能少
- 直线结构用 `Sequential`，有分支就自定义 `forward`
- 训练/验证切换 `train()/eval()`，迁移设备用 `.to(device)`
- 下一步：04 训练流程，把模型、数据、损失、优化器串成完整循环
