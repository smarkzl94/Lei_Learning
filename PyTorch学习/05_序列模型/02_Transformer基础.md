# 10 - Transformer 基础

## 🎯 学习目标
- 理解注意力机制的核心思想与 Q/K/V 计算
- 理解多头注意力、位置编码的作用
- 掌握 Transformer 编码器的整体结构
- 能用 nn.TransformerEncoder 搭建分类模型

---

## 📚 核心知识点

### 1. 注意力机制：一句话版本

> 每个词（token）都去问所有词："你对我有多重要？" 然后按重要性加权汇总信息。

对比 RNN：信息不再逐步传递，**任意两个词直接交互**，长距离依赖一步到位，且所有时间步并行计算（GPU 友好）。

### 2. Self-Attention 的计算（必懂）

给每个 token 生成三个向量：

- **Q (Query)**：我要找什么
- **K (Key)**：我是什么（供别人匹配）
- **V (Value)**：我的实际内容

```
scores = Q·Kᵀ / √d_k        # 相关性打分（缩放防止梯度过小）
weights = softmax(scores)    # 归一化成注意力权重
output = weights · V         # 加权求和
```

```python
def self_attention(x):                     # x: (batch, seq, d_model)
    Q = W_q(x); K = W_k(x); V = W_v(x)
    scores = Q @ K.transpose(-2, -1) / math.sqrt(Q.size(-1))
    weights = scores.softmax(dim=-1)       # (batch, seq, seq) 注意力矩阵
    return weights @ V                     # (batch, seq, d_model)
```

PyTorch 一行版：`F.scaled_dot_product_attention(Q, K, V)`（自动走高效内核）。

### 3. 多头注意力（Multi-Head）

把 d_model 切成 h 份，每个头独立做注意力，再拼接：

- 不同头关注不同关系（语法、指代、位置…）
- `nn.MultiheadAttention(embed_dim=512, num_heads=8, batch_first=True)`
- 要求 `embed_dim % num_heads == 0`

### 4. 位置编码：注意力不知道顺序

Self-attention 本身对词序无感（打乱输入输出一样），必须注入位置信息：

```python
# 正弦位置编码（原版论文）
pe[:, 0::2] = sin(pos / 10000^(2i/d))
pe[:, 1::2] = cos(pos / 10000^(2i/d))

# 现代做法：可学习位置嵌入
self.pos_embed = nn.Embedding(max_len, d_model)
x = self.token_embed(x) + self.pos_embed(positions)
```

### 5. Transformer 编码器层结构

```
输入 x
  ├─→ Multi-Head Attention → +x (残差) → LayerNorm ─┐
  │                                                  │
  └─→ FFN(Linear→GELU→Linear) → + (残差) → LayerNorm → 输出
```

两个要点：
1. **残差连接**：每条支路都把输入加回来（和 ResNet 同理）
2. **LayerNorm**（不是 BatchNorm）：对单个样本的特征维度归一化，适合变长序列

```python
# PyTorch 现成实现
encoder_layer = nn.TransformerEncoderLayer(
    d_model=512, nhead=8, dim_feedforward=2048,
    dropout=0.1, batch_first=True,
)
encoder = nn.TransformerEncoder(encoder_layer, num_layers=6)
```

### 6. 文本分类示例

```python
class TransformerClassifier(nn.Module):
    def __init__(self, vocab_size, d_model=256, num_classes=2, max_len=512):
        super().__init__()
        self.token_emb = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.pos_emb = nn.Embedding(max_len, d_model)
        layer = nn.TransformerEncoderLayer(d_model, nhead=8,
                                           dim_feedforward=1024,
                                           batch_first=True)
        self.encoder = nn.TransformerEncoder(layer, num_layers=3)
        self.fc = nn.Linear(d_model, num_classes)

    def forward(self, x):                    # (batch, seq)
        pos = torch.arange(x.size(1), device=x.device)
        h = self.token_emb(x) + self.pos_emb(pos)
        h = self.encoder(h)                  # (batch, seq, d_model)
        return self.fc(h.mean(dim=1))        # 平均池化取句向量
```

### 7. 编码器 vs 解码器

| 结构 | 特点 | 代表 | 用途 |
|------|------|------|------|
| Encoder-only | 双向看全文 | BERT, ViT | 分类、理解 |
| Decoder-only | 带因果掩码，只看左边 | GPT 系列 | 文本生成 |
| Encoder-Decoder | 两者组合 | 原始 Transformer, T5 | 翻译、摘要 |

因果掩码：`nn.Transformer.generate_square_subsequent_mask(seq_len)`，上三角置 -∞，阻止"偷看未来"。

### 8. 视觉中的 Transformer（ViT）

把图像切成 16×16 的 patch，每个 patch 线性投影成一个 token，后面就是标准编码器。说明注意力机制是**通用**的序列建模工具，不限于文本。

---

## 💻 实战练习

```python
# 验证注意力矩阵的形状与含义
x = torch.randn(2, 10, 64)          # batch=2, 10个token, 64维
mha = nn.MultiheadAttention(64, num_heads=8, batch_first=True)
out, attn = mha(x, x, x, need_weights=True)
print(out.shape)    # (2, 10, 64)
print(attn.shape)   # (2, 10, 10) ← 每个词对每个词的注意力权重
```

## ⚠️ 常见坑

1. `d_model` 不能被 `num_heads` 整除 → 直接报错
2. 忘加位置编码 → 模型对词序无感，效果诡异
3. 生成任务忘加因果掩码 → 训练时偷看答案，推理时崩
4. 序列太长：注意力复杂度 O(L²)，长文本要截断或用高效变体

---

## 📝 小结

- 注意力 = Q·Kᵀ 打分 → softmax → 加权 V；并行、直接建模长依赖
- 多头 + 位置编码 + 残差 + LayerNorm = Transformer 编码器
- 分类用 Encoder，生成用 Decoder（带因果掩码）
- 下一步：11 MNIST 分类，一个端到端的完整小项目
