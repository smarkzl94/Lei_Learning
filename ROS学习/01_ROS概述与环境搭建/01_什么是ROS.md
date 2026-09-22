# 01 - 什么是 ROS

## 🎯 学习目标
- 理解 ROS 的设计理念和核心概念
- 了解 ROS 的版本历史和生态系统
- 理解 ROS 的优缺点和适用场景

---

## 📚 核心知识点

### 1. ROS 简介

**ROS (Robot Operating System)** 不是传统意义上的操作系统，而是一个面向机器人的**软件框架/中间件**，提供：
- 硬件抽象
- 设备驱动
- 库函数
- 可视化工具
- 消息传递
- 包管理

### 2. ROS 的核心设计思想

| 特性 | 说明 |
|------|------|
| **点对点** | 分布式架构，节点之间直接通信 |
| **多语言** | 支持 C++、Python、Java、Lisp 等 |
| **工具化** | 提供大量调试、可视化工具 |
| **开源** | BSD 协议，社区活跃 |
| **模块化** | 功能封装为独立节点，松耦合 |

### 3. ROS 版本

| 版本 | Ubuntu | 状态 | 推荐度 |
|------|--------|------|--------|
| Foxy | 20.04 | EOL | ⭐ |
| **Humble** | **22.04** | **LTS** | **⭐⭐⭐ 本仓库选定** |
| Iron | 22.04 | EOL | ⭐ |
| Jazzy | 24.04 | LTS | ⭐⭐⭐ 最新稳定版 |

> **决定**：直接上 ROS2 **Humble**（22.04 LTS，2027 年 5 月前维护）。ROS1（Noetic）已停止维护（2025.04 EOL），不再学习。

### 4. ROS 核心概念（先建立印象）

```
   ┌────────┐  发布   ┌──────────────────┐  订阅   ┌────────┐
   │ Node A │ ──────► │  Topic: /sensor  │ ──────► │ Node B │
   │ (传感器)│        │  (异步·多对多广播) │        │ (控制) │
   └────────┘        └──────────────────┘        └────────┘
        ▲                                              │
        │──────────── Service: /get_status ────────────┤
                     (同步·一问一答)

   ROS2 没有 Master：节点基于 DDS 自动互相发现
```

- **Node（节点）**：执行计算的进程，最小执行单元
- **Topic（话题）**：节点间异步通信的发布/订阅通道
- **Message（消息）**：话题中传输的数据结构
- **Service（服务）**：节点间同步通信的请求/响应机制
- **Action（动作）**：长任务通信：Goal + Feedback + Result + Cancel

### 5. ROS 的优缺点

**优点**：
- 模块化设计，易于复用代码
- 丰富的算法库和工具
- 强大的仿真环境（Gazebo）
- 活跃的社区和大量教程

**缺点**：
- 实时性较差（非硬实时）
- 学习曲线较陡
- 系统资源占用较大
- 版本碎片化

---

## 💻 快速体验

```bash
# 安装 ROS2 Humble（Ubuntu 22.04）
# 参考官方安装指南：https://docs.ros.org/en/humble/Installation.html

# 终端 1 - 运行小海龟（ROS2 不需要 roscore）
ros2 run turtlesim turtlesim_node

# 终端 2 - 键盘控制
ros2 run turtlesim turtle_teleop_key

# 查看节点列表
ros2 node list

# 查看话题列表
ros2 topic list

# 查看话题数据
ros2 topic echo /turtle1/pose
```

---

## ✏️ 练习任务

### 练习 1：体验小海龟
按照上面的命令启动 turtlesim，用键盘控制海龟移动，观察：
- 节点的启动和关闭
- 话题的数据流
- 使用 `rqt_graph` 查看节点关系图

### 练习 2：ROS 命令探索
尝试以下命令，理解每个命令的作用：
```bash
ros2 node info /turtlesim
ros2 topic info /turtle1/cmd_vel
ros2 service list
ros2 param list
```

### 练习 3：了解 ROS 社区
浏览以下网站，了解 ROS 生态系统：
- [ROS Wiki](http://wiki.ros.org/)
- [ROS Answers](https://answers.ros.org/)
- [GitHub ROS](https://github.com/ros)

---

## ❓ 常见问题

**Q: ROS 和机器人操作系统（如 VxWorks）有什么区别？**
A: ROS 不是实时操作系统，而是运行在 Linux 上的软件框架，依赖 Linux 的调度。硬实时场景需要结合实时内核。

**Q: 为什么直接学 ROS2 而不是 ROS1？**
A: ROS1（Noetic）2025 年已停止维护，ROS2 是唯一的长期方向。虽然 ROS1 中文老教程更多，但 ROS2（Humble）资料已足够，且概念模型更现代（无 Master、DDS 发现），学完不用迁移。
