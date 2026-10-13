# -*- coding: utf-8 -*-
"""
practice07 - 自注意力眼见为实：画出注意力热力图
对应专题 08_Transformer专题/02_QKV与自注意力.md
运行：python practice07_attention.py  → 生成 attention_demo.png

结构：
  SelfAttention    —— 封装三步计算（打分 → softmax → 加权），缩放可开关
  build_toy_words  —— 手工设计的 6 词例句（让注意力结果可读）
  scaling_experiment —— 对照实验：d_k=512 时去掉 /√d_k 会发生什么
  plot_heatmaps    —— 两张热力图并排
  main             —— 串起整个流程
"""
import math  # 只用 sqrt：给注意力分数做 /√d_k 缩放

import torch  # 张量和矩阵运算（@、softmax）
import matplotlib.pyplot as plt  # 画两张热力图

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]  # 让图里的中文不乱码
plt.rcParams["axes.unicode_minus"] = False  # 负号用 ASCII，避免某些字体缺字形


class SelfAttention:
    """单头自注意力的最小实现。演示用恒等变换：Q=K=V=输入本身。"""

    def __init__(self, scale=True):
        # scale=True  → scores / sqrt(d_k)，论文标准做法
        # scale=False → 不缩放，用于对照实验看 softmax 饱和
        self.scale = scale  # 存成成员变量，调用时决定走哪条路

    def __call__(self, x):
        """x: (seq, d_model)。返回 (输出, 注意力权重矩阵)。"""
        # 让实例能像函数一样被调用：attn(x) 就进这里
        d_k = x.size(-1)  # 取最后一维 = 向量维度 d_k，缩放要用它
        scores = x @ x.T  # ① 打分：每对词做点积，得到 (seq, seq) 的相关度矩阵
        if self.scale:
            scores = scores / math.sqrt(d_k)  # 按维度开根号缩小分数，防 softmax 饱和
        weights = scores.softmax(dim=-1)  # ② 归一化：沿最后一维（每个 Query 对所有 Key）
        output = weights @ x  # ③ 加权：按权重混合所有词的向量，(seq, d_model)
        return output, weights  # 输出新表示 + 权重矩阵（权重留着画图/打印）


def build_toy_words():
    """手工设计 6 个词向量，维度语义 ≈ [实体度, 动物度, 动作度, 修饰度]。

    目的：让注意力结果"可读"——「它」和「动物」向量接近，
    点积打分会自动把指代关系抓出来。
    """
    words = ["动物", "没", "过", "马路", "它", "累"]  # 6 个词的例句（打乱了语序也无妨，注意力不看顺序）
    x = torch.tensor([
        [1.0, 0.9, 0.1, 0.0],   # 动物：实体度高、动物度高
        [0.0, 0.1, 0.2, 0.9],   # 没：修饰度高，其他都低
        [0.1, 0.0, 1.0, 0.2],   # 过：动作度高
        [0.9, 0.2, 0.1, 0.1],   # 马路：实体度高但不是动物
        [0.8, 1.0, 0.0, 0.1],   # 它：实体+动物（故意设计得和"动物"很像）
        [0.0, 0.1, 0.9, 0.3],   # 累：偏状态，动作度沾边
    ])
    return words, x  # 词表和对应的 (6, 4) 向量矩阵


def print_attention_matrix(words, weights):
    """把 n×n 权重矩阵打印成对齐的表格。行=谁在看（Query），列=看谁（Key）。"""
    print("注意力矩阵（行=谁在看，列=看谁；每行加起来=1）：")
    print("        " + "  ".join(f"{w:>5}" for w in words))  # 列标题：被看的词
    for i, w in enumerate(words):  # 逐行打印：第 i 个词的注意力分配
        row = "  ".join(f"{weights[i, j]:.2f}" for j in range(len(words)))  # 每格保留两位小数
        print(f"  {w:>4}  {row}")  # 行标题（谁在看）+ 一整行权重


def scaling_experiment(d_k=512, seq=6):
    """对照实验：大维度下缩放 vs 不缩放。

    Q 和 K 用两组独立随机向量，模拟真实打分场景；
    若用同一组向量，自己和自己点积（对角线）必然最大，会把演示搞乱。
    返回 (不缩放的权重, 缩放后的权重)。
    """
    q = torch.randn(seq, d_k)  # 随机 Query：(6, 512)，标准正态
    k = torch.randn(seq, d_k)  # 随机 Key：另一组 (6, 512)，和 q 独立
    scores = q @ k.T  # 点积打分：512 维各分量独立叠加，波动约 ±√512 ≈ ±22
    w_noscale = scores.softmax(dim=-1)  # 不缩放：大分数直接把 softmax 推到饱和区
    w_scaled = (scores / math.sqrt(d_k)).softmax(dim=-1)  # 缩放后：分数回到 ±1 量级，softmax 待在敏感区

    print(f"\nd_k={d_k} 随机向量，分数波动范围 {scores.min():.0f} ~ {scores.max():.0f}：")
    # max(dim=1) 取每行最大权重，mean() 对 6 行求平均 → 一个数概括"有多 one-hot"
    print(f"  不缩放：每行最大权重 {w_noscale.max(dim=1).values.mean():.3f}"
          f"  → 几乎全押一个词（one-hot），梯度≈0")
    print(f"  缩放后：每行最大权重 {w_scaled.max(dim=1).values.mean():.3f}"
          f"  → 注意力仍分散在多个词上，梯度健康")
    return w_noscale, w_scaled  # 不缩放的那份要拿去做右图，缩放的只用来看数字


def _fill_cell_numbers(ax, matrix, threshold=0.5):
    """在热力图每个格子里写上数值，深底用白字、浅底用深字（下划线开头=内部辅助函数）。"""
    n = matrix.shape[0]  # 矩阵边长（词数）
    for i in range(n):  # 行
        for j in range(n):  # 列
            v = matrix[i, j]  # 当前格子的权重值
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",  # 在 (j, i) 居中写两位小数
                    fontsize=9, color="white" if v > threshold else "#333")  # 值大格子深→白字，否则深灰字


def plot_heatmaps(words, w_main, w_bad, save_path="attention_demo.png"):
    """左图：玩具句子的注意力（带缩放）；右图：不缩放的饱和灾难。"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.2), dpi=150)  # 一行两列子图
    n = len(words)  # 词数，设置坐标轴刻度用

    # ---- 左图：正常的注意力矩阵 ----
    ax1.imshow(w_main.numpy(), cmap="Blues", vmin=0, vmax=1)  # 蓝色系，0 白 1 深蓝
    ax1.set_xticks(range(n)); ax1.set_yticks(range(n))  # 每个词一格
    ax1.set_xticklabels(words); ax1.set_yticklabels(words)  # 坐标轴标上词
    ax1.set_xlabel("看谁（Key）"); ax1.set_ylabel("谁在看（Query）")  # 轴语义
    ax1.set_title("注意力热力图（带 /√d_k 缩放）\n「它」→「动物」最亮 = 指代关系",
                  fontsize=12, fontweight="bold")
    _fill_cell_numbers(ax1, w_main)  # 格子里填具体数值

    # ---- 右图：不缩放的饱和对照 ----
    ax2.imshow(w_bad.numpy(), cmap="Reds", vmin=0, vmax=1)  # 红色系，警示"灾难"
    ax2.set_xticks(range(n)); ax2.set_yticks(range(n))
    ax2.set_xticklabels(words); ax2.set_yticklabels(words)
    ax2.set_xlabel("看谁（Key）"); ax2.set_ylabel("谁在看（Query）")
    ax2.set_title("对照：d_k=512 且不缩放 → softmax 饱和\n每行只剩一个亮格，梯度消失",
                  fontsize=12, fontweight="bold")
    _fill_cell_numbers(ax2, w_bad)  # 同样填数值，能看清 1.00 和一片 0.00

    fig.tight_layout()  # 自动调整间距，防标题重叠
    fig.savefig(save_path, bbox_inches="tight", facecolor="white")  # 存图（白底、裁掉多余空白）
    print(f"\n热力图已保存到 {save_path}")


def main():
    torch.manual_seed(42)  # 固定随机种子，对照实验的随机向量每次一样

    # 第一部分：玩具句子跑一遍三步计算，「它」应该最关注「动物」
    words, x = build_toy_words()  # 拿词表和 (6, 4) 向量
    attn = SelfAttention(scale=True)  # 标准模式：带缩放
    output, weights = attn(x)  # 前向：output 是新表示，weights 是 (6, 6) 注意力矩阵
    print_attention_matrix(words, weights)  # 先打印成表，肉眼检查

    it_idx = words.index("它")  # 代词「它」在第几行（这里是 4）
    top = weights[it_idx].argmax().item()  # 「它」这一行权重最大的列下标
    print(f"\n「它」关注最多的是「{words[top]}」（权重 {weights[it_idx, top]:.2f}）"
          f"——指代关系被点积抓到了")

    # 第二部分：大维度对照实验，看 /√d_k 缺席时的 softmax 饱和
    w_noscale, _ = scaling_experiment(d_k=512, seq=len(words))  # 缩放后的结果只打印不用，用 _ 丢掉

    # 画图：可读注意力 vs 饱和灾难，并排对比
    plot_heatmaps(words, weights, w_noscale)


if __name__ == '__main__':
    main()  # 直接运行才执行；被 import 时安静如鸡
