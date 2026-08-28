# 01 - RViz 可视化工具

## 🎯 学习目标
- 掌握 RViz 的基本操作
- 能够添加和配置各种显示插件
- 理解 TF 可视化

---

## 📚 核心知识点

### 1. RViz 简介

RViz 是 ROS 的 3D 可视化工具，用于显示：
- 机器人模型（URDF）
- 传感器数据（激光、点云、图像）
- 路径和轨迹
- TF 坐标变换树
- 地图和导航信息

### 2. 启动 RViz

```bash
# ROS1
rosrun rviz rviz

# ROS2
ros2 run rviz2 rviz2

# 加载保存的配置
rviz -d config/my_config.rviz
```

### 3. 常用显示插件

| 插件 | 用途 | 订阅话题 |
|------|------|----------|
| **RobotModel** | 显示机器人模型 | `/robot_description` |
| **TF** | 显示坐标变换树 | `/tf`, `/tf_static` |
| **LaserScan** | 显示激光雷达数据 | `/scan` |
| **PointCloud2** | 显示点云 | `/point_cloud` |
| **Image** | 显示图像 | `/camera/image_raw` |
| **Path** | 显示规划路径 | `/plan` |
| **Odometry** | 显示里程计 | `/odom` |
| **Map** | 显示栅格地图 | `/map` |
| **Marker** | 显示自定义标记 | `/visualization_marker` |

### 4. 添加显示

1. 点击左下角 "Add" 按钮
2. 选择插件类型
3. 在左侧配置面板设置：
   - **Topic**：订阅的话题名
   - **Fixed Frame**：参考坐标系（通常是 `map` 或 `odom`）
   - 颜色、大小、样式等

### 5. 保存和加载配置

```bash
# 保存配置
File → Save Config As → my_config.rviz

# 在 launch 中加载
<node pkg="rviz" type="rviz" name="rviz" 
      args="-d $(find my_pkg)/config/my_config.rviz" />
```

### 6. 常用操作

| 操作 | 方法 |
|------|------|
| 旋转视角 | 左键拖动 |
| 平移视角 | 中键拖动 |
| 缩放 | 滚轮 / 右键拖动 |
| 选择物体 | Shift + 左键 |
| 2D 导航目标 | 顶部工具栏 "2D Nav Goal" |
| 2D 位姿估计 | 顶部工具栏 "2D Pose Estimate" |

---

## 💻 动手实验

### 实验 1：显示 Turtle
```bash
roslaunch turtlebot3_fake turtlebot3_fake.launch
rviz -d `rospack find turtlebot3_description`/rviz/model.rviz
```

### 实验 2：显示传感器数据
```bash
# 启动 Gazebo 仿真（带传感器）
roslaunch turtlebot3_gazebo turtlebot3_world.launch

# RViz 中添加：
# - LaserScan: /scan
# - Image: /camera/image_raw
# - PointCloud2: /camera/depth/points
```

### 实验 3：自定义 Marker
```cpp
#include <visualization_msgs/Marker.h>

visualization_msgs::Marker marker;
marker.header.frame_id = "map";
marker.header.stamp = ros::Time::now();
marker.ns = "my_markers";
marker.id = 0;
marker.type = visualization_msgs::Marker::SPHERE;
marker.action = visualization_msgs::Marker::ADD;
marker.pose.position.x = 1.0;
marker.pose.position.y = 2.0;
marker.pose.position.z = 0.0;
marker.scale.x = 0.5;
marker.scale.y = 0.5;
marker.scale.z = 0.5;
marker.color.r = 1.0;
marker.color.g = 0.0;
marker.color.b = 0.0;
marker.color.a = 1.0;

pub.publish(marker);
```

---

## ✏️ 练习任务

### 练习 1：创建 RViz 配置
为你的机器人项目创建一套完整的 RViz 配置，包含所有关键显示。

### 练习 2：Marker 阵列
用 `MarkerArray` 在 RViz 中显示机器人的路径历史。

### 练习 3：交互式 Marker
使用 `InteractiveMarker` 实现可在 RViz 中拖拽的控制点。

---

## ❓ 常见问题

**Q: RViz 报错 "Fixed Frame [map] does not exist"？**
A: 没有发布 `/tf` 变换。检查是否有节点发布 `map` 到其他 frame 的变换。

**Q: 激光数据不显示？**
A: 检查：1) Topic 是否正确；2) Fixed Frame 是否匹配；3) 数据时间戳是否有效。
