# 02 - SLAM 建图

## 🎯 学习目标
- 理解 SLAM 的基本概念
- 掌握 Gmapping 和 Cartographer 的使用
- 能够保存和加载地图

---

## 📚 核心知识点

### 1. SLAM 简介

**SLAM (Simultaneous Localization and Mapping)**：同时定位与建图
- 机器人未知环境中移动
- 同时估计自身位置（Localization）
- 同时构建环境地图（Mapping）

### 2. 常用 SLAM 算法

| 算法 | 传感器 | 特点 | ROS 包 |
|------|--------|------|--------|
| **Gmapping** | 2D 激光 | 经典、稳定 | `gmapping` |
| **Cartographer** | 2D/3D 激光 | Google 出品，效果好 | `cartographer` |
| **Hector** | 2D 激光 | 无需里程计 | `hector_slam` |
| **ORB-SLAM** | 摄像头 | 视觉 SLAM | `orb_slam2_ros` |
| **RTAB-Map** | 摄像头+激光 | 回环检测强 | `rtabmap_ros` |

### 3. Gmapping（ROS1）

```bash
# 安装
sudo apt install ros-noetic-slam-gmapping

# 运行（需要激光雷达 + 里程计）
roslaunch turtlebot3_slam turtlebot3_slam.launch slam_methods:=gmapping

# 键盘控制建图
roslaunch turtlebot3_teleop turtlebot3_teleop_key.launch
```

#### 主要参数
```xml
<node pkg="gmapping" type="slam_gmapping" name="slam_gmapping">
  <param name="maxUrange" value="8.0"/>        <!-- 最大可用范围 -->
  <param name="delta" value="0.05"/>           <!-- 地图分辨率 -->
  <param name="xmin" value="-10.0"/>
  <param name="xmax" value="10.0"/>
  <param name="ymin" value="-10.0"/>
  <param name="ymax" value="10.0"/>
</node>
```

### 4. Cartographer（推荐）

```bash
# 安装
sudo apt install ros-noetic-cartographer-ros

# 运行
roslaunch turtlebot3_slam turtlebot3_slam.launch slam_methods:=cartographer
```

### 5. 保存和加载地图

```bash
# 保存地图（ROS1）
rosrun map_server map_saver -f my_map

# 生成文件：
# my_map.pgm  - 地图图像（灰度）
# my_map.yaml - 地图元信息

# 加载地图
rosrun map_server map_server my_map.yaml
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

### 6. 建图技巧

1. **速度要慢**：移动太快会导致扫描匹配失败
2. **覆盖全面**：尽量走遍整个环境
3. **回环**：回到起点可以修正累积误差
4. **特征丰富**：避免长走廊等特征少的环境

---

## 💻 动手实验

### 实验 1：Gazebo 中建图
```bash
# 启动仿真环境
roslaunch turtlebot3_gazebo turtlebot3_world.launch

# 启动 SLAM
roslaunch turtlebot3_slam turtlebot3_slam.launch

# 键盘控制
roslaunch turtlebot3_teleop turtlebot3_teleop_key.launch
```

控制机器人走遍环境，观察 RViz 中的地图构建过程。

### 实验 2：保存和查看地图
```bash
# 保存
rosrun map_server map_saver -f my_map

# 查看 pgm 文件
# 可以用图像查看器打开，黑色=障碍物，白色=空闲，灰色=未知
```

### 实验 3：加载地图导航
```bash
# 加载已有地图
rosrun map_server map_server my_map.yaml

# 在 RViz 中可以看到地图，用 2D Pose Estimate 定位
```

---

## ✏️ 练习任务

### 练习 1：参数调优
调整 Gmapping 的分辨率和范围参数，观察对建图质量和速度的影响。

### 练习 2：多方法对比
用 Gmapping、Cartographer、Hector 分别建图，对比效果。

### 练习 3：回环测试
故意走一个大回路，观察回环检测对地图质量的改善。

---

## ❓ 常见问题

**Q: 建图时地图漂移？**
A: 1) 降低移动速度；2) 检查里程计是否准确；3) 增加回环路径。

**Q: 地图分辨率设多少合适？**
A: 室内 0.05m（5cm）；室外或大范围可设 0.1m。分辨率越高，计算量越大。

**Q: 没有里程计能用 SLAM 吗？**
A: Hector SLAM 不需要里程计；Cartographer 也可以纯激光运行，但有里程计效果更好。
