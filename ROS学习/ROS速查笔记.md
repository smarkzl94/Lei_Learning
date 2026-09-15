# 📓 ROS 速查笔记

> 高频命令和易忘概念的个人速查手册，和 [知识盲区](../知识盲区.md) 配合使用。
> 用法：写代码卡住时先查这里；这里没有的再记入知识盲区。

---

## 1. 三板斧（工作空间生命周期，最高频）

```bash
# ① 建：创建工作空间
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src && catkin_init_workspace

# ② 编：编译（改了代码就跑这个）
cd ~/catkin_ws && catkin_make
catkin_make -j4                     # 4 线程加速
rm -rf build devel && catkin_make   # 彻底重编（玄学问题先试试这个）

# ③ 配：加载环境（只需一次，写进 .bashrc）
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## 2. 工作空间目录结构

```
~/catkin_ws/
├── src/     ← 唯一要碰的目录：自己写的功能包放这里
├── build/   ← 编译中间文件（别管，出问题可删）
└── devel/   ← 编译产物 + setup.bash
```

---

## 3. Overlay（叠加）原则

**后 source 的覆盖先 source 的**，同左往右查找：

```bash
source /opt/ros/noetic/setup.bash      # 第1层：系统包
source ~/catkin_ws/devel/setup.bash    # 第2层：自己的包（同名时覆盖系统）
echo $ROS_PACKAGE_PATH
# → /home/lei/catkin_ws/src:/opt/ros/noetic/share   （左优先）
```

---

## 4. ROS 五大核心概念（八股文，面试/复盘必背）

| 概念 | 一句话定义 | 类比 | 通信方式 |
|------|-----------|------|----------|
| **Node 节点** | 执行计算的最小进程单元 | 节目组 | - |
| **Topic 话题** | 节点间**异步**的发布/订阅通道 | 电视频道 | 单向、持续广播、多对多 |
| **Message 消息** | Topic 里传输的数据结构（.msg 定义） | 频道节目内容 | - |
| **Service 服务** | 节点间**同步**的请求/响应 | 打电话 | 双向、一问一答、一对一 |
| **ROS Master** | 名字注册与查询中心 | 电话簿 | 只负责牵线，**数据不经过它** |

必背要点：

1. **Topic vs Service**：Topic 是"一直广播，爱听不听"（传感器数据）；Service 是"问了才答，必有回应"（拍照、查询）。
2. **Master 只管注册**：节点启动时向 Master 注册自己的地址，之后双方**点对点直连**，Master 挂了已建立的通信不受影响（但不能启动新节点）。
3. **松耦合**：发布者和订阅者互不知道对方存在，只认话题名。

配套命令：

```bash
rosnode list / info <节点>     # 节点
rostopic list / echo <话题>    # 话题
rosservice list / call <服务>  # 服务
rosmsg show <消息类型>         # 消息
```

---

## 5. 调试先查的环境变量

| 命令 | 用途 |
|------|------|
| `echo $ROS_PACKAGE_PATH` | 包搜索路径（"找不到包"先看它 source 没） |
| `echo $ROS_DISTRO` | 确认版本（应为 noetic） |
| `rosversion -d` | 同上 |

---

## 5. 海龟三件套（环境自检标准流程）

```bash
roscore                              # 终端1：必须先启动
rosrun turtlesim turtlesim_node      # 终端2：仿真器（WSLg 弹窗）
rosrun turtlesim turtle_teleop_key   # 终端3：键盘控制（方向键）
```

配套检查命令：

```bash
rosnode list        # 看活着的节点
rostopic list       # 看话题
rqt_graph           # 看节点关系图
```

---

## 6. 常见报错速查

| 现象 | 原因 | 解法 |
|------|------|------|
| `command not found: roscore` | 没 source | `source /opt/ros/noetic/setup.bash` 或重开终端 |
| `roscore` 启动失败说 already running | 已有主节点 | `killall -9 roscore rosmaster` 或重启 WSL |
| `rospack find xxx` 找不到自己的包 | 没 catkin_make 或没 source devel | 编译 + `source devel/setup.bash` |
| 改了代码运行结果没变 | 没重新编译 | `catkin_make` 后再跑 |
| WSL 里 `wsl打不开/一闪而过` | 虚拟机平台功能没开 | 管理员 PowerShell: `dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart` 后重启 |

---

## 记录区

> 以下由学习过程中追加（格式同 [知识盲区](../知识盲区.md)）

### ROS2 节点一生 · 五步链（建包→编译→运行全链路）

- **类型**：流程梳理
- **发现日期**：2026-09-16
- **关联知识点**：ROS 02 章 工作空间与功能包（03 创建功能包 / 04 launch）

**问题描述**：
建包、写代码、colcon build、source、ros2 run 分开看都懂，但串不起来——不知道每一步的产物是什么、出错该回查哪一步。

**正解/笔记**：

```
① 建包    ros2 pkg create my_package --build-type ament_cmake --node-name my_node
          └─→ 在 src/ 下生成  package.xml + CMakeLists.txt + src/my_node.cpp

② 写代码  编辑 my_node.cpp（init → Node → 循环 → shutdown）

③ 编译    colcon build
          └─→ 读两个配置文件 → 编译 → 放进 install/

④ 注册    source install/setup.bash
          └─→ 告诉终端：my_package 的存在、my_node 的路径（每个新终端都要！）

⑤ 运行    ros2 run my_package my_node
          └─→ 从 install/lib/my_package/ 找到可执行文件，启动节点
```

**排错对照表**：

| 现象 | 回查步骤 |
|------|---------|
| ros2 run 找不到包 | ④ source（99% 是这个） |
| 编译报错 | ② 代码 或 ① 的 package.xml / CMakeLists.txt |
| 节点启动无反应 | ⑤ spin 漏写 / 话题没对上 |
| launch 找不到文件 | ③ CMakeLists 漏 install(DIRECTORY launch ...) |

**核心记忆**：①② 是"写"，③ 是"编译"，④ 是"环境"，⑤ 是"跑"。launch 文件 = 把 ⑤ 自动化 + 附加参数/重映射。
（配图画布：「ROS 学习图解」Canvas 中的《ROS2 节点一生·五步链》）

---

### Topic 发布/订阅通信模型（多对多异步广播）

- **类型**：概念梳理
- **发现日期**：2026-09-16
- **关联知识点**：ROS 03 章 核心通信机制（01 话题 Topic）

**模型要点**：

```
Publisher A ─┐
Publisher B ─┼─→ /chatter (std_msgs/msg/String) ─→ Subscriber X
             │      ↑ Topic：单向·异步·多对多        ─→ Subscriber Y
             │                                      ─→ ros2 topic echo（也是订阅者）
```

| 特性 | 含义 |
|------|------|
| 单向 | 数据只从 Pub → Sub，没有回程 |
| 异步 | 发布者 publish() 完就走，不等订阅者处理 |
| 解耦 | 双方只认话题名，互不知道对方存在 |
| 多对多 | N 个发布者、M 个订阅者同时接同一个 Topic |

**与 Service 的边界**：要"一问一答"（如 /spawn 生成海龟）不能用 Topic，要用 Service（03-2）。
（配图画布：「ROS 学习图解」Canvas 中的《ROS Topic 多对多通信模型》）

---

### RCLCPP_INFO 的 printf 风格格式化日志

- **类型**：语法不懂
- **发现日期**：2026-09-16
- **关联知识点**：ROS 03 章 01 话题（节点打印）

**问题描述**：
`RCLCPP_INFO(get_logger(), "Publishing: '%s'", msg.data.c_str())` 这种写法没见过，不知道各部分是什么。

**正解/笔记**：

```cpp
RCLCPP_INFO( get_logger(), "Publishing: '%s'", msg.data.c_str() )
//   ④宏        ①日志器         ②格式字符串        ③填入的数据
```

- ① `get_logger()`：取本节点的日志器，日志要知道是哪个节点打的
- ② 格式字符串：和 `printf` 完全同一套，`%s`=字符串 `%d`=整数 `%f`=浮点 `%zu`=size_t
- ③ `msg.data.c_str()`：`%s` 只认 `const char*`，std::string 要转一下
- ④ `RCLCPP_INFO` 是**宏**，自动带级别 + 时间戳 + 节点名前缀；WARN/ERROR 用法相同

**为什么不用 std::cout**：日志要分级过滤、自动带前缀，cout 做不到。
