# PyTorch 学习笔记

> 个人学习笔记，记录日期：2026-09-30
> 配套教材：`PyTorch学习/01_基础入门/01_张量与运算.md`、`02_自动求导.md`
> 练习代码：`D:\DemoPy\practice\practice01.py` / `practice02.py`

---

# 第一部分：张量与运算（第 01 章）

## 一、张量的创建（初始化）

创建张量的核心问题就两个：**形状（shape）由谁定？内容从哪来？**
- 自己给数据 → `torch.tensor`
- 给形状、内容程序造 → 其余所有方法

```python
torch.tensor([[1, 2], [3, 4]])   # 内容完全确定，就是 1,2,3,4
```

**规律：嵌套几层 `[ ]` 就是几维**
- `torch.tensor(5)` → 0 维，一个数，shape `()`
- `torch.tensor([1, 2, 3])` → 1 维，一排，shape `(3,)`
- `torch.tensor([[1,2],[3,4]])` → 2 维，一张表，shape `(2, 2)`

### 创建方法速查表

| 方法 | 形状 | 内容 | 典型用途 |
|---|---|---|---|
| `torch.tensor(数据)` | 由数据定 | 你写的 | 有现成数据时 |
| `torch.zeros(m, n)` | 你指定 | 全 0 | 初始化占位、累加器 |
| `torch.ones(m, n)` | 你指定 | 全 1 | 构造单位张量 |
| `torch.rand(m, n)` | 你指定 | 0~1 随机 | 造测试数据 |
| `torch.randn(m, n)` | 你指定 | 0 附近随机 | **权重初始化** |
| `torch.arange(起,止,步)` | 程序算 | 等差数列 | 生成索引序列 |
| `torch.linspace(起,止,数)` | 程序算 | 等间距 | 生成坐标轴 |
| `torch.full((m,n), v)` | 你指定 | 全是 v | 填充固定值 |
| `x.new_ones(...)` | 你指定 | 全 1 | 继承 x 的类型/设备 |

**rand vs randn**：rand 造 0~1 的数（均匀分布），randn 造 0 附近的数（正态分布，权重初始化用它）。
**arange vs linspace**：arange 按**步长**取（前闭后开，取不到终点），linspace 按**个数**取（取得到终点）。

## 二、张量的常用属性

| 用法 | 含义 | 用途 |
|---|---|---|
| `x.shape` | 形状，如 `(4, 3, 32, 32)` | 排查 shape 对不对的第一手段 |
| `x.dtype` | 数据类型，默认 float32 | 索引/标签必须是 long |
| `x.device` | 在哪个设备（cpu / cuda:0） | 排查设备不一致报错 |
| `x.requires_grad` | 是否追踪梯度 | "录音开关"，第 02 章用 |
| `x.float()` / `x.long()` / `x.to(...)` | 类型转换 | 喂给模型前统一类型 |

**为什么默认 float32 不是 float64**：省一半内存，深度学习对精度不敏感。

## 三、形状操作（高频）

```python
x = torch.randn(4, 3, 32, 32)   # 模拟一批 4 张 3 通道 32x32 图片（NCHW）

x.view(4, -1)          # (4, 3072)  -1 让程序自动算维度（只能出现一次）
x.reshape(12, 32, 32)  # 同 view，但允许非连续内存，更不容易报错
x.flatten(1)           # (4, 3072)  从第 1 维开始压平
x.permute(0, 2, 3, 1)  # NCHW → NHWC，维度换序
x.transpose(1, 2)      # 交换两个维度
x.unsqueeze(0)         # 加一维：(C,H,W) → (1,C,H,W)，单张图假装成 batch
x.squeeze()            # 删长度为 1 的维，反向操作
x.expand(8, -1, -1, -1) # 撑大长度为 1 的维（不复制内存，比 repeat 快）
```

**记忆点**：
- 张量在内存里是一维"长条"，shape 只是"每几个切一组"的说明书
- view 只是换说明书（要求内存连续），reshape 换不了就先复制再换
- **图像永远 NCHW**：批次 N、通道 C、高 H、宽 W

## 四、索引与切片

| 写法 | 干什么 | 形象说法 |
|---|---|---|
| `x[0]` | 取一行 | 点名一个人 |
| `x[:, 0]` | 取一列 | 一门课的全班成绩 |
| `x[1:3]` | 取连续一段（含头不含尾） | 第 1~2 号 |
| `x[x > 80]` | 按条件挑元素（结果压平成 1 维） | 挑出 80 分以上的 |
| `x[idx]` | 按索引张量取多行，可重复可乱序 | 按学号清单点名 |

**读法**：逗号分隔维度，每个位置对应 shape 里对应维度；`:` 表示"全都要"。
**布尔掩码原理**：`x > 0` 先生成一张对错表（True/False），再把 True 位置的数挑出来。

## 五、数学运算

| 用法 | 含义 | 用途 |
|---|---|---|
| `a * b` | 逐元素乘 | 较少用 |
| `a @ b` | 矩阵乘法（一行乘一列，对应相乘再相加） | **神经网络主力**（线性层 y=xW+b） |
| `x.sum(dim=1)` | 沿维度聚合，该维消失 | 统计 |
| `x.sum(dim=1, keepdim=True)` | 聚合但保留维度 | 保住广播能力 |
| `x.argmax(dim=1)` | 返回最大值的位置 | **分类预测最常用** |
| `x.max(dim=1)` | 返回 (值, 位置) 两个结果 | 看预测置信度 |
| `torch.topk(x, k=5, dim=1)` | 前 5 大的值和位置 | Top-5 准确率 |

**`*` vs `@` 是最大的坑**：算出 shape 不对，先检查是不是把矩阵乘 `@` 写成了逐元素 `*`。
**dim 口诀**：`dim=k` 的意思是"把第 k 维压掉"。

## 六、广播机制

形状不同的张量运算时，自动把"长度为 1 或缺失"的维补齐，规则：**从右往左对齐，缺失当 1，是 1 就能撑**。

```python
x = torch.randn(4, 3)
b = torch.randn(3)
x + b        # b 自动复制成 (4,3) 再加——线性层的偏置就是这么加的
```

## 七、与 NumPy 互转

```python
t = torch.from_numpy(a)   # 共享内存！改一个另一个也变（零拷贝，省内存）
b = t.numpy()             # 仅 CPU 张量可转
a.copy() / t.clone()      # 要独立副本就显式复制
```

## 八、GPU 加速

```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
x = x.to(device)          # 张量搬过去；已在目标设备则是空操作
model = model.to(device)  # 模型搬过去
# 运算双方必须在同一设备，否则报错
```

---

# 第二部分：自动求导（第 02 章）

## 核心概念（用下山类比）

- **导数 = 坡度**：告诉你往哪个方向走（反方向）、迈多大步
- **梯度 = 每个参数各自的坡度**：每个参数一个数，"调大 loss 涨还是降"
- **loss（损失）= 错得有多离谱**：训练的唯一目标就是把它压到最小
- **forward（前向传播）= 做题**：算出预测
- **backward（反向传播）= 错题归因**：沿计算图回传，算出每个参数的梯度
- **训练 = 反复：做题 → 对答案(loss) → 归因(backward) → 改错(调参数)**

**为什么需要训练**：公式结构（y=xW+b）是给定的，但参数 W、b 初始是随机数——参数才是要学的"知识"，训练就是把旋钮拧到位的过程。

## 用法速查表

| 用法 | 用途 | 备注 |
|---|---|---|
| `x = torch.tensor(2.0, requires_grad=True)` | 给张量开"录音"（追踪计算） | 只有浮点类型能开 |
| `y = x**2 + 3*x` | 前向计算（自动建图） | 每个运算都被录下 |
| `loss.backward()` | 反向传播，梯度存入各参数的 `.grad` | loss 必须是标量 |
| `x.grad` | 取算好的梯度 | backward 之后才有值 |
| `optimizer.zero_grad()` / `w.grad.zero_()` | 清零梯度 | **每轮必做！否则梯度累加** |
| `w -= lr * w.grad` | 手写参数更新 | 必须包在 `no_grad` 里，否则报错 |
| `with torch.no_grad():` | 作用域内不建图 | **验证/测试必包**，省显存加速 |
| `param.requires_grad_(False)` | 永久关掉某参数的录音 | 微调时冻结预训练层 |
| `z = y.detach()` | 复制一个"失忆"分身 | 值共享内存，但与图无关 |
| `loss.item()` | 取单元素张量的纯数值 | 记录 loss 必用，防显存泄漏 |
| `loss.backward(retain_graph=True)` | 保留计算图 | 需要对同一图多次 backward 时 |

## 训练五步口诀（最重要）

```python
optimizer.zero_grad()    # 1. 清零（防梯度累积）
output = model(data)     # 2. forward：做题
loss = criterion(output, target)  # 3. loss：对答案
loss.backward()          # 4. backward：错题归因
optimizer.step()         # 5. step：调参数
```

## 梯度累积实验（亲手验证过）

```python
x = torch.tensor(1.0, requires_grad=True)
y = x**2; y.backward(); print(x.grad)   # 2.0
y = x**2; y.backward(); print(x.grad)   # 4.0 ← 没清零，翻倍了！
x.grad.zero_()
y = x**2; y.backward(); print(x.grad)   # 2.0 ← 清零后恢复正常
```

## 常见报错对照

| 现象 | 原因 |
|---|---|
| 梯度越训练越大 / loss 爆炸 | 忘了 `zero_grad()` |
| `x.grad` 是 None | 没开 requires_grad / 中间被 detach 或 .item() 断图 / 参数没参与 loss |
| backward 报错"图已释放" | 同一图 backward 了两次，需 `retain_graph=True` |
| 验证时显存暴涨 | 没包 `torch.no_grad()` |
| int 张量开 requires_grad 报错 | 只有浮点类型能求导 |

---

# 第三部分：nn.Module（第 03 章）

## 核心概念

- **层 = 保管参数的盒子**：`nn.Linear` 就是手写的 `x @ W + b` 的官方封装——参数自动创建、自动开录音，只管给形状
- **nn.Module = 收纳箱**：`self.xxx = 层` 自动登记参数，喂 optimizer / 搬 GPU / 存盘都靠它
- **激活函数 = 非线性调料**：没有它，叠多少层线性都等价于一层（面试高频）
- **Dropout**：训练时按概率随机掐零神经元防过拟合；评估时自动关闭

## 标准模板三条规则

| 规则 | 原因 |
|---|---|
| `super().__init__()` 必须第一行写 | 不写参数全部丢失 |
| 层在 `__init__` 定义 | 收纳箱只在初始化时扫描 self.xxx |
| 计算流程写在 `forward` | 每次 `model(x)` 自动调用，**不要写 `model.forward(x)`** |

## 用法速查表

| 用法 | 用途 | 备注 |
|---|---|---|
| `nn.Linear(in, out)` | 全连接层 | 参数量 = in×out + out（面试口算用） |
| `nn.ReLU()` | 激活函数（负数掐 0） | 夹在层之间 |
| `nn.Dropout(p)` | 随机置零防过拟合 | 训练生效，eval 自动关 |
| `nn.Sequential(...)` | 直线结构偷懒写法 | 有分支/跳跃必须手写 forward |
| `nn.ModuleList([...])` | 层数不固定的层列表 | **普通 list 存层会丢参数！** |
| `nn.Conv2d(in, out, k, stride, padding)` | 卷积 | out = (in+2p-k)/s + 1 |
| `model.parameters()` | 所有参数的迭代器 | 直接喂给 optimizer |
| `model.train()` / `model.eval()` | 切换训练/评估模式 | 验证前必须 eval() |
| `model.to(device)` | 整个模型搬设备 | 数据也要 .to(device) |
| `model.state_dict()` | 有序字典 {参数名: 值} | 只存权重不存结构 |
| `model.apply(fn)` | 递归应用自定义初始化 | 特殊场景才用 |

---

# 第四部分：训练流程（第 04 章）

## 核心概念

- **损失函数 = 阅卷老师**：分类用 `CrossEntropyLoss`（输入 logits + long 标签，**内部已含 softmax，别再手动加**）
- **优化器 = 拧参数的机械手**：默认 `AdamW(lr=1e-3)`；SGD+momentum 是老派 CNN 选择
- **调度器 = 先大步后小步**：余弦退火 `CosineAnnealingLR` 最常用，每个 epoch 末尾 `scheduler.step()`
- **学习率**：太小训不动，太大震荡——超参数之王

## 优化器对比

| 优化器 | 特点 | 场景 |
|---|---|---|
| SGD+momentum | 一视同仁，需调 lr，泛化好 | 传统 CNN 极限精度 |
| Adam | 每个参数私人步长，对 lr 不敏感 | 省心默认 |
| **AdamW** | 修正 weight decay 与自适应的耦合 | **新项目默认**，Transformer 标配 |

## 回归损失三兄弟（2026-09-30 补充）

| | 小误差 | 大误差 | 场景 |
|---|---|---|---|
| MSELoss（L2） | 平方，压小 | 爆炸放大 | 误差分布干净 |
| L1Loss | 线性 | 线性 | 有离群点 |
| **SmoothL1Loss** | 平方（像 MSE） | 绝对值（像 L1） | **检测框回归、DQN** |

## 标准训练循环（骨架，背下来）

```python
for epoch in range(num_epochs):
    model.train()
    for data, target in train_loader:
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()          # 1. 清梯度
        output = model(data)           # 2. 前向
        loss = criterion(output, target)  # 3. 算损失
        loss.backward()                # 4. 反传
        optimizer.step()               # 5. 更新

    model.eval()
    with torch.no_grad():              # 验证：只做题不学习
        correct = sum((model(d.to(device)).argmax(1) == t.to(device)).sum().item()
                      for d, t in val_loader)
    scheduler.step()
```

**训练 vs 验证对比**：

| | 训练 | 验证 |
|---|---|---|
| 模式 | train() | eval() |
| 录音 | 开 | 关（no_grad） |
| 目的 | 更新参数 | 只评估 |

## 常见坑

1. 忘 `zero_grad()` → 梯度累积爆炸
2. CrossEntropyLoss 前手动加 Softmax → 数值不稳
3. 标签不是 long → dtype 报错
4. 验证忘 eval()+no_grad → 指标虚低、显存爆炸
5. 每个 epoch 存模型 → 只存 best

---

## 待补充

- [ ] Dataset 与 DataLoader（数据加载，第 05 章）
- [ ] 练习代码统一函数化封装（2026-09-30 已完成 practice01-04）
