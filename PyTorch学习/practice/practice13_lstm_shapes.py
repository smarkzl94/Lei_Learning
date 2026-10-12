"""
practice13 - RNN/LSTM 维度体操：文本分类器的形状验证
对应文档 05_序列模型/01_RNN与LSTM.md
用随机索引走一遍 Embedding → BiLSTM → 拼接 → Linear，
逐行打印形状，把每个维度变化看清楚
运行：python practice13_lstm_shapes.py
"""
import torch
from torch import nn

torch.manual_seed(42)
VOCAB, EMBED, HIDDEN, NUM_CLASSES = 5000, 128, 256, 2


class TextClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, hidden=256, num_classes=2):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden, batch_first=True,
                            num_layers=2, bidirectional=True, dropout=0.5)
        self.fc = nn.Linear(hidden * 2, num_classes)  # 双向所以 ×2

    def forward(self, x, verbose=False):
        if verbose: print(f"输入词索引:        {tuple(x.shape)}  (batch, seq)")
        x = self.embedding(x)
        if verbose: print(f"Embedding 后:      {tuple(x.shape)}  每个词查表成 128 维向量")
        output, (h_n, c_n) = self.lstm(x)
        if verbose:
            print(f"LSTM output:       {tuple(output.shape)}  每步的记忆（双向 256×2）")
            print(f"LSTM h_n:          {tuple(h_n.shape)}  (层数×方向, batch, hidden)")
            print(f"LSTM c_n:          {tuple(c_n.shape)}  细胞状态，分类不用它")
        h = torch.cat([h_n[-2], h_n[-1]], dim=1)  # 最后一层的正向+反向
        if verbose: print(f"拼接正反向:        {tuple(h.shape)}  256+256=512")
        out = self.fc(h)
        if verbose: print(f"Linear 分类头:     {tuple(out.shape)}  2 个类别的得分")
        return out


model = TextClassifier(VOCAB, EMBED, HIDDEN, NUM_CLASSES)
model.eval()  # dropout 关掉，形状演示更干净

# 8 条评论，每条 20 个词（随机索引，只看形状不看语义）
x = torch.randint(1, VOCAB, (8, 20))
x[:, 15:] = 0  # 模拟真实场景：后 5 个位置是 padding（索引 0）

print("=" * 55)
with torch.no_grad():
    out = model(x, verbose=True)
print("=" * 55)

# 参数量统计：感受 Embedding 查找表有多大
total = sum(p.numel() for p in model.parameters())
emb = sum(p.numel() for p in model.embedding.parameters())
print(f"\n总参数 {total/1e6:.2f}M，其中 Embedding 表 {emb/1e6:.2f}M"
      f"（{VOCAB}×{EMBED} = {VOCAB*EMBED}，词表越大表越大）")

# 双向 forget ×2 验证：如果把 fc 写成 hidden 而不 ×2 会怎样
try:
    bad_fc = nn.Linear(HIDDEN, NUM_CLASSES)
    bad_fc(torch.cat([torch.randn(4, HIDDEN), torch.randn(4, HIDDEN)], dim=1))
except RuntimeError as e:
    print(f"\n常见坑验证：fc 忘记 ×2 会报错 → {e}")
