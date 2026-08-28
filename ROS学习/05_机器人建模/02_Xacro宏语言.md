# 02 - Xacro 宏语言

## 🎯 学习目标
- 理解 Xacro 的作用
- 掌握宏、属性、条件的用法
- 能够用 Xacro 简化 URDF 编写

---

## 📚 核心知识点

### 1. 为什么用 Xacro

URDF 的问题：
- 重复代码多（如左右对称的轮子）
- 参数分散，修改困难
- 没有计算能力

Xacro（XML Macro）是 URDF 的预处理工具：
- 宏定义和复用
- 属性（变量）
- 简单数学运算
- 条件判断

### 2. 基本语法

```xml
<?xml version="1.0"?>
<robot name="my_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  
  <!-- 属性定义 -->
  <xacro:property name="pi" value="3.14159265359"/>
  <xacro:property name="wheel_radius" value="0.1"/>
  <xacro:property name="wheel_width" value="0.05"/>
  <xacro:property name="base_width" value="0.3"/>
  <xacro:property name="base_length" value="0.5"/>
  <xacro:property name="base_height" value="0.1"/>
  
  <!-- 宏定义：轮子 -->
  <xacro:macro name="wheel" params="prefix reflect">
    <link name="${prefix}_wheel">
      <visual>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
        <material name="black">
          <color rgba="0 0 0 1"/>
        </material>
      </visual>
      <collision>
        <geometry>
          <cylinder radius="${wheel_radius}" length="${wheel_width}"/>
        </geometry>
      </collision>
      <inertial>
        <mass value="0.5"/>
        <inertia ixx="0.01" ixy="0" ixz="0"
                 iyy="0.01" iyz="0"
                 izz="0.01"/>
      </inertial>
    </link>
    
    <joint name="${prefix}_wheel_joint" type="continuous">
      <parent link="base_link"/>
      <child link="${prefix}_wheel"/>
      <origin xyz="0 ${reflect * base_width/2} 0" 
              rpy="${-pi/2} 0 0"/>
      <axis xyz="0 0 1"/>
    </joint>
  </xacro:macro>
  
  <!-- 使用宏 -->
  <xacro:wheel prefix="left" reflect="1"/>
  <xacro:wheel prefix="right" reflect="-1"/>
  
  <!-- 底盘 -->
  <link name="base_link">
    <visual>
      <geometry>
        <box size="${base_length} ${base_width} ${base_height}"/>
      </geometry>
    </visual>
  </link>
  
</robot>
```

### 3. 数学运算

```xml
<!-- Xacro 支持基本运算 -->
<xacro:property name="wheel_offset" value="${base_width/2 + wheel_width/2}"/>
<xacro:property name="wheel_circumference" value="${2 * pi * wheel_radius}"/>

<!-- 条件 -->
<xacro:if value="${base_length > 0.5}">
  <link name="extension">
    <!-- ... -->
  </link>
</xacro:if>

<!-- 除非（条件为假时执行） -->
<xacro:unless value="${has_laser}">
  <!-- ... -->
</xacro:unless>
```

### 4. 包含其他文件

```xml
<!-- 包含材质定义 -->
<xacro:include filename="$(find my_pkg)/urdf/materials.xacro"/>

<!-- 包含传感器宏 -->
<xacro:include filename="$(find my_pkg)/urdf/sensors.xacro"/>

<!-- 使用其他文件中的宏 -->
<xacro:laser_sensor prefix="front" parent="base_link" xyz="0.2 0 0.1"/>
```

### 5. 编译 Xacro 到 URDF

```bash
# 命令行转换
rosrun xacro xacro robot.xacro > robot.urdf

# 检查
roslaunch my_pkg display.launch

# launch 中自动转换
<param name="robot_description" 
       command="$(find xacro)/xacro '$(find my_pkg)/urdf/robot.xacro'" />
```

---

## 💻 动手实验

### 实验 1：重构 URDF
将一个已有的重复代码多的 URDF 重构为 Xacro，观察代码量减少。

### 实验 2：参数化机器人
创建一个 Xacro，通过参数控制：
- 底盘大小
- 轮子数量（2 轮或 4 轮）
- 是否安装激光雷达

### 实验 3：传感器宏库
创建一组常用传感器的 Xacro 宏（激光雷达、摄像头、IMU），方便复用。

---

## ✏️ 练习任务

### 练习 1：完整移动机器人
用 Xacro 创建一个参数化的移动机器人，支持：
- 2 轮/4 轮切换
- 底盘尺寸可调
- 传感器可选（激光、摄像头、IMU）

### 练习 2：机械臂 Xacro
创建一个 6 自由度机械臂的 Xacro，每个连杆的长度和质量可配置。

### 练习 3：宏库整理
将自己常用的 URDF 片段整理成 Xacro 宏库，方便后续项目复用。

---

## ❓ 常见问题

**Q: Xacro 转换后的 URDF 在哪里？**
A: 通常不保存到文件，而是直接在 launch 中通过 `command` 属性实时转换。

**Q: 宏参数可以有默认值吗？**
A: 可以：`params="prefix reflect:=1"`，`reflect` 有默认值 1。

**Q: Xacro 支持循环吗？**
A: 不支持直接的 for 循环。但可以通过多次调用宏或生成后处理来实现。
