# 14 - DQN

## 🎯 学习目标
- 理解为什么用神经网络近似 Q 函数
- 掌握 DQN 的两大核心技术：经验回放、目标网络
- 能用 PyTorch 实现 DQN 并跑通 CartPole
- 了解 Double DQN 等改进

---

## 📚 核心知识点

### 1. 从 Q 表到 DQN

Q-Learning 用表格存 Q(s,a)，但状态连续/高维时表格存不下。

**DQN 的思路**：用神经网络 Q(s, a; θ) 近似 Q 函数——输入状态，输出每个动作的 Q 值。

```
状态 s → [神经网络] → [Q(s,a₁), Q(s,a₂), ...] → argmax 选动作
```

### 2. 直接套 Q-Learning 会崩：三大问题

1. **样本相关性**：连续交互的数据高度相关，神经网络学不好
2. **目标在动**：TD 目标 `r + γ max Q(s',a')` 用的也是正在更新的网络 → 追着自己的尾巴跑
3. **数据浪费**：每条经验只用一次

### 3. 解法一：经验回放（Replay Buffer）

```python
from collections import deque
import random

buffer = deque(maxlen=10000)

# 存：每一步交互都存进去
buffer.append((state, action, reward, next_state, done))

# 学：随机抽一批打破相关性
batch = random.sample(buffer, 64)
```

类比：把交互经验存进"错题本"，随机抽题复习，而不是按顺序死记硬背。

### 4. 解法二：目标网络（Target Network）

维护两个结构相同的网络：

- **在线网络 Q(s,a;θ)**：实时更新，用于选动作
- **目标网络 Q(s,a;θ⁻)**：参数冻结，只用来算 TD 目标，**每隔 N 步从在线网络复制一次**

```python
# TD 目标用目标网络算 → 靶子固定，训练稳定
with torch.no_grad():
    target = reward + gamma * target_net(next_state).max(1).values * (1 - done)

# 损失：在线网络的预测 vs 固定目标
q_pred = online_net(state).gather(1, action)   # 取出执行动作对应的 Q 值
loss = F.mse_loss(q_pred, target)

# 每 N 步同步
target_net.load_state_dict(online_net.state_dict())
```

### 5. DQN 完整实现（CartPole）

```python
import torch, torch.nn as nn, torch.optim as optim
import gymnasium as gym, random, numpy as np
from collections import deque

class QNet(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_dim, 128), nn.ReLU(),
            nn.Linear(128, 128), nn.ReLU(),
            nn.Linear(128, action_dim),
        )
    def forward(self, x):
        return self.net(x)

env = gym.make('CartPole-v1')
online = QNet(4, 2)
target = QNet(4, 2)
target.load_state_dict(online.state_dict())

optimizer = optim.Adam(online.parameters(), lr=1e-3)
buffer = deque(maxlen=10000)
gamma, batch_size = 0.99, 64
epsilon, sync_every = 1.0, 100
step_count = 0

def select_action(s, eps):
    if random.random() < eps:
        return env.action_space.sample()
    with torch.no_grad():
        return online(torch.FloatTensor(s)).argmax().item()

for episode in range(300):
    state, _ = env.reset()
    done = False
    while not done:
        action = select_action(state, epsilon)
        ns, r, term, trunc, _ = env.step(action)
        buffer.append((state, action, r, ns, term or trunc))
        state = ns
        done = term or trunc

        # --- 学习 ---
        if len(buffer) >= batch_size:
            batch = random.sample(buffer, batch_size)
            s, a, r, ns2, d = zip(*batch)
            s  = torch.FloatTensor(np.array(s))
            a  = torch.LongTensor(a).unsqueeze(1)
            r  = torch.FloatTensor(r)
            ns2 = torch.FloatTensor(np.array(ns2))
            d  = torch.FloatTensor(d)

            q = online(s).gather(1, a).squeeze(1)
            with torch.no_grad():
                tq = r + gamma * target(ns2).max(1).values * (1 - d)
            loss = nn.MSELoss()(q, tq)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            step_count += 1
            if step_count % sync_every == 0:
                target.load_state_dict(online.state_dict())

    epsilon = max(0.05, epsilon * 0.99)
```

**预期**：CartPole 满分 500，训练后平均回报应从 ~20 涨到 200+。

### 6. 关键细节对照

| 细节 | 为什么 |
|------|--------|
| `gather(1, a)` | 从 Q 输出向量里取出**实际执行的那个动作**的 Q 值 |
| `(1 - done)` | 终止状态没有未来，TD 目标只剩即时奖励 r |
| 目标计算包 `no_grad` | 目标网络不参与反传 |
| 先存够 batch 再学 | 早期经验太少时学习不稳定 |

### 7. 常见改进（了解）

- **Double DQN**：动作用在线网络选、价值用目标网络估 → 解决 Q 值过估计
- **Dueling DQN**：网络拆成 V(s) + A(s,a) 两路 → 状态价值和动作优势分开学
- **Prioritized Replay**：按 TD 误差大小优先抽样 → 重点复习"错得狠的"

### 8. DQN 的适用边界

✅ 离散动作空间（推杆左右、游戏按键）
❌ 连续动作（机器人关节力矩）→ 需要 DDPG / PPO / SAC（见 15、16 章）

---

## 💻 实战练习

1. 关掉经验回放（直接用上一步学）→ 观察训练是否崩溃
2. 关掉目标网络（target=online）→ 观察 Q 值发散
3. 这两个消融实验是理解 DQN 设计的最好方式

## ⚠️ 常见坑

1. `gather` 的索引必须是 `LongTensor` 且带维度 → 形状错最常见
2. done 时忘乘 `(1-done)` → 终止状态也算了未来价值
3. ε 衰减太快 → 没探索够就定型；太慢 → 收敛慢
4. buffer 设太小 → 样本多样性不足

---

## 📝 小结

- DQN = Q-Learning + 神经网络 + 经验回放 + 目标网络
- 回放打破相关性，目标网络稳住靶子
- 只适用于离散动作；连续动作走向策略梯度方法
- 下一步：15 PPO，策略梯度方法的工业标准
