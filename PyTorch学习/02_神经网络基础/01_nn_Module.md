# 03 - nn.Module

## 🎯 学习目标
- 理解 nn.Module 的作用与设计思想
- 掌握自定义模型的标准写法
- 熟悉常用层：Linear、Conv2d、激活、Dropout、BN
- 掌握模型参数管理与设备迁移

---

## 📚 核心知识点

### 1. nn.Module 是什么

所有 PyTorch 模型的基类。它帮你自动完成三件事：

1. **参数注册**：`__init__` 里赋值的层/Parameter 会被自动收集
2. **状态管理**：`train()` / `eval()` 切换、`.to(device)` 设备迁移
3. **序列化**：`state_dict()` 保存/加载权重

### 2. 自定义模型的标准模板

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

> **规则**：层在 `__init__` 定义，计算流程在 `forward` 定义。

### 3. 常用层速查

| 层 | 作用 | 关键参数 |
|----|------|----------|
| `nn.Linear(in, out)` | 全连接 y=xWᵀ+b | 输入/输出维度 |
| `nn.Conv2d(in_c, out_c, k)` | 2D 卷积 | stride, padding |
| `nn.MaxPool2d(k)` / `AvgPool2d(k)` | 池化降采样 | kernel_size |
| `nn.ReLU()` / `GELU()` / `Sigmoid()` | 激活函数 | — |
| `nn.Dropout(p)` | 随机置零防过拟合 | p=丢弃概率 |
| `nn.BatchNorm2d(c)` | 批归一化加速收敛 | 通道数 |
| `nn.Embedding(n, d)` | 词嵌入 | 词表大小, 维度 |
| `nn.LSTM(...)` / `nn.TransformerEncoder` | 序列建模 | 见序列模型章 |
| `nn.Flatten()` | 展平 | start_dim |

```python
# 卷积输出尺寸公式（背诵）：
# out = (in + 2*padding - kernel) / stride + 1
nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1)  # 尺寸不变的经典配置
```

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

### 5. 参数管理

```python
model.parameters()          # 迭代所有参数（传给 optimizer）
model.named_parameters()    # 带名字，调试/分组学习率用

# 看模型结构
print(model)
print(sum(p.numel() for p in model.parameters()))       # 总参数量
print(sum(p.numel() for p in model.parameters() if p.requires_grad))  # 可训练参数
```

### 6. train() 与 eval()（重要！）

```python
model.train()   # 训练模式：Dropout 生效、BN 用当前 batch 统计
model.eval()    # 评估模式：Dropout 关闭、BN 用累积统计
```

> 这不是装饰——切换会真实改变 Dropout 和 BatchNorm 的行为。验证前忘写 `eval()` 会导致指标虚低。

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

### 8. 权重初始化

```python
def init_weights(m):
    if isinstance(m, nn.Linear):
        nn.init.kaiming_normal_(m.weight)   # ReLU 系用 He 初始化
        nn.init.zeros_(m.bias)

model.apply(init_weights)   # 递归应用到所有子模块
```

---

## 💻 实战练习

```python
# 写一个两层 MLP 并验证输出形状
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
