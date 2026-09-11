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

## 4. 调试先查的环境变量

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

（暂无）
