# ============================================================
# PyTorch 01-04 章 · 代码版复习（可直接运行）
# 运行命令: python review01_04.py
# 用法：从上往下读，每个 PART 对应一章；想看哪段就跳到哪个函数
# ============================================================
import sys

import torch
import torch.nn as nn
import torch.optim as optim

# Code Runner 的输出面板按 UTF-8 解码；Windows 默认是 GBK，不改中文会乱码
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


# ============================================================
# PART 1：张量与运算
# 一句话：张量就是多维数组，核心问题永远是「形状对不对」
# ============================================================
def part1_tensor():
    print(f"\n{'=' * 55}\nPART 1：张量与运算\n{'=' * 55}")

    # --- 创建：嵌套几层 [] 就是几维 ---
    a = torch.tensor([[1, 2], [3, 4]])      # 2 维，shape (2,2)
    b = torch.randn(2, 3)                   # 0 附近随机 → 权重初始化用它
    c = torch.zeros(2, 3)                   # 全 0 占位
    print("a =", a.tolist(), "| shape:", tuple(a.shape))

    # --- 形状操作：图像永远 NCHW ---
    x = torch.randn(4, 3, 32, 32)           # 假装一批 4 张 3 通道 32x32 图片
    flat = x.flatten(1)                     # (4, 3, 32, 32) → (4, 3072)，喂全连接层前必做
    one = torch.randn(3, 32, 32).unsqueeze(0)  # 单张图 (3,32,32) → (1,3,32,32)，假装成 batch
    print("flatten:", tuple(x.shape), "->", tuple(flat.shape))
    print("unsqueeze: (3,32,32) ->", tuple(one.shape))

    # --- 运算：* 逐元素，@ 矩阵乘（最大的坑）---
    m1 = torch.tensor([[1., 2.], [3., 4.]])
    m2 = torch.tensor([[5., 6.], [7., 8.]])
    print("逐元素 * :", (m1 * m2).tolist())     # 对应位置相乘
    print("矩阵乘 @ :", (m1 @ m2).tolist())     # 神经网络主力（y = xW + b）

    # --- 聚合：dim=k 的意思是"把第 k 维压掉" ---
    scores = torch.tensor([[0.1, 0.7, 0.2],    # 2 个样本，各 3 类打分
                           [0.8, 0.1, 0.1]])
    pred = scores.argmax(dim=1)                # 每个样本分数最高的类别 → [1, 0]
    print("argmax 预测类别:", pred.tolist())

    # --- 广播：从右往左对齐，缺失当 1，是 1 就能撑 ---
    data = torch.randn(4, 3)
    bias = torch.randn(3)                      # (3,) 自动复制成 (4,3) 再加
    print("广播结果 shape:", tuple((data + bias).shape), "← 线性层加偏置就是这么做的")


# ============================================================
# PART 2：自动求导
# 一句话：requires_grad 开录音 → 前向建图 → backward 把梯度写进 .grad
# ============================================================
def part2_autograd():
    print(f"\n{'=' * 55}\nPART 2：自动求导\n{'=' * 55}")

    # --- 最小例子：y = x² + 3x，dy/dx = 2x + 3，x=2 时应为 7 ---
    x = torch.tensor(2.0, requires_grad=True)  # 开"录音"（只有浮点能开）
    y = x ** 2 + 3 * x                         # 前向：每个运算都被录下
    y.backward()                               # 反传：梯度写入 x.grad
    print("x=2 时 dy/dx =", x.grad.item(), "（手算 2x+3 = 7 ✓）")

    # --- 梯度累积：不清零就会翻倍（训练五步第一步的由来）---
    x = torch.tensor(1.0, requires_grad=True)
    (x ** 2).backward()
    print("第 1 次 backward:", x.grad.item())  # 2.0
    (x ** 2).backward()                        # 没清零！
    print("第 2 次 backward:", x.grad.item())  # 4.0 ← 翻倍了！
    x.grad.zero_()                             # 清零恢复正常
    (x ** 2).backward()
    print("清零后再算:", x.grad.item())        # 2.0

    # --- no_grad：验证/测试必包，不建图省内存 ---
    with torch.no_grad():
        z = x ** 2                             # 这次不录音
    print("no_grad 里 requires_grad =", z.requires_grad)  # False

    # --- loss.item()：记录数值必用，取纯 Python 数 ---
    loss = torch.tensor(3.14)
    print("loss.item() =", loss.item(), type(loss.item()))


# ============================================================
# PART 3：nn.Module
# 一句话：层是保管参数的盒子，Module 是收纳箱，self.xxx 自动登记
# ============================================================
class TinyNet(nn.Module):
    """标准模板三条铁律：
    1. super().__init__() 必须第一行（不写参数全丢）
    2. 层在 __init__ 定义（收纳箱只在初始化时扫描 self.xxx）
    3. 计算流程写在 forward（model(x) 自动调用，别写 model.forward(x)）
    """

    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(2, 8)   # 参数量 = 2×8 + 8 = 24（in×out + out）
        self.relu = nn.ReLU()        # 激活函数：没有它叠多少层都等价一层
        self.fc2 = nn.Linear(8, 2)   # 参数量 = 8×2 + 2 = 18

    def forward(self, x):
        return self.fc2(self.relu(self.fc1(x)))


def part3_module():
    print(f"\n{'=' * 55}\nPART 3：nn.Module\n{'=' * 55}")

    model = TinyNet()
    total = sum(p.numel() for p in model.parameters())
    print("参数总数:", total, "（24 + 18 = 42 ✓，收纳箱自动登记的）")

    x = torch.randn(5, 2)            # 5 个样本，每个 2 维
    out = model(x)                   # 自动调 forward，输出 (5, 2)
    print("输入", tuple(x.shape), "-> 输出", tuple(out.shape))

    # train/eval 切换：影响 Dropout/BN 的行为，纯 Linear 无感
    model.eval()
    # 存权重：只存 state_dict（有序字典），不存结构
    print("state_dict 的键:", list(model.state_dict().keys()))


# ============================================================
# PART 4：训练流程
# 一句话：五步循环 = 清梯度 → 前向 → 损失 → 反传 → 更新
# ============================================================
def part4_training():
    print(f"\n{'=' * 55}\nPART 4：训练流程（完整闭环）\n{'=' * 55}")

    # --- 造数据：两类点，一条直线能分开 ---
    torch.manual_seed(42)                    # 固定随机种子，每次生成同一批点
    X = torch.randn(200, 2)                  # 200 个点，每个点 2 个坐标，分布在 0 附近
    y = (X[:, 0] + X[:, 1] > 0).long()       # x+y>0 记为 1 类，否则 0 类；标签必须是 long！

    # --- 组装机器：模型 + 阅卷老师 + 机械手 ---
    model = nn.Linear(2, 2)                  # 模型：2 个坐标 → 2 个类别的得分
    criterion = nn.CrossEntropyLoss()        # 阅卷老师：内部已含 softmax，别手动加！
    optimizer = optim.AdamW(model.parameters(), lr=0.05)  # 机械手：按学习率 0.05 更新参数

    # --- 训练：五步循环（背下来）---
    for epoch in range(1, 51):
        optimizer.zero_grad()                # 1. 清梯度（防累积）
        output = model(X)                    # 2. 前向：做题
        loss = criterion(output, y)          # 3. 损失：对答案
        loss.backward()                      # 4. 反传：错题归因
        optimizer.step()                     # 5. 更新：调参数
        if epoch % 25 == 0:
            print(f"epoch {epoch:3d} | train loss = {loss.item():.4f}")

    # --- 验证：eval() + no_grad()，只做题不学习 ---
    torch.manual_seed(123)                   # 换种子 = 模型没见过的新数据
    X_test = torch.randn(100, 2)
    y_test = (X_test[:, 0] + X_test[:, 1] > 0).long()
    model.eval()
    with torch.no_grad():
        acc = (model(X_test).argmax(dim=1) == y_test).float().mean().item()
    print(f"测试集准确率: {acc:.2%}")

    # --- 学习率对比（今天实测的反直觉结论）---
    # 二次损失 (w*3-9)²：lr=0.05 收敛，lr=0.2 爆炸（稳定边界 lr < 2/曲率）
    print("\n学习率对比（二次损失，曲率 18，生死线 lr≈0.11）：")
    for lr in (0.05, 0.2):
        w = torch.tensor([1.0], requires_grad=True)
        opt = optim.SGD([w], lr=lr)
        hist = []
        for _ in range(5):
            opt.zero_grad()
            loss = (w * 3 - 9) ** 2
            loss.backward()
            opt.step()
            hist.append(f"{loss.item():.1f}")
        print(f"  lr={lr}: {' -> '.join(hist)}")


if __name__ == '__main__':
    part1_tensor()
    part2_autograd()
    part3_module()
    part4_training()
    print(f"\n{'=' * 55}\n全部复习完毕 ✓  下一步：05 Dataset 与 DataLoader\n{'=' * 55}")
