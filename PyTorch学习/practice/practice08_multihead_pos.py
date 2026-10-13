# -*- coding: utf-8 -*-
"""
practice08 - 多头注意力与位置编码：两个实验
对应专题 08_Transformer专题/03_多头注意力与位置编码.md
运行：python practice08_multihead_pos.py  → 生成 multihead_demo.png

实验一：8 个头的注意力热力图排一排，看"不同头不同眼光"
实验二："人咬狗" vs "狗咬人"——不加位置编码输出完全一样，加了就区分开
"""
import math  # sqrt 和正弦位置编码都要用

import torch  # 张量运算
from torch import nn  # MultiheadAttention
import matplotlib.pyplot as plt  # 画 8 个头的热力图

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]  # 中文不乱码
plt.rcParams["axes.unicode_minus"] = False  # 负号正常显示


def sinusoidal_pe(seq_len, d_model):
    """正弦位置编码（2017 原版论文）。返回 (seq_len, d_model)。"""
    pe = torch.zeros(seq_len, d_model)  # 每个位置一行向量
    pos = torch.arange(seq_len).unsqueeze(1).float()  # 位置编号 0..seq-1，列向量
    div = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
    # div 是各维的频率系数：低维频率高（秒针），高维频率低（时针）
    pe[:, 0::2] = torch.sin(pos * div)  # 偶数维用 sin
    pe[:, 1::2] = torch.cos(pos * div)  # 奇数维用 cos
    return pe


def experiment_multihead(words, d_model=64, num_heads=8):
    """实验一：随机初始化的 8 头注意力，各头模式已经肉眼不同。"""
    torch.manual_seed(42)  # 固定种子，每次结果一致
    mha = nn.MultiheadAttention(embed_dim=d_model, num_heads=num_heads,
                                batch_first=True)  # batch 在第 0 维
    x = torch.randn(1, len(words), d_model)  # (batch=1, seq=6, 64) 随机词向量
    # average_attn_weights=False：不要平均，把每个头的矩阵单独还给我们
    _, attn = mha(x, x, x, need_weights=True, average_attn_weights=False)
    return attn[0]  # (8头, 6, 6)，去掉 batch 维


def experiment_word_order():
    """实验二：打乱词序，自注意力（无位置编码）输出不变；加位置编码后区分开。"""
    # 手工词向量（4 维，随意但互不相同）
    emb = {
        "人": torch.tensor([1.0, 0.0, 0.5, 0.2]),
        "咬": torch.tensor([0.0, 1.0, 0.3, 0.8]),
        "狗": torch.tensor([0.8, 0.1, 1.0, 0.0]),
    }
    seq_a = torch.stack([emb["人"], emb["咬"], emb["狗"]])  # 人咬狗
    seq_b = torch.stack([emb["狗"], emb["咬"], emb["人"]])  # 狗咬人（同样的词，顺序相反）

    def attend(x):
        # 单头自注意力（恒等 Q=K=V，带缩放），返回每个词的新表示
        w = (x @ x.T / math.sqrt(x.size(-1))).softmax(dim=-1)  # 打分+归一化
        return w @ x  # 加权混合

    out_a, out_b = attend(seq_a), attend(seq_b)  # 不加位置编码，各算一遍
    # "人"在 A 里是第 0 位，在 B 里是第 2 位
    same = torch.allclose(out_a[0], out_b[2], atol=1e-6)
    print(f"不加位置编码：「人」在两句里的输出相同？ {same}  ← 词序完全被忽略")

    pe = sinusoidal_pe(3, 4)  # 3 个位置的编码，4 维
    out_a2 = attend(seq_a + pe)  # 加了位置编码再算
    out_b2 = attend(seq_b + pe)
    diff = (out_a2[0] - out_b2[2]).abs().max().item()  # 两处「人」的输出差异
    print(f"加了位置编码：「人」在两处的输出最大差异 = {diff:.3f}  ← 词序进模型了")
    return pe


def plot_heads(words, attn, save_path="multihead_demo.png"):
    """把 8 个头的注意力矩阵画成 2×4 小图墙。"""
    fig, axes = plt.subplots(2, 4, figsize=(13, 6.5), dpi=140)
    n = len(words)
    for h, ax in enumerate(axes.flat):  # 逐个头画一张
        m = attn[h].detach().numpy()  # 第 h 个头的 (6, 6) 矩阵
        ax.imshow(m, cmap="Blues", vmin=0, vmax=m.max())  # 各自归一，突出各头模式
        ax.set_xticks(range(n)); ax.set_yticks(range(n))
        ax.set_xticklabels(words, fontsize=8); ax.set_yticklabels(words, fontsize=8)
        ax.set_title(f"头 {h + 1}", fontsize=11, fontweight="bold")
    fig.suptitle("8 个注意力头：同样的输入，8 种关注模式（随机初始化，训练后会分化出分工）",
                 fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])  # 给总标题留位置
    fig.savefig(save_path, bbox_inches="tight", facecolor="white")
    print(f"8 头热力图已保存到 {save_path}")


def main():
    words = ["动物", "没", "过", "马路", "它", "累"]  # 复用 02 篇的玩具句

    print("=== 实验一：多头注意力 ===")
    attn = experiment_multihead(words)
    print(f"8 个头的注意力矩阵形状：{tuple(attn.shape)}（头数, seq, seq）")
    # 看各头"专注度"差异：每头每行最大权重的平均值，越接近 1 越专注
    focus = attn.max(dim=-1).values.mean(dim=-1)  # (8,)
    for h, f in enumerate(focus):
        print(f"  头 {h + 1}: 平均最大权重 {f:.2f}"
              + ("（很专注，盯少数词）" if f > 0.5 else "（较分散，广撒网）"))

    print("\n=== 实验二：词序实验 ===")
    experiment_word_order()

    plot_heads(words, attn)


if __name__ == '__main__':
    main()  # 直接运行才执行
