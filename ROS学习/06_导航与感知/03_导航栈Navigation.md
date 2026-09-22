# 03 - 导航栈 Navigation（Nav2）

## 🎯 学习目标
- 理解 ROS2 Nav2 导航栈的架构
- 掌握 Nav2 的配置和使用
- 能够配置代价地图和控制器/规划器

---

## 📚 核心知识点

### 1. Nav2 架构

ROS2 的导航栈叫 **Nav2**（move_base 已被完全取代）：

```
                 ┌──────────────┐
                 │ Goal (x,y,θ) │  ← RViz "Nav2 Goal" / Action Client
                 └──────┬───────┘
                        ▼  (action: NavigateToPose)
              ┌───────────────────┐
              │    bt_navigator   │  行为树：编排整个导航流程
              └────────┬──────────┘
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
 ┌────────────┐ ┌────────────┐ ┌────────────┐
 │planner_server│ │controller_ │ │  behavior  │
 │(全局规划)   │ │ server     │ │ _server    │
 │ GridBased  │ │(局部规划+  │ │(恢复行为:  │
 │            │ │  实时避障) │ │  旋转/清除)│
 │ global_    │ │ FollowPath │ └────────────┘
 │ costmap    │ │ local_     │ ┌────────────┐
 └────────────┘ │ costmap    │ │ waypoint_  │
                └─────┬──────┘ │ follower   │
                      ▼        │(多点巡逻)  │
                ┌────────────┐ └────────────┘
                │  cmd_vel   │
                └────────────┘
```

核心组件：
- **bt_navigator**：行为树导航主控，接收 NavigateToPose 目标
- **planner_server**：全局规划（计算最优路径）
- **controller_server**：局部规划（跟踪路径 + 实时避障），发布 cmd_vel
- **costmap**：不再独立，嵌在 planner/controller server 内部
- **behavior_server**：恢复行为（卡住了转一转、清代价地图）

### 2. 安装和运行

```bash
# 安装
sudo apt install ros-humble-nav2-bringup ros-humble-turtlebot3-navigation2

# TurtleBot3 仿真 + 导航一条龙（推荐入门方式）
export TURTLEBOT3_MODEL=waffle
ros2 launch nav2_bringup tb3_simulation_launch.py

# 已有地图 + 已有仿真的导航
ros2 launch turtlebot3_navigation2 navigation2.launch.py map:=/path/to/map.yaml
```

### 3. 关键配置（nav2_params.yaml，一份文件管全部）

Nav2 把所有参数集中在一份 yaml，核心段落：

```yaml
# ① 局部规划 + 局部代价地图
controller_server:
  ros__parameters:
    controller_frequency: 20.0
    progress_checker_plugin: "progress_checker"
    goal_checker_plugins: ["general_goal_checker"]
    controller_plugins: ["FollowPath"]
    progress_checker:
      plugin: "nav2_controller::SimpleProgressChecker"
      required_movement_radius: 0.5
      movement_time_allowance: 10.0
    general_goal_checker:
      plugin: "nav2_controller::SimpleGoalChecker"
      xy_goal_tolerance: 0.25        # 位置容差（米）
      yaw_goal_tolerance: 0.25       # 角度容差（弧度）

    FollowPath:                       # 局部规划器（DWA 的后继者 DWB）
      plugin: "dwb_core::DWBLocalPlanner"
      min_vel_x: 0.0
      max_vel_x: 0.26                 # 最大线速度
      min_vel_theta: -1.0
      max_vel_theta: 1.0              # 最大角速度
      acc_lim_x: 2.5                  # 线加速度限制
      acc_lim_theta: 3.2              # 角加速度限制
      sim_time: 1.7                   # 前向模拟时间
      vx_samples: 20                  # 速度采样数
      vtheta_samples: 20

    local_costmap:
      global_frame: odom
      robot_base_frame: base_link
      update_frequency: 5.0
      publish_frequency: 2.0
      rolling_window: true            # 滚动窗口跟随机器人
      width: 3.0
      height: 3.0
      resolution: 0.05
      plugins: ["obstacle_layer", "inflation_layer"]
      obstacle_layer:
        plugin: "nav2_costmap_2d::ObstacleLayer"
        observation_sources: scan
        scan:
          topic: /scan
          data_type: "LaserScan"
          robot_base_frame: base_link
          max_obstacle_height: 2.0
          clearing: true
          marking: true
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        cost_scaling_factor: 3.0
        inflation_radius: 0.55        # 膨胀半径

# ② 全局规划 + 全局代价地图
planner_server:
  ros__parameters:
    expected_planner_frequency: 20.0
    planner_plugins: ["GridBased"]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.5
      use_astar: false
      allow_unknown: true

    global_costmap:
      global_frame: map
      robot_base_frame: base_link
      update_frequency: 1.0
      plugins: ["static_layer", "obstacle_layer", "inflation_layer"]
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_subscribe_transient_local: true
      # obstacle_layer / inflation_layer 同上
```

> 机器人轮廓参数改为 `robot_radius: 0.22`（圆形）或在 costmap 里配 `footprint: "[...]"`。

### 4. 发送导航目标

#### RViz
顶部工具栏 **"Nav2 Goal"**（不是 ROS1 的 2D Nav Goal）。

#### 命令行（topic 方式）
```bash
ros2 topic pub /goal_pose geometry_msgs/msg/PoseStamped \
  "{header: {frame_id: 'map'}, pose: {position: {x: 1.0, y: 2.0}, orientation: {w: 1.0}}}"
```

#### C++ 代码（正是你刚学的 Action！）
Nav2 的目标走 **`nav2_msgs::action::NavigateToPose`** Action：

```cpp
#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>
#include <nav2_msgs/action/navigate_to_pose.hpp>

using NavigateToPose = nav2_msgs::action::NavigateToPose;
using Client = rclcpp_action::Client<NavigateToPose>;

class NavSender : public rclcpp::Node {
public:
    NavSender() : Node("nav_goal_sender") {
        client_ = rclcpp_action::create_client<NavigateToPose>(this, "navigate_to_pose");

        auto goal = NavigateToPose::Goal();
        goal.pose.header.frame_id = "map";
        goal.pose.pose.position.x = 1.0;
        goal.pose.pose.position.y = 2.0;
        goal.pose.pose.orientation.w = 1.0;

        client_->wait_for_action_server();
        auto options = rclcpp_action::Client<NavigateToPose>::SendGoalOptions();
        options.result_callback = [this](const Client::WrappedResult& result) {
            if (result.code == rclcpp_action::ResultCode::SUCCEEDED)
                RCLCPP_INFO(get_logger(), "Goal reached!");
            else
                RCLCPP_WARN(get_logger(), "Failed, code: %d", (int)result.code);
        };
        client_->async_send_goal(goal, options);
    }
private:
    Client::SharedPtr client_;
};
```

### 5. 导航结果码

```cpp
// result.code 的可能值：
// SUCCEEDED          - 成功到达
// ABORTED            - 失败（路径不可达/规划失败）
// CANCELED           - 被取消
// 失败细节在 result.result->error_code：
//   0=无错误 1=未知 2=无效目标 ... 具体见 nav2_msgs/msg/ComputePathToPose error codes
```

---

## 💻 动手实验

### 实验 1：RViz 中导航
```bash
# 启动仿真 + 导航（一条龙）
export TURTLEBOT3_MODEL=waffle
ros2 launch nav2_bringup tb3_simulation_launch.py
```

1. 用 "2D Pose Estimate" 定位机器人
2. 用 "Nav2 Goal" 设置目标点
3. 观察路径规划和执行过程

### 实验 2：多点巡逻
用 `nav2_msgs::action::FollowWaypoints` 让机器人在几个预设点之间循环导航。

---

## ✏️ 练习任务

### 练习 1：参数调优
调整 FollowPath 的速度限制和采样参数，观察对导航行为的影响。

### 练习 2：动态避障
在 Gazebo 中动态添加障碍物，观察局部规划器的避障行为。

### 练习 3：导航失败处理
编写健壮的导航程序，处理各种失败情况：
- 目标不可达（result.code 判断 + error_code 细分）
- 路径被阻塞
- 超时重试

---

## ❓ 常见问题

**Q: 机器人原地旋转不前进？**
A: 通常是局部规划器参数问题。检查 `sim_time` 是否太短，速度采样数是否足够，代价地图膨胀是否过厚。

**Q: 导航时撞到障碍物？**
A: 增大 `inflation_radius`，确保 `robot_radius`/`footprint` 准确，降低最大速度。

**Q: 全局路径很奇怪？**
A: 检查代价地图的膨胀层参数，可能是膨胀半径太大导致只能走窄路。

**Q: move_base 的配置文件能直接用吗？**
A: 不能。Nav2 参数结构完全不同：代价地图嵌在 server 里、插件化配置（`plugin:` 字段）、DWA 换成 DWB。迁移时对照官方 nav2_params.yaml 模板改。
