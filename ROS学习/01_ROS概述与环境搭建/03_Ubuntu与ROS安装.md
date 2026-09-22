# 03 - Ubuntu 与 ROS 安装

## 🎯 学习目标
- 完成 Ubuntu 和 ROS 的安装
- 配置 ROS 环境
- 验证安装成功

---

## 📚 核心知识点

### 1. 安装 Ubuntu（若还没有）

#### 方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **双系统** | 性能最好 | 分区麻烦 | ⭐⭐⭐ |
| **虚拟机** | 方便切换 | 性能损耗、Gazebo 可能卡 | ⭐⭐ |
| **WSL2** | Windows 用户友好 | Gazebo 有兼容问题 | ⭐ |
| **云服务器** | 无需本地配置 | 无法连接硬件 | ⭐ |

#### 双系统安装要点
1. 下载 Ubuntu ISO（20.04 或 22.04）
2. 制作启动 U 盘（Rufus/Ventoy）
3. 预留至少 50GB 空间
4. 关闭 Windows 快速启动
5. 关闭 Secure Boot（某些情况）

### 2. 安装 ROS2 Humble（Ubuntu 22.04）

```bash
# 1. 设置语言环境
locale
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

# 2. 添加软件源
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 3. 安装
sudo apt update
sudo apt install ros-humble-desktop

# 4. 环境配置
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc

# 5. 安装开发工具
sudo apt install ros-dev-tools
```

### 3. 创建工作空间（ROS2）

```bash
# 创建工作空间
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/
colcon build

# 配置环境
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## 💻 安装验证

```bash
# 终端 1：运行小海龟
ros2 run turtlesim turtlesim_node

# 终端 2：键盘控制
ros2 run turtlesim turtle_teleop_key

# 终端 3：查看节点和话题
ros2 node list
ros2 topic list
ros2 run rqt_graph rqt_graph
```

---

## ✏️ 练习任务

### 练习 1：确认安装
运行上述验证命令，确认 ROS 安装成功。截图保存小海龟运行画面。

### 练习 2：环境变量检查
```bash
echo $ROS_DISTRO      # 应输出 humble
which ros2            # 命令位置
```

### 练习 3：rqt 工具探索
```bash
ros2 run rqt_gui rqt_gui
```
探索 rqt 的插件：Node Graph、Topic Monitor、Message Publisher 等。

---

## ❓ 常见问题

**Q: `rosdep` 相关命令报错？**
A: ROS2 用 `rosdep init` / `rosdep update` 初始化，报错多半是网络问题，尝试手机热点或代理。

**Q: Gazebo 启动黑屏/崩溃？**
A: 虚拟机常见问题，建议用双系统。如果是独立显卡，检查驱动是否安装。

**Q: 能同时装 ROS1 和 ROS2 吗？**
A: 可以共存，但**不要同时 source 两个发行版**的环境，一个终端只激活一个：`source /opt/ros/humble/setup.bash`（本仓库只学 ROS2）。
