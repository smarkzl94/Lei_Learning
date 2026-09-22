# 02 - SLAM 建图

## 🎯 学习目标
- 理解 SLAM 的基本概念
- 掌握 slam_toolbox（ROS2 官方推荐的 2D 激光 SLAM）
- 能够保存和加载地图

---

## 📚 核心知识点

### 1. SLAM 简介

**SLAM (Simultaneous Localization and Mapping)**：同时定位与建图
- 机器人未知环境中移动
- 同时估计自身位置（Localization）
- 同时构建环境地图（Mapping）

### 2. 常用 SLAM 算法（ROS2 生态）

| 算法 | 传感器 | 特点 | ROS2 包 |
|------|--------|------|--------|
| **slam_toolbox** | 2D 激光 | **ROS2 官方推荐**，基于图优化 | `slam_toolbox` |
| **Cartographer** | 2D/3D 激光 | Google 出品，效果好 | `cartographer_ros` |
| **RTAB-Map** | 摄像头+激光 | 回环检测强，支持 3D | `rtabmap_ros` |
| lidarslam_ros | 3D 激光 | 3D 激光 SLAM | `lidarslam_ros` |

> 注：Gmapping / Hector 是 ROS1 时代的包，ROS2 无官方移植，直接用 slam_toolbox 替代。

### 3. slam_toolbox（主推）

```bash
# 安装
sudo apt install ros-humble-slam-toolbox

# TurtleBot3 一键建图（slam_method 可选 slam_toolbox / cartographer）
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_slam slam.launch.py slam_method:=slam_toolbox

# 键盘控制建图（另一个终端）
ros2 launch turtlebot3_teleop teleop_keyboard.launch.py
```

#### 主要参数（config/mapper_params_online_async.yaml）
```yaml
slam_toolbox:
  ros__parameters:
    solver_plugin: solver_plugins::CeresSolver
    mode: mapping            # mapping / localization / lifelong
    resolution: 0.05         # 地图分辨率（米/格）
    max_laser_range: 12.0    # 激光最大有效范围
    minimum_time_interval: 0.5
    transform_timeout: 0.2
    map_update_interval: 5.0
```

### 4. 保存和加载地图

```bash
# 保存地图（生成 my_map.pgm + my_map.yaml）
ros2 run nav2_map_server map_saver_cli -f my_map

# 加载地图（nav2 的 map_server 是生命周期节点，启动后要用 ros2 lifecycle set 激活）
ros2 run nav2_map_server map_server --ros-args -p yaml_filename:=my_map.yaml
ros2 lifecycle set /map_server configure
ros2 lifecycle set /map_server activate
```

#### 地图 YAML 格式
```yaml
# my_map.yaml
image: my_map.pgm
resolution: 0.050000
origin: [-10.000000, -10.000000, 0.000000]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.196
```

### 5. 建图技巧

1. **速度要慢**：移动太快会导致扫描匹配失败
2. **覆盖全面**：尽量走遍整个环境
3. **回环**：回到起点可以修正累积误差
4. **特征丰富**：避免长走廊等特征少的环境

---

## 💻 动手实验

### 实验 1：Gazebo 中建图
```bash
# 启动仿真环境
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# 启动 SLAM（另一个终端）
ros2 launch turtlebot3_slam slam.launch.py slam_method:=slam_toolbox

# 键盘控制（第三个终端）
ros2 launch turtlebot3_teleop teleop_keyboard.launch.py
```

控制机器人走遍环境，观察 RViz 中的地图构建过程。

### 实验 2：保存和查看地图
```bash
# 保存
ros2 run nav2_map_server map_saver_cli -f my_map

# 查看 pgm 文件
# 可以用图像查看器打开，黑色=障碍物，白色=空闲，灰色=未知
```

### 实验 3：加载地图导航
```bash
# 用 nav2 的 bringup 加载地图（后面导航章节详解）
ros2 launch nav2_bringup bringup_launch.py map:=/path/to/my_map.yaml

# 在 RViz 中可以看到地图，用 2D Pose Estimate 定位
```

---

## ✏️ 练习任务

### 练习 1：参数调优
调整 slam_toolbox 的 resolution 和 max_laser_range 参数，观察对建图质量和速度的影响。

### 练习 2：多方法对比
用 slam_toolbox 和 cartographer 分别建图（`slam_method:=cartographer`），对比效果。

### 练习 3：回环测试
故意走一个大回路，观察回环检测对地图质量的改善。

---

## ❓ 常见问题

**Q: 建图时地图漂移？**
A: 1) 降低移动速度；2) 检查里程计是否准确；3) 增加回环路径。

**Q: 地图分辨率设多少合适？**
A: 室内 0.05m（5cm）；室外或大范围可设 0.1m。分辨率越高，计算量越大。

**Q: ROS1 教程里的 Gmapping 在哪？**
A: Gmapping 没有 ROS2 官方移植。slam_toolbox 是它的现代化替代，TurtleBot3 官方 ROS2 教程也用它。
