# 04 - 第一个 ROS 程序：小海龟

## 🎯 学习目标
- 理解 ROS 节点、话题、消息的概念
- 掌握常用 ROS 命令行工具
- 能够分析节点间的通信关系

---

## 📚 核心知识点

### 1. 运行小海龟

```bash
# 终端 1：启动 ROS Master（ROS1 需要，ROS2 不需要显式启动）
roscore

# 终端 2：启动海龟仿真器
rosrun turtlesim turtlesim_node

# 终端 3：启动键盘控制节点
rosrun turtlesim turtle_teleop_key
```

### 2. ROS1 核心命令

#### 节点相关
```bash
rosnode list                    # 列出所有节点
rosnode info /turtlesim         # 查看节点信息
rosnode ping /turtlesim         # 测试节点连通性
rosnode kill /turtlesim         # 关闭节点
```

#### 话题相关
```bash
rostopic list                   # 列出所有话题
rostopic info /turtle1/cmd_vel  # 查看话题信息
rostopic echo /turtle1/pose     # 实时显示话题数据
rostopic hz /turtle1/pose       # 统计发布频率
rostopic bw /turtle1/pose       # 统计带宽占用
rostopic pub /turtle1/cmd_vel geometry_msgs/Twist \
    "{linear: {x: 1.0}, angular: {z: 0.5}}"   # 发布消息
```

#### 消息相关
```bash
rosmsg list                     # 列出所有消息类型
rosmsg show geometry_msgs/Twist # 查看消息结构
rosmsg md5 geometry_msgs/Twist  # 查看消息 md5
```

#### 服务相关
```bash
rosservice list                 # 列出所有服务
rosservice info /spawn          # 查看服务信息
rosservice call /spawn 5 5 0.5 "turtle2"   # 调用服务生成新海龟
```

#### 参数相关
```bash
rosparam list                   # 列出所有参数
rosparam get /background_b      # 获取参数值
rosparam set /background_b 100  # 设置参数值
rosparam dump params.yaml       # 导出参数
```

### 3. ROS2 核心命令

```bash
# 节点
ros2 node list
ros2 node info /turtlesim

# 话题
ros2 topic list
ros2 topic info /turtle1/cmd_vel
ros2 topic echo /turtle1/pose
ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist \
    "{linear: {x: 1.0}, angular: {z: 0.5}}"

# 服务
ros2 service list
ros2 service type /spawn
ros2 service call /spawn turtlesim/srv/Spawn \
    "{x: 5, y: 5, theta: 0, name: 'turtle2'}"

# 参数
ros2 param list
ros2 param get /turtlesim background_b
ros2 param set /turtlesim background_b 100
```

### 4. 小海龟话题分析

```
/turtle1/cmd_vel    (geometry_msgs/Twist)
    ├── linear.x    # 前后速度 (m/s)
    ├── linear.y    # 左右速度 (m/s)
    ├── linear.z    # 上下速度 (m/s)
    ├── angular.x   # 绕 x 轴旋转
    ├── angular.y   # 绕 y 轴旋转
    └── angular.z   # 旋转速度 (rad/s)

/turtle1/pose       (turtlesim/Pose)
    ├── x           # x 坐标
    ├── y           # y 坐标
    ├── theta       # 朝向角度
    ├── linear_velocity
    └── angular_velocity
```

### 5. rqt_graph 可视化

```bash
# ROS1
rosrun rqt_graph rqt_graph

# ROS2
ros2 run rqt_graph rqt_graph
```

可以看到节点和话题的连接关系图。

---

## 💻 动手实验

### 实验 1：用命令行控制海龟
```bash
# 持续发布速度命令（1Hz）
rostopic pub -r 1 /turtle1/cmd_vel geometry_msgs/Twist \
    "{linear: {x: 2.0}, angular: {z: 1.0}}"
```

### 实验 2：生成多只海龟
```bash
rosservice call /spawn 2 2 0 "turtle2"
rosservice call /spawn 8 8 1.57 "turtle3"
```

### 实验 3：改变背景颜色
```bash
rosparam set /background_r 150
rosparam set /background_g 150
rosparam set /background_b 150
rosservice call /clear
```

### 实验 4：清除轨迹
```bash
rosservice call /clear
```

---

## ✏️ 练习任务

### 练习 1：话题监控
使用 `rostopic echo` 观察：
- 不动键盘时 `/turtle1/pose` 的数据
- 按不同方向键时 `/turtle1/cmd_vel` 的变化

### 练习 2：节点通信图
启动 `rqt_graph`，然后：
1. 只启动 turtlesim_node，观察图
2. 再启动 turtle_teleop_key，观察变化
3. 启动 rostopic echo，观察变化

### 练习 3：消息结构分析
```bash
rosmsg show geometry_msgs/Twist
rosmsg show turtlesim/Pose
```
理解每个字段的含义。

---

## ❓ 常见问题

**Q: `roscore` 和 `rosrun` 有什么区别？**
A: `roscore` 启动 ROS Master（名字服务）；`rosrun` 运行某个包中的节点。

**Q: 为什么有时需要先 `source` setup.bash？**
A: 为了让当前终端知道 ROS 命令和包的位置。添加到 `~/.bashrc` 后新开终端会自动加载。

**Q: ROS2 不需要 `roscore`？**
A: ROS2 使用 DDS 作为中间件，分布式发现，不需要中央 Master。
