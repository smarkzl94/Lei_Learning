"""
practice11 - CNN 图像分类实战：迁移学习（方案A：冻结特征层，只训分类头）
对应文档 04_卷积神经网络/02_图像分类实战.md
CPU 友好版：特征缓存 trick —— 冻结的特征只需算一次
运行：python practice11_cnn_transfer.py

整条流水线：
  图片 → 预处理 → 冻结的 ResNet18 主干 → 512 维特征（只算一次）
       → 可训练的分类头 Linear(512→10) → 10 个类别得分
"""
import io  # 把 parquet 里的图片字节当成文件打开

import duckdb  # 直接用 SQL 读 parquet，不用先下载成图片文件夹
import torch  # 张量、随机数、保存权重
from PIL import Image  # 把 PNG 字节解码成图片
from torch import nn  # Linear、Sequential 这些层
from torch.utils.data import DataLoader, Dataset, Subset  # 数据集接口、取子集、按批读取
from torchvision import models, transforms  # 现成的 ResNet18，以及图片预处理

torch.manual_seed(42)  # 固定随机种子，裁剪、打乱、新分类头的初始权重每次一样

RESIZE = 96  # 原图 32×32；ResNet 习惯 224，这里折中成 96 以换速度
EPOCHS = 15  # 分类头要看完整训练集的轮数
BATCH_SIZE = 64  # 每次同时处理 64 张，或 64 条特征向量
CLASSES = ['飞机', '汽车', '鸟', '猫', '鹿', '狗', '青蛙', '马', '船', '卡车']  # 下标 0~9 就是标签
IMAGENET_MEAN = [0.485, 0.456, 0.406]  # 预训练时每个颜色通道的均值
IMAGENET_STD = [0.229, 0.224, 0.225]  # 对应标准差；输入必须按同一套数标准化，主干才认得出图
BEST_FC_PATH = 'best_fc.pth'  # 只存分类头，主干是别人训好的，不用存


class CIFARParquet(Dataset):
    """从 HF parquet 读取 CIFAR-10，接口与 torchvision 数据集一致。"""

    def __init__(self, path, transform=None):
        # 一次读出全部「图片字节 + 标签」；字节先不解码，取某一张时再打开
        rows = duckdb.sql(f"SELECT img.bytes AS b, label FROM '{path}'").fetchall()
        self.imgs = [r[0] for r in rows]  # 每张图的 PNG 原始字节
        self.labels = [r[1] for r in rows]  # 每张图的类别编号 0~9
        self.transform = transform  # 后面 __getitem__ 里才真正做缩放、增强、标准化

    def __len__(self):
        return len(self.labels)  # DataLoader / Subset 靠它知道一共有多少张

    def __getitem__(self, i):
        img = Image.open(io.BytesIO(self.imgs[i])).convert('RGB')  # 字节 → 三通道图片
        if self.transform:
            img = self.transform(img)  # PIL 图 → 标准化后的张量，形状 (3, 96, 96)
        return img, self.labels[i]  # 一条样本 = (图, 标签)


def extract_features(model, dataset, tag):
    """用「去掉 fc 的 ResNet18」把每张图压成 512 维特征向量。"""
    # children() 最后一层是 fc；丢掉它，再把剩余的 (512, 1, 1) 拉成 (512,)
    backbone = nn.Sequential(*list(model.children())[:-1], nn.Flatten())
    backbone.eval()  # 关掉 Dropout / BN 的训练行为，特征每次要一样
    # shuffle=False：特征和标签按下标对齐，后面才能和 y 对上
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    feats, labs = [], []  # 每批一个张量，最后再拼起来
    with torch.no_grad():  # 主干已冻结，这里不算梯度，省内存
        for i, (imgs, labels) in enumerate(loader):  # imgs: (64, 3, 96, 96)
            feats.append(backbone(imgs))  # 一批图 → (64, 512)
            labs.append(labels)  # 这批对应的标签，顺序不能打乱
            if (i + 1) % 10 == 0:
                print(f"  {tag}: {i + 1}/{len(loader)} 批", flush=True)  # 提特征很慢，隔 10 批报一次
    return torch.cat(feats), torch.cat(labs)  # (N, 512) 和 (N,)，N 是子集张数


def main():
    # train_tf 给训练集用，val_tf 给验证集用
    # 训练做随机增强，验证保持确定性。两边都要按 ImageNet 的均值方差标准化
    train_tf = transforms.Compose([
        transforms.Resize(RESIZE),  # 32×32 → 96×96，迁就预训练主干的感受野
        transforms.RandomCrop(RESIZE, padding=8),  # 先垫一圈再随机裁回 96，等于随机平移
        transforms.RandomHorizontalFlip(),  # 左右翻转；飞机、猫这类左右对称，标签不变
        transforms.ToTensor(),  # PIL → 张量，像素从 0~255 变成 0~1，形状 (3, 96, 96)
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),  # Normalize 再按 ImageNet 的均值和方差做一次平移缩放。主干认的是这种数值范围，不按这套数处理，冻住的卷积层就提取不出原来那套特征
    ])
    TRAIN_PARQUET = './data/cifar10_train.parquet'  # 训练集文件
    train_full = CIFARParquet(TRAIN_PARQUET, train_tf)  # 完整训练集，取样本时才做增强
    
    val_tf = transforms.Compose([
        transforms.Resize(RESIZE),  # 验证不做随机裁剪和翻转，同一张图每次结果相同
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD), # Normalize 再按 ImageNet 的均值和方差做一次平移缩放。主干认的是这种数值范围，不按这套数处理，冻住的卷积层就提取不出原来那套特征
    ])
    VAL_PARQUET = './data/cifar10_test.parquet'  # 验证集文件（官方测试集，训练时没见过）
    val_full = CIFARParquet(VAL_PARQUET, val_tf)  # 完整验证集
    
    N_TRAIN, N_VAL = 3000, 1000  # 只用子集：CIFAR-10 全量 5 万张，CPU 跑不动
    train_set = Subset(train_full, range(3000))  # 只要前 3000 张
    val_set = Subset(val_full, range(1000))  # 只要前 1000 张
    print(f"训练集 {len(train_set)} 张，验证集 {len(val_set)} 张（CIFAR-10 子集）")

    # 方案 A：主干照搬 ImageNet 上学来的视觉特征，只换最后一层来认这 10 类
    model = models.resnet18(weights='IMAGENET1K_V1')  # 18 层残差网络，原来输出 1000 类
    for param in model.parameters():
        param.requires_grad_(False)  # 卷积层全部冻住：不再为 CIFAR 改这些权重
    model.fc = nn.Linear(model.fc.in_features, len(CLASSES))  # 新头：512 → 10，默认可训练
    
    total = sum(param.numel() for param in model.parameters())  # 整个网络的参数个数
    trainable = sum(param.numel() for param in model.parameters() if param.requires_grad)  # 只有新 fc
    print(f"参数：总 {total / 1e6:.1f}M，可训练只有 {trainable / 1e3:.1f}K（分类头）")

    print("提取训练集特征（一次性）...")
    x_train, y_train = extract_features(model, train_set, "train")  # 图变成 (3000, 512)
    print("提取验证集特征（一次性）...")
    x_val, y_val = extract_features(model, val_set, "val")  # (1000, 512)；验证不做随机增强，缓存有效
    print(f"特征形状：{tuple(x_train.shape)}  ← 每张图已压成 512 维向量")

    # 特征已经缓存，这里只更新分类头
    optimizer = torch.optim.AdamW(model.fc.parameters(), lr=1e-3, weight_decay=0.01)  # 优化器只拿到 fc 的参数
    criterion = nn.CrossEntropyLoss()  # 10 个得分 vs 一个类别编号，内部含 softmax
    n_train = len(x_train)  # 3000 条特征向量，不再是 3000 张图
    best_acc = 0.0  # 验证集上见过的最高准确率

    for epoch in range(EPOCHS):  # 每一轮把 3000 条特征都看一遍
        model.fc.train()  # 分类头切到训练模式（这层没有 Dropout，影响很小）
        perm = torch.randperm(n_train)  # 每轮重新洗牌，避免模型记住样本顺序
        total_loss = 0.0  # 这一轮损失的加权和，后面除以张数得到平均
        for start in range(0, n_train, BATCH_SIZE):  # 0, 64, 128, ... 直到 3000
            idx = perm[start:start + BATCH_SIZE]  # 这一批在缓存里的下标
            optimizer.zero_grad()  # 清掉上一批留在分类头上的梯度
            loss = criterion(model.fc(x_train[idx]), y_train[idx])  # (64, 512) → (64, 10) 得分，再和标签比
            loss.backward()  # 只回传到 fc 的权重和偏置
            optimizer.step()  # 按学习率改分类头
            total_loss += loss.item() * len(idx)  # loss 是批平均，乘回来才是这批的总损失

        model.fc.eval()  # 验证：不再更新
        with torch.no_grad():
            preds = model.fc(x_val).argmax(1)  # 10 个得分里最大的那个下标 = 预测类别
            acc = (preds == y_val).float().mean().item()  # 猜对的比例
        if acc > best_acc:  # 比历史最好还高，才覆盖存盘
            best_acc = acc
            torch.save(model.fc.state_dict(), BEST_FC_PATH)  # 只存分类头的权重，不存整个 ResNet
        mark = "  ★ 新最佳" if acc == best_acc else ""
        print(f"Epoch {epoch + 1:2d}: loss={total_loss / n_train:.4f}  val_acc={acc:.4f}{mark}")

    print(f"\n最佳验证准确率：{best_acc:.4f}")  # 15 轮里验证集最高的那一次，不一定是最后一轮

    # 用最好的头，看哪几类互相认错。行是真实类别，列是预测类别
    model.fc.load_state_dict(torch.load(BEST_FC_PATH, weights_only=True))  # 换回验证集上最好的那颗头
    model.fc.eval()
    with torch.no_grad():
        preds = model.fc(x_val).argmax(1)  # 1000 张验证图各自的预测类别

    conf = torch.zeros(len(CLASSES), len(CLASSES), dtype=torch.int)  # 10×10 计数表，起步全 0
    for true_label, pred in zip(y_val, preds):
        conf[true_label, pred] += 1  # 真实是行、预测是列，该格 +1；对角线就是猜对的

    print("\n混淆矩阵（行=真实，列=预测）：")
    print("      " + " ".join(f"{name:>4}" for name in CLASSES))  # 列标题
    for i, row in enumerate(conf):
        counts = " ".join(f"{value:>4}" for value in row.tolist())
        print(f"{CLASSES[i]:>4}  {counts}")  # 一行：这一类被预测成各类的次数

    print("\n各类召回率：")
    for i, name in enumerate(CLASSES):
        recall = conf[i, i].item() / conf[i].sum().item()  # 该类猜对的次数 / 该类真实总数
        print(f"  {name}: {recall:.2f}")

    _, label = val_full[0]  # 验证集第 0 张的真实标签；图本身下面会再提一次特征
    features, _ = extract_features(model, Subset(val_full, [0]), "推理")  # 单张图 → (1, 512)
    with torch.no_grad():
        prob = model.fc(features).softmax(1)  # 10 个得分变成加总为 1 的概率
        confidence, pred = prob.max(1)  # 最大概率，以及它对应的类别下标
    print(
        f"\n单图推理：预测「{CLASSES[pred.item()]}」（置信度 {confidence.item():.2f}），"
        f"真实「{CLASSES[label]}」"
    )


if __name__ == '__main__':
    main()  # 直接运行本文件才训练；被别的文件 import 时不会自动开跑
