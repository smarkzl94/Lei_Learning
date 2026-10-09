# PyTorch 01 章实战练习：张量与运算
# 环境：torch 2.9.1+cpu 已装好，直接运行本文件
# 每个任务先自己写，写不出再看教材 01_张量与运算.md 对应小节
# 结构说明：每个任务一个函数，文件底部用 if __name__ == '__main__' 统一调度
# 运行命令: python practice01.py

import sys

import numpy as np
import torch

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def task1_shape_ops():
    """任务 1：张量创建与形状变换"""
    print("=" * 50)
    print("任务 1：张量创建与形状变换")
    print("=" * 50)
    # 创建一个 (4, 3, 32, 32) 的随机张量 x（模拟一批 4 张 3 通道 32x32 图片）
    # 然后依次打印：
    #   ① flatten 成 (4, 3072)
    #   ② permute 成 NHWC 格式 (4, 32, 32, 3)
    #   ③ 用 -1 让 torch 自动推断：reshape 成 (12, 32, 32)
    x = torch.randn(4, 3, 32, 32)
    flat = x.flatten(1)
    nhwc = x.permute(0, 2, 3, 1)
    auto = x.reshape(12, 32, 32)
    print("原 shape:", x.shape)
    print("flatten:", flat.shape)
    print("permute:", nhwc.shape)
    print("reshape:", auto.shape)


def task2_linear_layer():
    """任务 2：手写线性层正向传播 y = xW + b"""
    print("=" * 50)
    print("任务 2：手写线性层正向传播 y = xW + b")
    print("=" * 50)
    # 输入 batch=64 个 784 维向量，隐层 128 维
    # 算出 y，打印 shape，并确认是 (64, 128)
    x = torch.randn(64, 784)
    W = torch.randn(784, 128)
    b = torch.randn(128)
    y = x @ W + b
    print("y shape:", y.shape)


def task3_argmax():
    """任务 3：模拟分类预测的 argmax"""
    print("=" * 50)
    print("任务 3：模拟分类预测的 argmax")
    print("=" * 50)
    # logits 是 (8, 10)：8 个样本，10 个类别的"打分"
    # ① 找出每个样本得分最高的类别索引（argmax, dim=1）→ shape (8,)
    # ② 找出每个样本的最高分是多少（max 返回两个值，看教材或 help）
    logits = torch.tensor([
        [0.1, 2.0, 0.3, -1.0, 0.0, 0.5, 0.2, 0.8, 0.9, 0.4],
        [1.0, 0.1, 3.0,  0.2, 0.0, 0.1, 0.3, 0.2, 0.5, 0.7],
    ])
    logits = torch.cat([logits, torch.randn(6, 10)], dim=0)
    classes = logits.argmax(dim=1)
    scores, indices = logits.max(dim=1)
    print("argmax:", classes.shape, classes)
    print("max scores:", scores)
    print("max indices:", indices)


def task4_bool_mask():
    """任务 4：布尔掩码——数正数"""
    print("=" * 50)
    print("任务 4：布尔掩码——数正数")
    print("=" * 50)
    # x = torch.randn(1000)，不手写循环，统计有多少个元素 > 0
    # （提示：布尔掩码 + sum）
    x = torch.randn(1000)
    print("x > 0 的元素个数:", int((x > 0).sum()))


def task5_numpy_share():
    """任务 5：NumPy 互转的共享内存坑"""
    print("=" * 50)
    print("任务 5：NumPy 互转的共享内存坑")
    print("=" * 50)
    # ① 建 numpy 数组 a = [1,2,3]，转张量 t，修改 t[0]=99，打印 a——观察 a 变没变
    # ② 重新来：这次转之前 .copy() 出独立副本，再验证修改互不影响
    a = np.array([1, 2, 3])
    t = torch.from_numpy(a)
    t[0] = 99
    print("共享内存 a:", a)
    print("共享内存 t:", t)

    a = np.array([1, 2, 3])
    t = torch.from_numpy(a.copy())
    t[0] = 99
    print("独立副本 a:", a)
    print("独立副本 t:", t)


def main():
    """统一入口：想跑哪个任务就取消哪行的注释（或全跑）"""
    task1_shape_ops()
    task2_linear_layer()
    task3_argmax()
    task4_bool_mask()
    task5_numpy_share()


if __name__ == '__main__':
    main()
