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

### 2. 安装 ROS Noetic（Ubuntu 20.04）

```bash
# 1. 设置软件源
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'

# 2. 添加密钥
sudo apt install curl
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -

# 3. 更新索引
sudo apt update

# 4. 安装完整版 ROS
sudo apt install ros-noetic-desktop-full

# 5. 环境配置（每次新开终端自动加载）
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
source ~/.bashrc

# 6. 安装构建依赖
sudo apt install python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool build-essential
sudo rosdep init
rosdep update
```

### 3. 安装 ROS2 Humble（Ubuntu 22.04）

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

### 4. 创建工作空间（ROS1）

```bash
# 创建工作空间
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/
catkin_make

# 配置环境
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 5. 创建工作空间（ROS2）

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

### ROS1 验证
```bash
# 终端 1：启动 Master
roscore

# 终端 2：运行小海龟
rosrun turtlesim turtlesim_node

# 终端 3：键盘控制
rosrun turtlesim turtle_teleop_key

# 终端 4：查看节点和话题
rosnode list
rostopic list
rqt_graph
```

### ROS2 验证
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
echo $ROS_DISTRO      # 应输出 noetic 或 humble
echo $ROS_ROOT        # ROS 安装路径
which roscore         # 命令位置
```

### 练习 3：rqt 工具探索
```bash
# ROS1
rqt

# ROS2
ros2 run rqt_gui rqt_gui
```
探索 rqt 的插件：Node Graph、Topic Monitor、Message Publisher 等。

---

## ❓ 常见问题

**Q: `rosdep init` 报错？**
A: 可能是网络问题，尝试使用手机热点或配置代理。也可以手动下载 rosdistro。

**Q: Gazebo 启动黑屏/崩溃？**
A: 虚拟机常见问题，建议用双系统。如果是独立显卡，检查驱动是否安装。

**Q: 如何切换 ROS1 和 ROS2？**
```bash
# 临时切换（当前终端）
source /opt/ros/noetic/setup.bash   # ROS1
source /opt/ros/humble/setup.bash    # ROS2

# 不要同时 source 两个！
```
