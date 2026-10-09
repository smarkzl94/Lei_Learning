# PyTorch 03 章实战练习：nn.Module
# 环境：torch 2.9.1+cpu 已装好，直接运行本文件
# 每个任务先自己写，写不出再看教材 01_nn_Module.md 对应小节
# 结构说明：每个任务一个函数，文件底部用 if __name__ == '__main__' 统一调度
# 运行命令: python practice03.py

import sys
from pathlib import Path

import torch
import torch.nn as nn

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


class MLP(nn.Module):
    """任务 2 的模型，提到模块级供任务 5 复用（类定义不占执行流程）"""

    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 256)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(256, 10)

    def forward(self, x):
        x = x.flatten(1)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        return self.fc2(x)


def task1_linear_box():
    """任务 1：nn.Linear 就是帮你保管参数的盒子"""
    print("=" * 50)
    print("任务 1：nn.Linear 就是帮你保管参数的盒子")
    print("=" * 50)
    # ③ 关键验证：手写 x @ W.T + b 和 layer(x) 对比（为什么 W 要转置？）
    layer = nn.Linear(784, 128)
    print(f"weight.shape: {layer.weight.shape}, bias.shape: {layer.bias.shape}")

    x = torch.randn(64, 784)
    y = layer(x)
    print(f"y.shape: {y.shape}")

    y2 = x @ layer.weight.T + layer.bias
    print(f"y2.shape: {y2.shape}")
    print(torch.allclose(y, y2, atol=1e-5))


def task2_mlp_template():
    """任务 2：按标准模板写一个 MLP"""
    print("=" * 50)
    print("任务 2：按标准模板写一个 MLP")
    print("=" * 50)
    # ③ 口算验证：Linear(784,256) 参数量 = 784*256 + 256，和打印的对不对？
    model = MLP()
    x = torch.randn(32, 1, 28, 28)
    y = model(x)
    print("输出 shape:", y.shape)
    print(model)
    print("参数量:", sum(p.numel() for p in model.parameters()))
    print("Linear(784, 256) 参数量:", 784 * 256 + 256)


def task3_train_eval():
    """任务 3：亲眼看到 train/eval 的行为差异"""
    print("=" * 50)
    print("任务 3：亲眼看到 train/eval 的行为差异")
    print("=" * 50)
    drop_model = nn.Sequential(
        nn.Linear(10, 10),
        nn.Dropout(0.9),
    )
    x = torch.randn(1, 10)

    drop_model.train()
    print("train:")
    for i in range(3):
        print(i, drop_model(x))

    drop_model.eval()
    print("eval:")
    for i in range(3):
        print(i, drop_model(x))


def task4_sequential_vs_custom():
    """任务 4：Sequential vs 自定义 forward"""
    print("=" * 50)
    print("任务 4：Sequential vs 自定义 forward")
    print("=" * 50)
    # ② 去掉 ReLU（纯线性叠加）验证：参数量不变，但表达能力退化为单层线性
    seq_model = nn.Sequential(
        nn.Flatten(start_dim=1),
        nn.Linear(784, 256),
        nn.ReLU(),
        nn.Dropout(0.5),
        nn.Linear(256, 10),
    )
    x = torch.randn(32, 1, 28, 28)
    seq_model.eval()
    y = seq_model(x)
    print("Sequential 输出 shape:", y.shape)
    print("Sequential 参数量:", sum(p.numel() for p in seq_model.parameters()))

    linear_model = nn.Sequential(
        nn.Flatten(start_dim=1),
        nn.Linear(784, 256),
        nn.Dropout(0.5),
        nn.Linear(256, 10),
    )
    linear_model[1].load_state_dict(seq_model[1].state_dict())
    linear_model[3].load_state_dict(seq_model[4].state_dict())
    linear_model.eval()
    y_linear = linear_model(x)
    print("去掉 ReLU 参数量:", sum(p.numel() for p in linear_model.parameters()))
    print("去掉 ReLU 输出 shape:", y_linear.shape)
    print("输出是否相同:", torch.allclose(y, y_linear, atol=1e-5))


def task5_save_load():
    """任务 5：保存与加载权重（state_dict）"""
    print("=" * 50)
    print("任务 5：保存与加载权重（state_dict）")
    print("=" * 50)
    weight_path = Path(__file__).with_name("model.pth")
    m1 = MLP().eval()
    torch.save(m1.state_dict(), weight_path)
    m2 = MLP().eval()
    m2.load_state_dict(torch.load(weight_path, weights_only=True))
    x = torch.randn(32, 1, 28, 28)
    print("加载后输出一致:", torch.allclose(m1(x), m2(x), atol=1e-5))
    print("state_dict 键名:", next(iter(m1.state_dict())))


def main():
    """统一入口：想跑哪个任务就取消哪行的注释（或全跑）"""
    task1_linear_box()
    task2_mlp_template()
    task3_train_eval()
    task4_sequential_vs_custom()
    task5_save_load()


if __name__ == '__main__':
    main()
