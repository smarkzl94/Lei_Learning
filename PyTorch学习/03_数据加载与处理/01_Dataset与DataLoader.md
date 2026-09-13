# 05 - Dataset 与 DataLoader

## 🎯 学习目标
- 理解 Dataset / DataLoader 的职责划分
- 掌握自定义 Dataset 的标准写法
- 掌握 DataLoader 的关键参数与性能调优
- 了解内置数据集与数据划分

---

## 📚 核心知识点

### 1. 职责划分

| 组件 | 职责 | 类比 |
|------|------|------|
| `Dataset` | 定义"第 i 条数据是什么"（怎么读、怎么增强） | 菜谱 |
| `DataLoader` | 批量取数、打乱、多进程加载、组 batch | 传菜员 |

### 2. 自定义 Dataset 三步法

继承 `torch.utils.data.Dataset`，实现两个方法：

```python
from torch.utils.data import Dataset
from PIL import Image
import os

class CatDogDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.samples = []                              # (路径, 标签) 列表
        for label, cls in enumerate(['cat', 'dog']):
            cls_dir = os.path.join(root_dir, cls)
            for fname in os.listdir(cls_dir):
                self.samples.append((os.path.join(cls_dir, fname), label))
        self.transform = transform

    def __len__(self):
        return len(self.samples)                       # ① 数据集多大

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        image = Image.open(path).convert('RGB')        # ② 第 idx 条怎么读
        if self.transform:
            image = self.transform(image)
        return image, label                            # 返回 (数据, 标签)
```

> **黄金法则**：`__init__` 只建索引（快），真正的读图放在 `__getitem__`（懒加载），大数据集才不会内存爆炸。

### 3. DataLoader 关键参数

```python
from torch.utils.data import DataLoader

loader = DataLoader(
    dataset,
    batch_size=32,        # 每批多少条
    shuffle=True,         # 训练集打乱；验证集 False
    num_workers=4,        # 多进程加载（Windows 下要包 if __name__ == '__main__'）
    pin_memory=True,      # 配合 GPU 加速 H2D 拷贝
    drop_last=True,       # 丢掉最后不足一个 batch 的尾巴
    persistent_workers=True,  # epoch 间不重启 worker，提速
)
```

**遍历**：

```python
for batch_idx, (images, labels) in enumerate(loader):
    # images: (32, 3, 224, 224)  labels: (32,)
    ...
```

### 4. Windows 下 num_workers 的坑

```python
# Windows 多进程必须包入口保护，否则无限重启报错
if __name__ == '__main__':
    loader = DataLoader(ds, num_workers=4)
    ...
# 调试期先设 num_workers=0（单进程）排除问题
```

### 5. 内置数据集

```python
from torchvision import datasets, transforms

transform = transforms.Compose([
    transforms.ToTensor(),                              # HWC[0,255] → CHW[0,1]
    transforms.Normalize((0.1307,), (0.3081,)),         # MNIST 均值方差
])

train_set = datasets.MNIST('./data', train=True,  download=True, transform=transform)
test_set  = datasets.MNIST('./data', train=False, download=True, transform=transform)

# 文件夹结构即标签的经典加载方式：
# data/train/cat/xxx.jpg  data/train/dog/yyy.jpg
dataset = datasets.ImageFolder('data/train', transform=transform)
print(dataset.classes)        # ['cat', 'dog']
```

常用内置：`MNIST`、`CIFAR10/100`、`ImageFolder`、`FashionMNIST`。

### 6. 数据集划分

```python
from torch.utils.data import random_split

train_set, val_set = random_split(dataset, [0.8, 0.2],
                                  generator=torch.Generator().manual_seed(42))
```

> ⚠️ 划分后要给 val_set 单独套"无增强"的 transform——用两个 Dataset 实例分别包装同一批路径，不要在划分后再改 transform。

### 7. collate_fn：自定义组 batch

默认 collate 把样本堆成张量。当样本**长度不一**（如变长序列）时要自定义：

```python
from torch.nn.utils.rnn import pad_sequence

def collate_fn(batch):
    seqs, labels = zip(*batch)
    seqs = pad_sequence(seqs, batch_first=True, padding_value=0)  # 补齐到最长
    return seqs, torch.tensor(labels)

loader = DataLoader(ds, batch_size=32, collate_fn=collate_fn)
```

### 8. 性能诊断口诀

GPU 利用率低（数据喂不饱）时按序排查：

1. `num_workers` 调大（CPU 核数的一半起步）
2. 开 `pin_memory=True` + `persistent_workers=True`
3. 增强太重 → 换成 GPU 端增强或预处理后存盘
4. 磁盘慢 → 打包成 lmdb/webdataset/二进制

---

## 💻 实战练习

```python
# 验证自定义 Dataset：取一条看形状和标签
ds = CatDogDataset('data/train', transform=transform)
img, label = ds[0]
print(img.shape, label)          # torch.Size([3, 224, 224]) 0

loader = DataLoader(ds, batch_size=8, shuffle=True)
imgs, labels = next(iter(loader))
print(imgs.shape, labels.shape)  # (8,3,224,224) (8,)
```

## ⚠️ 常见坑

1. `__init__` 里就把所有图读进内存 → 大数据集直接 OOM，必须懒加载
2. 验证集也做了随机增强 → 指标抖动，val 只做 Resize+ToTensor+Normalize
3. Windows 下 `num_workers>0` 不包 `if __name__ == '__main__'` → 死循环报错
4. `Image.open` 忘 `.convert('RGB')` → 灰度图/带透明通道的图混入，shape 不一致

---

## 📝 小结

- Dataset 管"读一条"，DataLoader 管"组一批"
- `__len__` + `__getitem__` 两个方法就是一个数据集
- 训练 shuffle=True，验证 shuffle=False + 无随机增强
- 下一步：06 数据增强，用 transform 让模型见更多"变化"
