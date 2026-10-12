"""
practice12 - CNN 图像分类实战：迁移学习方案 B（解冻深层，分层学习率微调）
对应文档 04_卷积神经网络/02_图像分类实战.md 第 2 节「方案B」
前置：先跑过 practice11（方案 A），本脚本会加载它训好的分类头 best_fc.pth 继续

与方案 A 的区别：
  A 冻结全部主干，只训分类头（特征可以缓存，飞快）
  B 额外解冻 layer4（最后一个残差块），让它适配 CIFAR-10；
    深层小学习率、分类头大学习率 = 分层学习率
  代价：特征每步都在变，不能再缓存，每轮要真跑图片（约 20 秒/轮，CPU 可承受）
"""
import io  # 把 parquet 里的图片字节当成文件打开

import duckdb  # 直接用 SQL 读 parquet
import torch  # 张量、随机数、保存权重
from PIL import Image  # 把 PNG 字节解码成图片
from torch import nn  # Linear 这些层
from torch.utils.data import DataLoader, Dataset, Subset  # 数据集接口
from torchvision import models, transforms  # ResNet18 和图片预处理

torch.manual_seed(42)  # 和方案 A 同样的种子，方便对比

RESIZE = 96  # 与方案 A 保持一致，主干输入 96×96
EPOCHS = 5  # 微调不用太多轮：主干只需小幅适配，多了容易过拟合
BATCH_SIZE = 64
CLASSES = ['飞机', '汽车', '鸟', '猫', '鹿', '狗', '青蛙', '马', '船', '卡车']
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]  # 主干仍然是 ImageNet 训出来的，标准化数值照旧
BEST_PATH = 'best_finetune.pth'  # 这次要存整个模型：主干的 layer4 也变了


class CIFARParquet(Dataset):
    """从 HF parquet 读取 CIFAR-10，接口与 torchvision 数据集一致。"""

    def __init__(self, path, transform=None):
        rows = duckdb.sql(f"SELECT img.bytes AS b, label FROM '{path}'").fetchall()
        self.imgs = [r[0] for r in rows]  # 每张图的 PNG 原始字节
        self.labels = [r[1] for r in rows]
        self.transform = transform

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, i):
        img = Image.open(io.BytesIO(self.imgs[i])).convert('RGB')
        if self.transform:
            img = self.transform(img)
        return img, self.labels[i]


def evaluate(model, loader):
    """在验证集上算准确率。model.eval() + no_grad：不算梯度、BN 用统计值。"""
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for imgs, labels in loader:
            correct += (model(imgs).argmax(1) == labels).sum().item()
            total += labels.size(0)
    return correct / total


def main():
    # 数据部分和方案 A 完全相同：训练随机增强、验证确定性、同一套标准化
    train_tf = transforms.Compose([
        transforms.Resize(RESIZE),
        transforms.RandomCrop(RESIZE, padding=8),  # 随机平移
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
    val_tf = transforms.Compose([
        transforms.Resize(RESIZE),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
    train_full = CIFARParquet('./data/cifar10_train.parquet', train_tf)
    val_full = CIFARParquet('./data/cifar10_test.parquet', val_tf)
    train_set = Subset(train_full, range(3000))  # 和方案 A 用同一个子集，对比才公平
    val_set = Subset(val_full, range(1000))
    train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_set, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    # 模型：还是那颗 ResNet18，但这次只冻"浅层"
    model = models.resnet18(weights='IMAGENET1K_V1')
    model.fc = nn.Linear(model.fc.in_features, len(CLASSES))  # 换 10 类头
    try:
        model.fc.load_state_dict(torch.load('best_fc.pth', weights_only=True))
        print("已加载方案 A 训好的分类头（best_fc.pth），站在它的肩膀上微调")
    except FileNotFoundError:
        print("没找到 best_fc.pth，先跑 practice11 效果更好；现在从头训分类头")

    for param in model.parameters():
        param.requires_grad_(False)  # 先全部冻住
    for param in model.layer4.parameters():
        param.requires_grad_(True)  # 解冻最后一个残差块：学 CIFAR 特有的高层特征
    for param in model.fc.parameters():
        param.requires_grad_(True)  # 分类头继续训

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"本轮可训练参数：{trainable / 1e6:.2f}M（layer4 + fc），其余冻结")

    # 分层学习率：深层学来的特征很珍贵，小步改；分类头是新的，大步走
    optimizer = torch.optim.AdamW([
        {'params': model.layer4.parameters(), 'lr': 1e-4},  # 深层：小心翼翼
        {'params': model.fc.parameters(), 'lr': 3e-4},  # 分类头：可以放开一点
    ], weight_decay=0.01)
    criterion = nn.CrossEntropyLoss()

    best_acc = 0.0
    for epoch in range(EPOCHS):
        model.train()  # 注意：BN 层进入训练模式，统计量会随 CIFAR 数据更新
        total_loss = n = 0
        for imgs, labels in train_loader:  # 每批 64 张真图，正向+反向约 0.4 秒
            optimizer.zero_grad()
            loss = criterion(model(imgs), labels)
            loss.backward()  # 梯度只流向 layer4 和 fc（浅层 requires_grad=False）
            optimizer.step()
            total_loss += loss.item() * imgs.size(0)
            n += imgs.size(0)

        acc = evaluate(model, val_loader)
        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), BEST_PATH)  # 整个模型一起存
        mark = "  ★ 新最佳" if acc == best_acc else ""
        print(f"Epoch {epoch + 1}: loss={total_loss / n:.4f}  val_acc={acc:.4f}{mark}")

    print(f"\n微调最佳验证准确率：{best_acc:.4f}（方案 A 是 0.7720）")

    # 混淆矩阵：和方案 A 对比，猫狗不分这类错误有没有减少
    model.load_state_dict(torch.load(BEST_PATH, weights_only=True))
    model.eval()
    conf = torch.zeros(len(CLASSES), len(CLASSES), dtype=torch.int)
    with torch.no_grad():
        for imgs, labels in val_loader:
            preds = model(imgs).argmax(1)
            for t, p in zip(labels, preds):
                conf[t, p] += 1

    print("\n混淆矩阵（行=真实，列=预测）：")
    print("      " + " ".join(f"{name:>4}" for name in CLASSES))
    for i, row in enumerate(conf):
        print(f"{CLASSES[i]:>4}  " + " ".join(f"{v:>4}" for v in row.tolist()))

    print("\n各类召回率：")
    for i, name in enumerate(CLASSES):
        print(f"  {name}: {conf[i, i].item() / conf[i].sum().item():.2f}")


if __name__ == '__main__':
    main()
