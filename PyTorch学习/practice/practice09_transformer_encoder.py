# -*- coding: utf-8 -*-
"""
practice09 - 用 nn.TransformerEncoder 搭一个真正的序列分类器
对应专题 08_Transformer专题/04_完整架构拆解.md
运行：python practice09_transformer_encoder.py

做三件事：
1. 搭模型：Embedding + 正弦位置编码 + TransformerEncoder + 分类头
2. 数参数：拆出注意力 vs FFN，验证"FFN 约占 2/3"
3. 真训练：在一个合成小任务上跑几轮，看 loss 下降、准确率上升

合成任务规则：一句话里"信号词"（编号 1）比"干扰词"（编号 2）多 → 标签 1，否则 0。
"""
import math  # 正弦位置编码要用 sqrt / sin / cos

import torch  # 张量运算
from torch import nn  # 神经网络零件
from torch.utils.data import DataLoader, TensorDataset  # 批次加载

torch.manual_seed(42)  # 固定随机种子，结果可复现


class SinusoidalPE(nn.Module):
    """正弦位置编码（2017 原版）：把"第几个位置"编码成向量，加到词向量上。"""

    def __init__(self, d_model, max_len=512):
        super().__init__()
        pe = torch.zeros(max_len, d_model)  # 每个位置一行向量
        pos = torch.arange(max_len).unsqueeze(1).float()  # 位置编号 0..max_len-1，列向量
        div = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        # div 是各维频率系数：低维频率高（秒针），高维频率低（时针）
        pe[:, 0::2] = torch.sin(pos * div)  # 偶数维用 sin
        pe[:, 1::2] = torch.cos(pos * div)  # 奇数维用 cos
        self.register_buffer("pe", pe)  # 不是参数，不参与训练，但要跟着模型走

    def forward(self, x):
        # x: (batch, seq, d_model) → 给每个位置加上对应的位置向量
        return x + self.pe[: x.size(1)]


class TransformerClassifier(nn.Module):
    """整条流水线：词索引 → 词向量+位置编码 → TransformerEncoder → 整句表示 → 二分类。"""

    def __init__(self, vocab_size, num_classes, d_model=128, nhead=4,
                 dim_ff=512, num_layers=2, max_len=512):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)  # 词索引 → 词向量
        self.pos_encoder = SinusoidalPE(d_model, max_len)  # 注入词序信息
        # 一个 encoder block：多头注意力 + Add&Norm + FFN + Add&Norm 全封装在里面
        layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead,
            dim_feedforward=dim_ff,  # FFN 中间维，惯例 4 倍
            dropout=0.1,
            batch_first=True,  # ⚠️ 不设的话默认 (seq, batch, d)，维度错位不报错！
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=num_layers)  # 堆 num_layers 层
        self.head = nn.Linear(d_model, num_classes)  # 整句表示 → 各类得分

    def forward(self, tokens):
        # tokens: (batch, seq) 词索引
        x = self.embedding(tokens)  # → (batch, seq, d_model)
        x = self.pos_encoder(x)  # 加位置编码，形状不变
        x = self.encoder(x)  # → (batch, seq, d_model)，形状依然不变（这就是能无限堆叠的原因）
        x = x.mean(dim=1)  # 整句表示：序列维取平均（BERT 用 [CLS]，玩具任务取平均就够）
        return self.head(x)  # → (batch, num_classes)


def make_synthetic_data(n_samples, seq_len, vocab_size, signal=1, noise=2):
    """造合成数据：信号词比干扰词多 → 标签 1，否则 0。规则简单、确定可学。"""
    tokens = torch.randint(3, vocab_size, (n_samples, seq_len))  # 背景词（3 号以上，无意义）
    labels = torch.randint(0, 2, (n_samples,))  # 先随机定标签
    for i in range(n_samples):
        n_signal = torch.randint(0, seq_len // 2 + 1, (1,)).item()  # 本句信号词个数
        n_noise = seq_len // 2 - n_signal  # 干扰词个数，两者总和固定
        pos = torch.randperm(seq_len)[: n_signal + n_noise]  # 随机选插入位置
        tokens[i, pos[:n_signal]] = signal  # 放信号词
        tokens[i, pos[n_signal:]] = noise  # 放干扰词
        labels[i] = 1 if n_signal > n_noise else 0  # 按规则重打标签
    return tokens, labels


def count_params(model):
    """数参数：把 encoder 每一层拆成 注意力 vs FFN，验证 FFN 约占 2/3。"""
    print("=" * 56)
    print("参数量明细（每个 encoder layer 内部）")
    print("=" * 56)
    layer = model.encoder.layers[0]  # 取第一层拆开看（各层结构相同）
    groups = {
        "注意力 in_proj（Q/K/V 一体）": layer.self_attn.in_proj_weight,
        "注意力 out_proj（O 投影）": layer.self_attn.out_proj.weight,
        "FFN linear1（扩张 4 倍）": layer.linear1.weight,
        "FFN linear2（压回）": layer.linear2.weight,
    }
    attn_total, ffn_total = 0, 0
    for name, w in groups.items():
        n = w.numel()  # 权重元素个数（不含 bias）
        print(f"  {name:<28} {tuple(w.shape)!s:<18} {n:>9,}")
        if "FFN" in name:
            ffn_total += n
        else:
            attn_total += n
    share = ffn_total / (ffn_total + attn_total)
    print("-" * 56)
    print(f"  FFN 合计 {ffn_total:,} vs 注意力合计 {attn_total:,}"
          f"  →  FFN 占比 {share:.1%}（理论值 2/3 ≈ 66.7%）")
    total = sum(p.numel() for p in model.parameters())
    print(f"  全模型总参数：{total:,}（含 embedding、LayerNorm、分类头）")
    print("=" * 56)


def train_one_epoch(model, loader, optimizer, loss_fn):
    """训练一轮，返回平均 loss 和准确率。"""
    model.train()  # 开启 dropout
    total_loss, correct, n = 0.0, 0, 0
    for tokens, labels in loader:
        logits = model(tokens)  # 前向：算各类得分
        loss = loss_fn(logits, labels)  # 错多少
        optimizer.zero_grad()  # 清空旧梯度
        loss.backward()  # 反向传播：每个参数分到自己的责任
        optimizer.step()  # 梯度下降：下山一步
        total_loss += loss.item() * len(labels)  # 按样本数加权累计
        correct += (logits.argmax(dim=1) == labels).sum().item()  # 猜对几个
        n += len(labels)
    return total_loss / n, correct / n


def evaluate(model, loader):
    """在没见过的数据上验证，不更新参数。"""
    model.eval()  # 关掉 dropout
    correct, n = 0, 0
    with torch.no_grad():  # 验证不需要梯度，省内存
        for tokens, labels in loader:
            correct += (model(tokens).argmax(dim=1) == labels).sum().item()
            n += len(labels)
    return correct / n


def main():
    # ---- 超参数 ----
    vocab_size, seq_len, num_classes = 50, 16, 2  # 词表、句长、二分类
    d_model, nhead, dim_ff, num_layers = 128, 4, 512, 2  # 模型尺寸
    batch_size, epochs, lr = 64, 5, 1e-3  # 训练配置

    # ---- 数据 ----
    train_x, train_y = make_synthetic_data(2000, seq_len, vocab_size)  # 训练集 2000 条
    val_x, val_y = make_synthetic_data(400, seq_len, vocab_size)  # 验证集 400 条
    train_loader = DataLoader(TensorDataset(train_x, train_y), batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(TensorDataset(val_x, val_y), batch_size=batch_size)

    # ---- 模型 ----
    model = TransformerClassifier(vocab_size, num_classes, d_model, nhead, dim_ff, num_layers)
    count_params(model)  # 先验证 FFN 占 2/3

    # 前向形状走一遍，对照专题 04 的数据流图
    sample = train_x[:2]  # 取 2 条看形状
    print(f"\n形状流：输入 {tuple(sample.shape)} (batch, seq)")
    h = model.embedding(sample)
    print(f"  embedding 后 {tuple(h.shape)} (batch, seq, d_model)")
    h = model.encoder(model.pos_encoder(h))
    print(f"  encoder 后 {tuple(h.shape)} ← 形状不变，可无限堆叠")
    print(f"  分类头输出 {tuple(model(sample).shape)} (batch, num_classes)\n")

    # ---- 训练 ----
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)  # Adam 优化器
    loss_fn = nn.CrossEntropyLoss()  # 交叉熵：分类任务的标准尺子
    for epoch in range(1, epochs + 1):
        train_loss, train_acc = train_one_epoch(model, train_loader, optimizer, loss_fn)
        val_acc = evaluate(model, val_loader)
        print(f"epoch {epoch}: train_loss={train_loss:.4f}  "
              f"train_acc={train_acc:.3f}  val_acc={val_acc:.3f}")


if __name__ == "__main__":
    main()  # 直接运行才执行；被 import 时安静如鸡
