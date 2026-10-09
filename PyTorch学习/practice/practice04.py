# PyTorch 04 章实战练习：训练流程
# 环境：torch 2.9.1+cpu 已装好，直接运行本文件
# 本章是把 01-03 章零件组装成完整训练机器，每个任务都在加深"五步循环"
# 结构说明：每个任务一个函数，文件底部用 if __name__ == '__main__' 统一调度
# 运行命令: python practice04.py

import sys

import torch
import torch.nn as nn
import torch.optim as optim

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def task1_optimizer():
    """任务 1：用 optimizer 替代手写更新（复刻 practice02 任务 3）"""
    print(f"{'=' * 50}\n任务 1：用 optimizer 替代手写更新\n{'=' * 50}")
    # 用 optim.SGD 重写那个循环（20 轮，loss=(w*3-9)²，lr=0.1）
    # 体会：zero_grad / backward / step 三步分别对应什么
    # 你的代码：
    w = torch.tensor([1.0], requires_grad=True)  # 要更新的参数，初始值为 1
    optimizer = optim.SGD([w], lr=0.1)  # 用 SGD 代替手写的 w -= lr * grad
    for _ in range(20):
        optimizer.zero_grad()  # 清掉上一轮累积的梯度
        loss = (w * 3 - 9) ** 2  # 目标是让 w 接近 3，此时 loss 为 0
        loss.backward()  # 把 d(loss)/dw 写入 w.grad
        optimizer.step()  # 按学习率更新 w
    print("optimizer w:", w.item())


def task1_manual():
    """任务 1 对照：不用 optimizer，手写同样的更新。"""
    print(f"{'=' * 50}\n任务 1 对照：手写更新\n{'=' * 50}")
    w = torch.tensor([1.0], requires_grad=True)
    lr = 0.1
    for _ in range(20):
        if w.grad is not None:
            w.grad.zero_()  # 对应 optimizer.zero_grad()
        loss = (w * 3 - 9) ** 2
        loss.backward()  # 对应 loss.backward()，结果仍在 w.grad
        with torch.no_grad():
            w -= lr * w.grad  # 对应 optimizer.step()
    print("手写 w:", w.item())


def task2_crossentropy():
    """任务 2：认识阅卷老师 CrossEntropyLoss"""
    print(f"{'=' * 50}\n任务 2：认识阅卷老师 CrossEntropyLoss\n{'=' * 50}")
    # ① 造 logits = torch.tensor([[2.0, 1.0, 0.1]]), 标签 label = torch.tensor([0])
    #   用 CrossEntropyLoss 算 loss——预测对了吗？loss 大不大？
    # ② 换一个说错了的答案（label=2），loss 变大还是变小？
    # ③ 关键细节：label 必须是 long 类型（用 torch.tensor([0]) 默认就是），
    #   试试传成 float（torch.tensor([0.0])）会怎样？
    # 你的代码：
    logits = torch.tensor([[2.0, 1.0, 0.1]])  # 1 个样本，3 个类别的原始打分
    criterion = nn.CrossEntropyLoss()  # 官方交叉熵：内部会做 softmax 再取负对数
    label = torch.tensor([0])  # 正确答案是第 0 类；整数默认是 long
    loss = criterion(logits, label)  # 预测偏向第 0 类，loss 较小
    print("loss:", loss.item())  # 取出这个 0 维张量里的 Python 数

    label = torch.tensor([2])  # 故意标成第 2 类，这一类打分最低
    loss = criterion(logits, label)  # 正确答案的概率更小，loss 变大
    print("loss:", loss.item())
    

def task2_manual():
    """任务 2 对照：手写 CrossEntropyLoss。loss = -log(softmax(logits)[label])。"""
    print(f"{'=' * 50}\n任务 2 对照：手写 CrossEntropyLoss\n{'=' * 50}")
    logits = torch.tensor([[2.0, 1.0, 0.1]])  # 和上面同一个样本的三个打分
    label = torch.tensor([0])  # 只看第 0 类是正确答案的情况
    criterion = nn.CrossEntropyLoss()  # 用来和手写结果对照
    z = logits[0]  # 去掉 batch 维，得到长度为 3 的分数
    z = z - z.max()  # 每个分数减去最大值，概率不变，避免 exp 溢出
    prob = z.exp() / z.exp().sum()  # softmax：三个类别的概率，加起来是 1
    loss = -prob[label].log()  # 只取第 0 类的概率，再取负对数
    print("softmax 概率:", prob)  # 第 0 类概率最高，约 0.66
    print("手写 loss:", loss.item())  # -log(第 0 类概率)
    print("库 loss:", criterion(logits, label).item())  # 应和手写 loss 一致


def task3_full_training():
    """任务 3：完整训练一个二分类小模型（本章核心任务）"""
    print(f"{'=' * 50}\n任务 3：完整训练一个二分类小模型\n{'=' * 50}")
    # 造一批合成分类数据：两类点，用一条直线就能分开
    #   X: (200, 2) 随机数；y: 第0类 X[:,0]+X[:,1]>0，否则第1类
    # 模型：nn.Linear(2, 2)（2维输入 → 2类输出，最简单的分类器）
    # 训练：CrossEntropyLoss + SGD(lr=0.5)，跑 50 轮（每轮全量数据，不用 batch）
    # 每 10 轮打印一次 loss 和准确率（argmax 后和 y 对比）
    # 期望：准确率最终接近 100%
    torch.manual_seed(42)
    X = torch.randn(200, 2)
    y = (X[:, 0] + X[:, 1] > 0).long()   # 0/1 标签，已帮你造好
    model = nn.Linear(2, 2)
    optimizer = optim.SGD(model.parameters(), lr=0.5)
    criterion = nn.CrossEntropyLoss()
    # 训练循环（50轮，每10轮打印 loss 和 acc）
    # 这里没有 DataLoader，直接把全部 200 个样本当一个 batch——五步循环不变
    for epoch in range(1, 51):
        optimizer.zero_grad()              # 1. 清梯度（防累积）
        output = model(X)                  # 2. 前向：200 个样本一次算完，output shape (200, 2)
        loss = criterion(output, y)        # 3. 算损失：logits + long 标签
        loss.backward()                    # 4. 反传：梯度写入所有参数的 .grad
        optimizer.step()                   # 5. 更新：机械手拧一遍参数

        if epoch % 10 == 0:
            acc = (output.argmax(dim=1) == y).float().mean().item()  # 预测类别 vs 真实标签
            print(f"epoch {epoch:3d} | loss = {loss.item():.4f} | acc = {acc:.2%}")


def task4_lr_experiment():
    """任务 4：感受学习率的威力（lr 太小 vs 太大）"""
    print(f"{'=' * 50}\n任务 4：感受学习率的威力\n{'=' * 50}")
    # 用任务 3 的代码，分别试 lr=0.001（太小）和 lr=10（太大），各跑 50 轮
    # 观察 loss 曲线和最终准确率，回答：
    #   太小会怎样？太大会怎样？为什么？
    # 把任务 3 的训练封装成函数，只换 lr，方便对比
    def train_with_lr(lr):
        torch.manual_seed(42)          # 固定随机种子，保证每次实验数据/初始权重相同，对比才公平
        X = torch.randn(200, 2)
        y = (X[:, 0] + X[:, 1] > 0).long()
        model = nn.Linear(2, 2)
        optimizer = optim.SGD(model.parameters(), lr=lr)
        criterion = nn.CrossEntropyLoss()
        print(f"--- lr = {lr} ---")
        for epoch in range(1, 51):
            optimizer.zero_grad()
            output = model(X)
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()
            if epoch % 10 == 0:
                acc = (output.argmax(dim=1) == y).float().mean().item()
                print(f"  epoch {epoch:3d} | loss = {loss.item():10.4f} | acc = {acc:.2%}")

    train_with_lr(0.001)   # 太小：步子像蚂蚁爬，50 轮还没走到最低点，loss 降不动、acc 上不去
    train_with_lr(10)      # 实测反而收敛更快！说明这个问题太简单——可分数据的交叉熵对大 lr 很宽容

    # 想看"lr 太大爆炸"，回到任务 1 的二次损失 (w*3-9)²：它对 lr 敏感得多
    print("--- 二次损失 (w*3-9)² 上的对比 ---")
    for lr in (0.05, 0.2):
        w = torch.tensor([1.0], requires_grad=True)
        opt = optim.SGD([w], lr=lr)
        history = []
        for _ in range(5):
            opt.zero_grad()
            loss = (w * 3 - 9) ** 2
            loss.backward()
            opt.step()
            history.append(f"{loss.item():.2f}")
        print(f"  lr={lr}: loss 前5轮 = {history}")
    # 实测：lr=0.05 三轮收敛到 0；lr=0.2 每步跨过最低点且越跨越远，36→243→1645→… 指数爆炸
    # 为什么：梯度只告诉你"往哪走"，lr 决定"走多远"。
    #   太小 → 走得慢，训练时间内走不到（lr=0.001 现象）
    #   太大 → 一步跨过最低点，落点比起点更远，来回横跳越跳越远（lr=0.2 现象）
    #   分类任务里没爆炸只是因为数据太容易分——换个难问题就会翻车


def task5_eval_pattern():
    """任务 5：验证阶段的标准写法（eval + no_grad）"""
    print(f"{'=' * 50}\n任务 5：验证阶段的标准写法\n{'=' * 50}")
    # 接任务 3 训练完的模型，写验证代码：
    #   model.eval() + with torch.no_grad(): 造 100 个新测试点，算准确率
    # 再对比：把 model.train() 改回去、去掉 no_grad 各跑一次，准确率有变化吗？
    # 思考：为什么真实项目里验证必须 eval + no_grad？
    # 先把任务 3 的模型重新训出来（和上面同样的种子与流程）
    torch.manual_seed(42)
    X = torch.randn(200, 2)
    y = (X[:, 0] + X[:, 1] > 0).long()
    model = nn.Linear(2, 2)
    optimizer = optim.SGD(model.parameters(), lr=0.5)
    criterion = nn.CrossEntropyLoss()
    for epoch in range(50):
        optimizer.zero_grad()
        loss = criterion(model(X), y)
        loss.backward()
        optimizer.step()

    # 造 100 个新测试点（换种子，模拟"模型没见过的数据"）
    torch.manual_seed(123)
    X_test = torch.randn(100, 2)
    y_test = (X_test[:, 0] + X_test[:, 1] > 0).long()

    # 标准验证写法：eval() + no_grad()
    model.eval()                      # 关掉 Dropout/BN 的随机行为（本模型没有，但习惯必须养成）
    with torch.no_grad():             # 不建图不录音：省内存、更快
        pred = model(X_test).argmax(dim=1)
        acc = (pred == y_test).float().mean().item()
    print(f"标准验证（eval+no_grad）准确率: {acc:.2%}")

    # 对比实验：去掉 no_grad 再跑一次
    pred = model(X_test).argmax(dim=1)   # 没包 no_grad，照样建图录音
    acc = (pred == y_test).float().mean().item()
    print(f"去掉 no_grad 后准确率: {acc:.2%}（数值一样，但白白建了计算图、占了内存）")

    # 对比实验：切回 train() 再跑一次
    model.train()
    with torch.no_grad():
        pred = model(X_test).argmax(dim=1)
        acc = (pred == y_test).float().mean().item()
    print(f"train() 模式下准确率: {acc:.2%}（本模型无 Dropout/BN 所以数值不变）")
    # 思考答案：准确率在这里没变化，是因为 Linear 在两种模式下行为一致。
    # 真实项目里模型常有 Dropout/BatchNorm——train() 下 Dropout 会随机掐神经元，
    # 每次预测结果都不一样，验证指标就废了；no_grad 则是省显存提速。
    # 所以"eval() + no_grad"是验证的铁律，不论模型里有没有这些层。


def main():
    """统一入口：想跑哪个任务就取消哪行的注释（或全跑）"""
    task1_optimizer()
    task1_manual()
    task2_crossentropy()
    task2_manual()
    task3_full_training()
    task4_lr_experiment()
    task5_eval_pattern()


if __name__ == '__main__':
    main()
