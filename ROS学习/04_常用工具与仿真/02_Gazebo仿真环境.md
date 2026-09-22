# 02 - Gazebo 仿真环境

## 🎯 学习目标
- 掌握 Gazebo 的基本操作
- 理解 SDF/URDF 在 Gazebo 中的应用
- 能够创建简单的仿真世界
- 掌握 Gazebo 插件的使用

---

## 📚 核心知识点

### 1. Gazebo 简介

Gazebo 是 ROS 配套的物理仿真器：
- **物理引擎**：ODE、Bullet、Simbody、DART
- **传感器仿真**：摄像头、激光雷达、IMU、力传感器等
- **环境模拟**：光照、重力、摩擦力
- **场景**：室内、室外、自定义世界

### 2. 启动 Gazebo

```bash
# TurtleBot3 仿真（常用入口）
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# 空世界
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

### 3. Gazebo 插件（ROS2 版）

#### 差速驱动插件
```xml
<!-- URDF 中的 Gazebo 插件（ROS2 参数为下划线风格） -->
<gazebo>
  <plugin name="diff_drive" filename="libgazebo_ros_diff_drive.so">
    <ros>
      <remapping>cmd_vel:=cmd_vel</remapping>
      <remapping>odom:=odom</remapping>
    </ros>
    <update_rate>50</update_rate>
    <left_joint>wheel_left_joint</left_joint>
    <right_joint>wheel_right_joint</right_joint>
    <wheel_separation>0.354</wheel_separation>
    <wheel_diameter>0.194</wheel_diameter>
    <max_wheel_torque>20</max_wheel_torque>
    <max_wheel_acceleration>1.0</max_wheel_acceleration>
    <command_topic>cmd_vel</command_topic>
    <odometry_topic>odom</odometry_topic>
    <odometry_frame>odom</odometry_frame>
    <robot_base_frame>base_footprint</robot_base_frame>
    <publish_odom>true</publish_odom>
    <publish_odom_tf>true</publish_odom_tf>
    <publish_wheel_tf>false</publish_wheel_tf>
  </plugin>
</gazebo>
```

#### 激光雷达插件（ROS2 用 ray_sensor）
```xml
<gazebo reference="base_scan">
  <sensor type="ray" name="lds_lfcd_sensor">
    <plugin name="gazebo_ros_lds_lfcd_controller" 
            filename="libgazebo_ros_ray_sensor.so">
      <ros>
        <remapping>~/out:=scan</remapping>
      </ros>
      <frame_name>base_scan</frame_name>
    </plugin>
  </sensor>
</gazebo>
```

#### 摄像头插件
```xml
<gazebo reference="camera_link">
  <sensor type="camera" name="camera">
    <plugin name="camera_controller" 
            filename="libgazebo_ros_camera.so">
      <ros>
        <remapping>~/image_raw:=image_raw</remapping>
        <remapping>~/camera_info:=camera_info</remapping>
      </ros>
      <camera_name>camera</camera_name>
      <frame_name>camera_link</frame_name>
      <update_rate>30.0</update_rate>
    </plugin>
  </sensor>
</gazebo>
```

### 4. 世界文件（.world）

```xml
<?xml version="1.0"?>
<sdf version="1.6">
  <world name="my_world">
    <!-- 物理属性 -->
    <physics type="ode">
      <real_time_update_rate>1000</real_time_update_rate>
      <max_step_size>0.001</max_step_size>
    </physics>
    
    <!-- 场景 -->
    <scene>
      <ambient>0.4 0.4 0.4 1</ambient>
      <background>0.7 0.7 0.7 1</background>
      <shadows>true</shadows>
    </scene>
    
    <!-- 地面 -->
    <include>
      <uri>model://ground_plane</uri>
    </include>
    
    <!-- 太阳 -->
    <include>
      <uri>model://sun</uri>
    </include>
    
    <!-- 自定义模型 -->
    <model name="my_obstacle">
      <pose>2 2 0.5 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box><size>1 1 1</size></box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box><size>1 1 1</size></box>
          </geometry>
          <material>
            <ambient>1 0 0 1</ambient>
          </material>
        </visual>
      </link>
    </model>
  </world>
</sdf>
```

### 5. Gazebo 命令（ROS2）

```bash
# 生成模型（spawn_entity.py 是 ROS2 标准方式）
ros2 run gazebo_ros spawn_entity.py -file my_robot.sdf -entity my_robot
ros2 run gazebo_ros spawn_entity.py -topic robot_description -entity my_robot   # 从 URDF 生成

# 删除模型
ros2 service call /delete_entity gazebo_msgs/srv/DeleteEntity "{name: 'my_robot'}"

# 暂停/继续仿真：GUI 中空格键；或向 /world/*/control 服务发请求
```

---

## 💻 动手实验

### 实验 1：运行 TurtleBot3 仿真
```bash
export TURTLEBOT3_MODEL=waffle
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

用键盘控制机器人移动，观察传感器数据。

### 实验 2：自定义世界
创建一个包含墙壁和障碍物的世界文件，加载到 Gazebo 中。

### 实验 3：传感器测试
在 Gazebo 中：
1. 查看激光雷达数据（RViz）
2. 查看摄像头图像（rqt_image_view）
3. 查看里程计数据（ros2 topic echo /odom）

---

## ✏️ 练习任务

### 练习 1：迷宫世界
创建一个迷宫世界，在 Gazebo 中运行机器人，手动控制走出迷宫。

### 练习 2：传感器标定
通过修改 URDF 中的传感器参数（位置、角度范围），理解参数对数据的影响。

### 练习 3：动态障碍物
编写节点在 Gazebo 中动态添加和删除障碍物模型。

---

## ❓ 常见问题

**Q: Gazebo 启动慢？**
A: 第一次启动会下载模型，耐心等待。可以在 `~/.gazebo/models` 中预置常用模型。

**Q: 机器人在 Gazebo 中漂移？**
A: 检查 URDF 中的质量、惯性参数是否合理。质量太小或惯性矩阵不合理会导致不稳定。

**Q: 仿真和真实机器人的区别？**
A: 仿真理想化了物理（完美的传感器、精确的模型），真实环境有噪声、延迟和未建模动态。算法在仿真中验证后需要在真实环境中调参。
