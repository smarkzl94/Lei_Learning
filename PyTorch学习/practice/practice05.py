# ============================================================
# PyTorch 05 章实战：Dataset 与 DataLoader
# 运行命令: python practice05.py
# 核心一句话：Dataset 管"读一条"（菜谱），DataLoader 管"组一批"（传菜员）
# ============================================================
import torch
from torch import nn, optim
from torch.utils.data import DataLoader, Dataset, random_split


# ============================================================
# 任务 1：最小自定义 Dataset——两个方法就是一个数据集
# ============================================================
class MyDataset(Dataset):
    """自定义 Dataset 三步法：
    1. __init__：只建索引（快），别在这里读大数据——黄金法则是懒加载
    2. __len__：告诉外界数据集多大
    3. __getitem__：第 idx 条怎么读、怎么返回 (数据, 标签)
    """

    def __init__(self, n=200):
        # 这里是合成数据所以直接生成；真实场景只存"文件路径+标签"列表
        torch.manual_seed(42)
        self.X = torch.randn(n, 2)
        self.y = (self.X[:, 0] + self.X[:, 1] > 0).long()  # 和第 04 章同样的二分类数据

    def __len__(self):
        return len(self.X)              # len(ds) 时调用

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]  # ds[i] 时调用，返回一条 (数据, 标签)


def task1_dataset():
    print(f"{'=' * 55}\n任务 1：最小自定义 Dataset\n{'=' * 55}")
    ds = MyDataset(200)
    print("len(ds) =", len(ds))           # __len__ 在工作
    x, y = ds[0]                            # __getitem__ 在工作
    print("ds[0] 数据:", x.tolist(), "标签:", y.item())
    # 没有 DataLoader 也能用，但只能一条一条取——组 batch、打乱都得手写

# ============================================================
# 任务 2：DataLoader 组 batch——传菜员上岗
# ============================================================
def task2_dataloader():
    print(f"{'=' * 55}\n任务 2：DataLoader 组 batch\n{'=' * 55}")
    ds = MyDataset(10)                        # 只用 10 条，方便观察
    loader = DataLoader(ds, batch_size=4, shuffle=True)
    # batch_size=4：每批 4 条；shuffle=True：每轮顺序打乱（训练集 True，验证集 False）

    for batch_idx, (X, y) in enumerate(loader):
        # DataLoader 自动把 4 条 (2,) 的数据堆成 (4, 2)，4 个标签堆成 (4,)
        print(f"batch {batch_idx}: X shape {tuple(X.shape)}, X = {X.tolist()}, y = {y.tolist()}")
    # 10 条 ÷ 4 = 3 批，最后一批只有 2 条（drop_last=True 可丢掉这个尾巴）

    print("\n同一个 loader 再遍历一遍（注意顺序变了）:")
    X, y = next(iter(loader))
    print("第一批的 y:", y.tolist(), "← shuffle 让每个 epoch 顺序不同，防模型背顺序")


# ============================================================
# 任务 3：mini-batch 训练——把第 04 章的训练循环接上 DataLoader（本章核心）
# ============================================================
def task3_minibatch_training():
    print(f"{'=' * 55}\n任务 3：mini-batch 训练（接第 04 章）\n{'=' * 55}")
    ds = MyDataset(200)
    loader = DataLoader(ds, batch_size=32, shuffle=True)   # 200 条 ÷ 32 = 7 批/轮

    model = nn.Linear(2, 2)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.05)

    # 和第 04 章的五步一模一样，只是外面多了一层"逐批取数"的循环
    for epoch in range(1, 6):
        model.train()
        total_loss = 0.0
        for X, y in loader:                   # ← 唯一的新东西：一批一批喂
            optimizer.zero_grad()             # 1. 清梯度
            output = model(X)                 # 2. 前向（这批 32 条）
            loss = criterion(output, y)       # 3. 损失
            loss.backward()                   # 4. 反传
            optimizer.step()                  # 5. 更新
            total_loss += loss.item()
        print(f"epoch {epoch} | 平均 loss = {total_loss / len(loader):.4f}")
    # 为什么要分批？200 条能全塞进内存，但真实数据是几十万张图——
    # 全量算一次梯度太慢太占内存，mini-batch 是"抽样估计梯度"，又快又稳

    # 验证一下效果
    model.eval()
    with torch.no_grad():
        acc = (model(ds.X).argmax(1) == ds.y).float().mean().item()
    print(f"训练集准确率: {acc:.2%}")


# ============================================================
# 任务 4：random_split 划分训练/验证集
# ============================================================
def task4_split():
    print(f"{'=' * 55}\n任务 4：random_split 划分数据集\n{'=' * 55}")
    ds = MyDataset(200)
    train_set, val_set = random_split(
        ds, [160, 40],
        generator=torch.Generator().manual_seed(42))   # 固定种子，划分可复现

    # 训练 loader 打乱，验证 loader 不打乱——铁律
    train_loader = DataLoader(train_set, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=32, shuffle=False)
    print(f"训练集 {len(train_set)} 条，验证集 {len(val_set)} 条")

    # 完整闭环：训练 + 验证（这就是以后所有项目的骨架）
    model = nn.Linear(2, 2)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.05)

    for epoch in range(1, 6):
        model.train()
        for X, y in train_loader:
            optimizer.zero_grad()
            loss = criterion(model(X), y)
            loss.backward()
            optimizer.step()

        model.eval()                          # 验证：只做题不学习
        correct = 0
        with torch.no_grad():
            for X, y in val_loader:
                correct += (model(X).argmax(1) == y).sum().item()
        print(f"epoch {epoch} | 验证准确率 = {correct / len(val_set):.2%}")


# ============================================================
# 任务 5：collate_fn——样本长度不一时怎么组 batch
# ============================================================
class VarLenDataset(Dataset):
    """模拟 NLP 场景：每条是长度不一的序列（比如句子）"""

    def __init__(self):
        self.data = [torch.tensor([1, 2, 3]),        # 长 3
                     torch.tensor([4, 5]),            # 长 2
                     torch.tensor([6, 7, 8, 9])]      # 长 4
        self.labels = [0, 1, 0]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]


def collate_fn(batch):
    """默认的组 batch 是直接 stack，长度不一就会报错。
    自定义 collate_fn：先把短序列补 0 到本批最长，再 stack。"""
    from torch.nn.utils.rnn import pad_sequence
    seqs, labels = zip(*batch)                          # 拆开：3 条序列 + 3 个标签
    seqs = pad_sequence(seqs, batch_first=True, padding_value=0)  # 补齐
    return seqs, torch.tensor(labels)


def task5_collate():
    print(f"{'=' * 55}\n任务 5：collate_fn 处理变长序列\n{'=' * 55}")
    ds = VarLenDataset()
    loader = DataLoader(ds, batch_size=3, collate_fn=collate_fn)
    seqs, labels = next(iter(loader))
    print("补齐后的 batch:")
    print(seqs)          # 短序列尾部补 0，shape (3, 4)
    print("labels:", labels.tolist())
    # 如果不给 collate_fn，这行会直接报 stack 错误——可以删掉参数试试


if __name__ == '__main__':
    task1_dataset()
    task2_dataloader()
    task3_minibatch_training()
    task4_split()
    task5_collate()
    print(f"\n{'=' * 55}\n05 章练习完毕 ✓  下一步：06 数据增强（需 torchvision）\n{'=' * 55}")
