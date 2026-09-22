# 03 - rqt 与 rosbag

## 🎯 学习目标
- 掌握 rqt 插件工具集
- 掌握 rosbag 记录和回放
- 理解日志和调试工具

---

## 📚 核心知识点

### 1. rqt 工具集

rqt 是基于 Qt 的 ROS GUI 工具框架：

```bash
# 启动 rqt 主界面
ros2 run rqt_gui rqt_gui

# 常用插件（ros2 run 或直接命令名）
ros2 run rqt_graph rqt_graph              # 节点和话题关系图
ros2 run rqt_plot rqt_plot                # 实时数据曲线
ros2 run rqt_console rqt_console          # 日志查看
ros2 run rqt_reconfigure rqt_reconfigure  # 动态参数调节
ros2 run rqt_image_view rqt_image_view    # 图像查看
ros2 run rqt_bag rqt_bag                  # bag 文件可视化
ros2 run rqt_topic rqt_topic              # 话题监控
ros2 run rqt_tf_tree rqt_tf_tree          # TF 树可视化
```

#### rqt_plot 使用
```bash
# 绘制话题字段
ros2 run rqt_plot rqt_plot /turtle1/pose/x
ros2 run rqt_plot rqt_plot /turtle1/pose/x /turtle1/pose/y   # 多条曲线
```

#### rqt_console 使用
```bash
# 启动日志查看器
ros2 run rqt_console rqt_console

# 代码中的日志级别（RCLCPP 系列宏）
RCLCPP_DEBUG(get_logger(), "debug info");    // 调试
RCLCPP_INFO(get_logger(), "normal info");    // 信息
RCLCPP_WARN(get_logger(), "warning!");       // 警告
RCLCPP_ERROR(get_logger(), "error!");        // 错误
RCLCPP_FATAL(get_logger(), "fatal error!");  // 致命
```

### 2. ros2 bag

#### 记录
```bash
# 记录所有话题
ros2 bag record -a

# 记录指定话题（生成一个目录，如 rosbag2_2026_09_22/）
ros2 bag record /tf /scan /odom

# 指定输出目录名
ros2 bag record -o session1 /scan

# 选择存储格式（默认 sqlite3，推荐 mcap）
ros2 bag record -s mcap /scan
```

#### 回放与信息
```bash
# 基本信息
ros2 bag info session1

# 回放
ros2 bag play session1

# 倍速回放
ros2 bag play session1 -r 2    # 2 倍速
ros2 bag play session1 -r 0.5  # 半速

# 循环回放
ros2 bag play session1 -l

# 指定时间范围
ros2 bag play session1 --start-offset 10   # 从 10s 开始

# 速率限制/暂停
ros2 bag play session1 --pause             # 启动即暂停，按空格继续
```

### 3. 日志系统

```cpp
// 日志级别
RCLCPP_DEBUG(node->get_logger(), "debug");
RCLCPP_INFO(node->get_logger(), "info");
RCLCPP_WARN(node->get_logger(), "warn");
RCLCPP_ERROR(node->get_logger(), "error");

// 一次性日志
RCLCPP_INFO_ONCE(node->get_logger(), "once");

// 节流日志（每 1000ms 最多打一次）
RCLCPP_INFO_THROTTLE(node->get_logger(), *node->get_clock(), 1000, "1Hz max");
```

---

## 💻 动手实验

### 实验 1：rqt 监控
```bash
# 终端 1：启动小海龟
ros2 run turtlesim turtlesim_node
ros2 run turtlesim turtle_teleop_key

# 终端 2：画曲线
ros2 run rqt_plot rqt_plot /turtle1/pose/x /turtle1/pose/y /turtle1/pose/theta

# 终端 3：看日志
ros2 run rqt_console rqt_console
```

### 实验 2：ros2 bag 记录回放
```bash
# 记录小海龟运行（生成 turtle_session/ 目录）
ros2 bag record -o turtle_session /turtle1/pose /turtle1/cmd_vel

# 控制小海龟移动，然后 Ctrl+C 停止记录

# 重启 turtlesim（不启动 teleop）
ros2 run turtlesim turtlesim_node

# 回放
ros2 bag play turtle_session
```

---

## ✏️ 练习任务

### 练习 1：数据采集脚本
编写一个脚本，自动记录特定话题并在一定时间后停止。

### 练习 2：数据分析
用 Python 读取 rosbag，提取数据并绘制图表（位置轨迹、速度曲线等）。

### 练习 3：日志系统
为你的节点添加完善的日志系统，支持：
- 不同级别的日志
- 日志文件输出
- 运行时级别切换

---

## ❓ 常见问题

**Q: bag 文件太大？**
A: 只记录必要话题（高频点云/图像最占空间），或换 mcap 格式（`-s mcap`），或按大小分割。

**Q: bag 回放时时间戳不对？**
A: 记录时加 `--use-sim-time` 相关处理；确保回放节点使用 `/clock`（launch 中设 `use_sim_time:=True`）。

**Q: rqt_plot 不显示数据？**
A: 检查话题是否有数据（`ros2 topic hz`），检查字段路径是否正确。
