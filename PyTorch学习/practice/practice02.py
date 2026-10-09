# PyTorch 02 章实战练习：自动求导
# 环境：torch 2.9.1+cpu 已装好，直接运行本文件
# 每个任务先自己写，写不出再看教材 02_自动求导.md 对应小节
# 结构说明：每个任务一个函数，文件底部用 if __name__ == '__main__' 统一调度
# 运行命令: python practice02.py

import sys

import torch

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def task1_first_backward():
    """任务 1：体验一次完整的反向传播"""
    print("=" * 50)
    print("任务 1：体验一次完整的反向传播")
    print("=" * 50)
    # ① x = 2.0（开录音），y = x² + 3x，backward 后验证 grad 是不是 7
    # ② 改 x = 5.0 重新来一遍，验证 grad 是不是 13
    x = torch.tensor(2.0, requires_grad=True)
    y = x**2 + 3*x
    y.backward()
    print("x.grad:", x.grad)
    x = torch.tensor(5.0, requires_grad=True)
    y = x**2 + 3*x
    y.backward()
    print("x.grad:", x.grad)


def task2_grad_accumulate():
    """任务 2：亲眼见证梯度累积的坑"""
    print("=" * 50)
    print("任务 2：亲眼见证梯度累积的坑")
    print("=" * 50)
    # 第一次 backward 后 x.grad 是多少？第二次呢？是不是翻倍了？
    x = torch.tensor(1.0, requires_grad=True)
    y = x ** 2
    y.backward()
    print("x.grad:", x.grad)
    y = x ** 2
    y.backward()
    print("x.grad:", x.grad)
    x.grad.zero_()
    y = x ** 2
    y.backward()
    print("x.grad:", x.grad)


def task3_manual_descent():
    """任务 3：手动梯度下降，让 w 自己走向 3"""
    print("=" * 50)
    print("任务 3：手动梯度下降，让 w 自己走向 3")
    print("=" * 50)
    # 不用任何 optimizer，手写训练循环：
    #   w 初始 1.0，loss = (w*3 - 9)²，学习率 0.1，迭代 20 轮
    w = torch.tensor([1.0], requires_grad=True)
    lr = 0.1
    for _ in range(20):
        if w.grad is not None:
            w.grad.zero_()
        loss = (w * 3 - 9) ** 2
        loss.backward()
        with torch.no_grad():
            w -= lr * w.grad
    print("w:", w.item())


def task4_no_grad_scope():
    """任务 4：no_grad 的作用域实验"""
    print("=" * 50)
    print("任务 4：no_grad 的作用域实验")
    print("=" * 50)
    # ① 在 torch.no_grad() 里面算 y1 = x * x，y1.requires_grad 是 True 还是 False？
    # ② 在 no_grad 外面算 y2 = x * x，这次呢？
    x = torch.tensor(2.0, requires_grad=True)
    with torch.no_grad():
        y1 = x * x
        print("y1.requires_grad:", y1.requires_grad)
    y2 = x * x
    print("y2.requires_grad:", y2.requires_grad)


def task5_detach():
    """任务 5：detach 拆出分身"""
    print("=" * 50)
    print("任务 5：detach 拆出分身")
    print("=" * 50)
    # 已验证的结论（2026-09-30 纠错后）：
    # ① y.backward() 正常，x.grad = 4（dy/dx = 2x，x=2）
    # ② z = y.detach() 后：z.requires_grad = False，z.backward() 会报错（分身没录音）
    # ③ detach 不影响原图！y 再 backward 报错的真正原因是"同一图被 backward 两次，
    #    图已释放"（见教材第 6 节），要重复 backward 需 retain_graph=True
    x = torch.tensor(2.0, requires_grad=True)
    y = x * x
    y.backward()
    print("x.grad:", x.grad)
    # z = y.detach()
    # z.backward()
    # print("x.grad:", x.grad)
    # print("z.requires_grad:", z.requires_grad)
    # y.backward()
    # print("x.grad:", x.grad)


def main():
    """统一入口：想跑哪个任务就取消哪行的注释（或全跑）"""
    task1_first_backward()
    task2_grad_accumulate()
    task3_manual_descent()
    task4_no_grad_scope()
    task5_detach()


if __name__ == '__main__':
    main()
