# 09 - RNN 与 LSTM

## 🎯 学习目标
- 理解序列数据的特点与 RNN 的循环结构
- 理解 RNN 的梯度消失问题与 LSTM 的门控解法
- 掌握 nn.LSTM / nn.Embedding 的用法
- 能搭建一个文本分类模型

---

## 📚 核心知识点

### 1. 什么是序列数据

时间步之间有依赖关系的数据：文本（词序）、语音、股价、机器人关节轨迹。普通全连接/CNN 没有"记忆"，无法建模依赖。

### 2. RNN 的循环结构

```
x₁ → [RNN] → h₁
x₂ → [RNN] → h₂     同一组权重在每个时间步复用
x₃ → [RNN] → h₃
            ↑
       h₂ 传进来（记忆）
```

每个时间步：`h_t = tanh(W_x·x_t + W_h·h_{t-1} + b)`

- **权重共享**：处理任意长度的序列
- **致命伤**：长序列反向传播时梯度连乘 → **梯度消失/爆炸**，记不住早期信息

### 3. LSTM：用门控保护记忆

LSTM 增加了一条**细胞状态 c**（信息高速公路）和三个门：

| 门 | 作用 | 直觉 |
|----|------|------|
| 遗忘门 f | 决定旧记忆丢多少 | "之前的信息还重要吗" |
| 输入门 i | 决定新信息存多少 | "当前输入值得记吗" |
| 输出门 o | 决定记忆暴露多少 | "现在该输出什么" |

门 = sigmoid(线性变换) → 0~1 的开关系数，逐元素相乘控制信息流动。梯度可以沿细胞状态"加法通道"长距离回传，缓解消失。

> GRU 是 LSTM 的简化版（两个门），参数更少，效果接近，工程中常用。

### 4. PyTorch 中的 LSTM

```python
lstm = nn.LSTM(
    input_size=128,      # 每个时间步输入的维度（词向量维度）
    hidden_size=256,     # 隐藏状态维度（记忆容量）
    num_layers=2,        # 堆叠层数
    batch_first=True,    # ← 必加！输入变 (batch, seq, feature)
    bidirectional=True,  # 双向：同时看前文和后文
    dropout=0.5,         # 层间 dropout
)

output, (h_n, c_n) = lstm(x)
# output: (batch, seq_len, 256*2)  每个时间步的隐藏状态
# h_n:    (num_layers*2, batch, 256)  最后一步的隐藏状态（分类用它）
```

### 5. 文本分类完整示例

```python
class TextClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, hidden=256, num_classes=2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden, batch_first=True,
                            num_layers=2, bidirectional=True, dropout=0.5)
        self.fc = nn.Linear(hidden * 2, num_classes)   # 双向所以要 ×2

    def forward(self, x):                     # x: (batch, seq_len) 词索引
        x = self.embedding(x)                 # (batch, seq_len, 128)
        _, (h_n, _) = self.lstm(x)            # h_n: (4, batch, 256)
        h = torch.cat([h_n[-2], h_n[-1]], dim=1)  # 拼接最后一层正反向
        return self.fc(h)                     # (batch, num_classes)
```

### 6. Embedding：词的向量化

```python
nn.Embedding(vocab_size=10000, embedding_dim=128, padding_idx=0)
```

- 本质是一个 `(10000, 128)` 的查找表，把词索引映射成稠密向量
- `padding_idx=0`：让 0 号（padding 位）向量不参与梯度更新
- 变长序列配合 `pad_sequence` 补齐（见 05 章 collate_fn）

### 7. 训练序列模型的特殊技巧

```python
# ① 梯度裁剪（RNN 必备，防爆）
loss.backward()
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
optimizer.step()

# ② pack_padded_sequence：让 LSTM 跳过 padding 部分（进阶）
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
packed = pack_padded_sequence(emb, lengths.cpu(), batch_first=True, enforce_sorted=False)
out, _ = lstm(packed)
out, _ = pad_packed_sequence(out, batch_first=True)
```

### 8. RNN 的现状

- 文本领域已被 Transformer 全面取代（见 10 章）
- 但 LSTM 在**小数据、边缘设备、实时控制**（如机器人传感器序列）仍有价值
- 学习它是为了理解"记忆与门控"思想，这是理解 GRU/注意力/状态空间模型的台阶

---

## 💻 实战练习

```python
# 用随机数据验证维度流转
model = TextClassifier(vocab_size=5000)
x = torch.randint(0, 5000, (8, 20))    # batch=8, 每条 20 个词
out = model(x)
print(out.shape)   # (8, 2)
```

## ⚠️ 常见坑

1. 忘 `batch_first=True` → 维度全错（默认 seq 在第 0 维）
2. 双向 LSTM 最后 fc 忘 ×2 → 维度不匹配
3. 训练 RNN 不做梯度裁剪 → loss 突然 NaN
4. 变长序列不处理 padding → 模型把 0 填充当真实数据学

---

## 📝 小结

- RNN 权重共享、按时间步循环，但有梯度消失问题
- LSTM 用遗忘/输入/输出三门保护细胞状态，实现长记忆
- `nn.Embedding` 查表 + `nn.LSTM(batch_first=True)` 是文本分类标配
- 下一步：10 Transformer 基础，注意力机制如何取代循环结构
