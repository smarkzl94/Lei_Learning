# 11 - MNIST 分类

## 🎯 学习目标
- 端到端跑通第一个完整深度学习项目
- 串联前面所有知识：数据 → 模型 → 训练 → 评估 → 推理
- 掌握训练过程可视化与结果分析

---

## 📚 核心知识点

### 1. 为什么是 MNIST

- 6 万张 28×28 灰度手写数字图，10 类，自动下载
- 5 分钟能训完，是验证"整套流程是否写对"的最佳试验田
- 做通了 MNIST，换任何数据集都只是改 Dataset 和分类数

### 2. 完整代码（可直跑）

```python
import torch
import torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# ===== 1. 配置 =====
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
torch.manual_seed(42)
EPOCHS, BATCH, LR = 5, 64, 1e-3

# ===== 2. 数据 =====
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,)),   # MNIST 官方统计值
])
train_set = datasets.MNIST('./data', train=True,  download=True, transform=transform)
test_set  = datasets.MNIST('./data', train=False, download=True, transform=transform)
train_loader = DataLoader(train_set, BATCH, shuffle=True)
test_loader  = DataLoader(test_set,  BATCH, shuffle=False)

# ===== 3. 模型 =====
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),  # 28→14
            nn.Conv2d(32, 64, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), # 14→7
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 128), nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 10),
        )
    def forward(self, x):
        return self.classifier(self.features(x))

model = Net().to(device)

# ===== 4. 损失 + 优化器 =====
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LR)

# ===== 5. 训练 =====
for epoch in range(EPOCHS):
    model.train()
    total_loss = 0.0
    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        loss = criterion(model(imgs), labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    # ===== 6. 测试 =====
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for imgs, labels in test_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            correct += (model(imgs).argmax(1) == labels).sum().item()
            total += labels.size(0)
    print(f"Epoch {epoch+1}: loss={total_loss/len(train_loader):.4f}, "
          f"test_acc={correct/total:.4f}")

# ===== 7. 保存 =====
torch.save(model.state_dict(), 'mnist_cnn.pth')
```

**预期结果**：1 个 epoch 后 acc > 97%，5 epochs 后 > 99%。达不到说明代码有 bug。

### 3. 逐项对照前面章节

| 代码片段 | 对应章节 |
|----------|----------|
| `datasets.MNIST` + `DataLoader` | 05 Dataset 与 DataLoader |
| `Normalize((0.1307,), (0.3081,))` | 06 数据增强 |
| Conv → ReLU → MaxPool 块 | 07 CNN 基础 |
| `zero_grad → forward → loss → backward → step` | 04 训练流程 |
| `model.eval()` + `no_grad()` | 02 自动求导 |
| `nn.Module` 自定义模型 | 03 nn.Module |

### 4. 训练过程可视化

```python
import matplotlib.pyplot as plt

# 记录每 epoch 的 loss / acc 后画曲线
plt.plot(train_losses, label='train loss')
plt.plot(test_accs, label='test acc')
plt.legend(); plt.xlabel('epoch'); plt.show()
```

**读曲线**：
- train loss 降、test acc 涨 → 正常
- train loss 降、test acc 停涨/反降 → 开始过拟合
- 两者都不动 → lr 太小或模型/数据有问题

### 5. 错误样本分析（进阶习惯）

```python
# 找出所有预测错的样本，肉眼看看长什么样
wrong = []
model.eval()
with torch.no_grad():
    for imgs, labels in test_loader:
        preds = model(imgs.to(device)).argmax(1).cpu()
        mask = preds != labels
        wrong += list(zip(imgs[mask], labels[mask], preds[mask]))
# 显示前 8 张：很多"错"样本人看也难辨认 → 模型已接近数据上限
```

### 6. 单张图推理

```python
from PIL import Image

img = Image.open('my_digit.png').convert('L').resize((28, 28))
x = transform(img).unsqueeze(0).to(device)      # 加 batch 维
model.eval()
with torch.no_grad():
    pred = model(x).argmax(1).item()
print("预测数字:", pred)
```

---

## 💻 实战练习

1. 把 CNN 换成纯 MLP（784→256→10），对比准确率差距（预期 ~98% vs ~99.2%）
2. 尝试 lr=0.1 和 lr=1e-5，观察 loss 曲线有什么不同
3. 只训练 1000 张图，看数据量对精度的影响

## ⚠️ 常见坑

1. 最后一层加了 Softmax 再用 CrossEntropyLoss → 重复（04 章强调过）
2. `transform` 忘传 → 收到 PIL 图像直接进模型报错
3. 推理时忘 `unsqueeze(0)` 加 batch 维 → 形状报错
4. 把 test_loader 设成 `shuffle=True` → 无意义且指标不好对应

---

## 📝 小结

- MNIST 是流程验证器：数据→模型→训练→评估→推理一条龙
- 这套骨架改 Dataset + 改 num_classes 就是任何分类项目
- 学会读 loss/acc 曲线判断训练状态
- 下一步：12 目标检测入门，从"是什么"到"在哪里"
