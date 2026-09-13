# 15 - PPO

## 🎯 学习目标
- 理解策略梯度与价值方法的区别
- 理解 PPO 的 clipped 目标函数为何稳定
- 掌握 Actor-Critic 架构
- 了解 PPO 的训练流程与超参数

---

## 📚 核心知识点

### 1. 两条路线：价值方法 vs 策略方法

| | DQN（价值） | PPO（策略） |
|---|------------|------------|
| 学什么 | Q 值，间接推策略 | 直接学策略 π(a\|s) |
| 动作空间 | 只能离散 | **离散 + 连续都行** |
| 样本效率 | 高（可回放旧数据） | 较低（主要 on-policy） |
| 稳定性 | 依赖技巧堆叠 | 天然较稳 |

机器人关节控制是**连续动作**（力矩取任意实数），DQN 做不了，这正是 PPO 的主场。

### 2. 策略梯度：直接优化策略

策略 π_θ(a|s) 是神经网络（θ 是参数），直接对期望回报求梯度：

```
∇J(θ) = E[ ∇log π_θ(a|s) · A(s,a) ]
```

直觉：
- 动作带来的优势 A > 0（比预期好）→ 增大它的概率
- A < 0（比预期差）→ 减小它的概率
- `log π` 让"调概率"变成可微分的梯度下降

**优势函数 A(s,a) = Q(s,a) − V(s)**：这个动作比平均水平好多少。用 Critic 网络估计 V(s) 来当基线，降低方差 → **Actor-Critic** 架构。

### 3. Actor-Critic 网络结构

```python
class ActorCritic(nn.Module):
    def __init__(self, state_dim, action_dim):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(state_dim, 128), nn.Tanh(),
            nn.Linear(128, 128), nn.Tanh(),
        )
        self.actor_head = nn.Linear(128, action_dim)   # 输出动作分布参数
        self.critic_head = nn.Linear(128, 1)           # 输出 V(s)

    def forward(self, x):
        h = self.shared(x)
        logits = self.actor_head(h)          # 离散：各类别 logit
        value = self.critic_head(h)          # 状态价值
        return logits, value
```

- **离散动作**：Actor 输出 logits → `Categorical` 分布采样
- **连续动作**：Actor 输出高斯分布的均值（+可学习 std）→ `Normal` 分布采样

### 4. PPO 的核心：Clipped 目标

朴素策略梯度的问题：步子迈大了策略突变，训练崩溃。PPO 限制每次更新幅度：

```python
ratio = torch.exp(new_logprob - old_logprob)   # 新旧策略概率比

surr1 = ratio * advantage
surr2 = torch.clamp(ratio, 1 - 0.2, 1 + 0.2) * advantage
actor_loss = -torch.min(surr1, surr2).mean()   # ← PPO 的灵魂
```

- `ratio` ≈ 1 表示新策略没偏离旧策略太多
- 裁剪到 [0.8, 1.2]：**好的更新给奖励但不许贪多，坏的更新直接踩刹车**
- 取 min 保证裁剪只在"有利"方向生效（悲观原则）

### 5. PPO 完整训练循环

```
循环：
  1. 用当前策略 rollout：收集 T 步 (s,a,r,logprob,value)
  2. 用 GAE 计算每步优势 A 和回报目标
  3. 对这批数据做 K 个 epoch 的小批量更新：
       actor_loss = -min(ratio·A, clip(ratio)·A)
       critic_loss = MSE(V(s), 回报)
       entropy_bonus → 鼓励探索
       total_loss = actor_loss + 0.5·critic_loss - 0.01·entropy
  4. 重复
```

### 6. GAE：广义优势估计

用多步信息平衡偏差与方差：

```
δ_t = r_t + γ·V(s_{t+1}) − V(s_t)          # 单步 TD 误差
A_t = δ_t + (γλ)·δ_{t+1} + (γλ)²·δ_{t+2} + ...
```

λ=0 → 只看一步（偏差大）；λ=1 → 看全程（方差大）；常用 λ=0.95。

### 7. 训练片段（骨架）

```python
dist = Categorical(logits=logits)          # 或 Normal(mu, sigma)
new_logprob = dist.log_prob(action)
ratio = (new_logprob - old_logprob).exp()

actor_loss = -torch.min(ratio * adv,
                        ratio.clamp(0.8, 1.2) * adv).mean()
critic_loss = F.mse_loss(value, returns)
entropy = dist.entropy().mean()

loss = actor_loss + 0.5 * critic_loss - 0.01 * entropy
optimizer.zero_grad()
loss.backward()
nn.utils.clip_grad_norm_(model.parameters(), 0.5)
optimizer.step()
```

### 8. 关键超参数（经验值）

| 参数 | 常用值 | 说明 |
|------|--------|------|
| clip ε | 0.2 | 裁剪范围 |
| γ / λ | 0.99 / 0.95 | 折扣 / GAE |
| lr | 3e-4 | 配合 Adam |
| rollout 步数 | 2048 | 每轮收集的数据量 |
| K epochs | 10 | 每批数据复用次数 |
| batch | 64 | 小批量大小 |

> 工程建议：PPO 细节极多，实战用 **stable-baselines3 / CleanRL** 的实现，先理解原理再调库。

---

## 💻 实战练习

```python
# 用 stable-baselines3 三行跑通 PPO
from stable_baselines3 import PPO
import gymnasium as gym

env = gym.make('CartPole-v1')
model = PPO('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=50000)
```

## ⚠️ 常见坑

1. advantage 忘 detach → 梯度传错地方
2. old_logprob 每轮没重存 → ratio 基准错了
3. 熵系数设太大 → 策略一直保持随机不收敛
4. on-policy 数据用完必须丢 → 拿旧数据反复刷会偏

---

## 📝 小结

- PPO 直接优化策略，天然支持连续动作 → 机器人领域标配
- Actor 出动作分布、Critic 估价值算优势
- clip(ratio) 限制更新步幅是稳定性的来源
- 下一步：16 机器人强化学习，把 PPO 用到仿真机器人上
