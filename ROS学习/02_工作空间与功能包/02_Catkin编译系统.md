# 02 - 编译系统（ament / colcon）

> ROS2 的构建体系：ament（CMake 扩展）+ colcon（编译工具）。ROS1 的 catkin 已被取代，不再学习。

## 🎯 学习目标
- 理解 ROS2 的编译系统（ament + colcon）
- 掌握 package.xml 的配置
- 理解 CMakeLists.txt 的关键指令

---

## 📚 核心知识点

### 1. package.xml

package.xml 定义了包的元信息和依赖关系。

```xml
<?xml version="1.0"?>
<package format="3">
  <name>my_package</name>
  <version>0.0.1</version>
  <description>My first ROS2 package</description>
  
  <maintainer email="user@example.com">My Name</maintainer>
  <license>MIT</license>
  
  <!-- 构建工具 -->
  <buildtool_depend>ament_cmake</buildtool_depend>
  
  <!-- 构建 + 运行都依赖 -->
  <depend>rclcpp</depend>
  <depend>std_msgs</depend>
  
  <!-- 测试依赖 -->
  <test_depend>ament_lint_auto</test_depend>
</package>
```

| 标签 | 说明 |
|------|------|
| `<buildtool_depend>` | 构建工具（ament_cmake / ament_python） |
| `<depend>` | 构建和运行都依赖（ROS2 最常用） |
| `<build_depend>` | 仅编译时需要 |
| `<exec_depend>` | 仅运行时需要 |
| `<test_depend>` | 仅测试时需要 |

### 2. CMakeLists.txt（ROS2）

```cmake
cmake_minimum_required(VERSION 3.8)
project(my_package)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 查找依赖
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)

# 添加可执行文件
add_executable(my_node src/my_node.cpp)
ament_target_dependencies(my_node rclcpp std_msgs)

# 安装
install(TARGETS my_node
  DESTINATION lib/${PROJECT_NAME})

ament_package()
```

关键指令速记：

```cmake
# 多节点包：每个可执行文件重复 add_executable + install
add_executable(node_b src/node_b.cpp)
ament_target_dependencies(node_b rclcpp)

install(TARGETS node_a node_b
  DESTINATION lib/${PROJECT_NAME})

# 安装 launch 目录（launch 文件必须装，否则 ros2 launch 找不到）
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME})

# 结尾必须是这句（生成包的配置文件）
ament_package()
```

---

## 💻 动手实验

### 实验 1：分析现有包的配置
```bash
# 找一个系统包分析其配置
cat /opt/ros/humble/share/turtlesim/package.xml
cat /opt/ros/humble/share/turtlesim/CMakeLists.txt
```

### 实验 2：手动创建最小包
```bash
cd ~/ros2_ws/src
mkdir my_minimal_pkg
cd my_minimal_pkg

# 创建 package.xml
cat > package.xml << 'EOF'
<?xml version="1.0"?>
<package format="3">
  <name>my_minimal_pkg</name>
  <version>0.0.1</version>
  <description>Minimal package</description>
  <maintainer email="test@test.com">Test</maintainer>
  <license>MIT</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <depend>rclcpp</depend>
</package>
EOF

# 创建 CMakeLists.txt
cat > CMakeLists.txt << 'EOF'
cmake_minimum_required(VERSION 3.8)
project(my_minimal_pkg)
find_package(ament_cmake REQUIRED)
ament_package()
EOF

# 编译
cd ~/ros2_ws
colcon build --packages-select my_minimal_pkg
```

---

## ✏️ 练习任务

### 练习 1：依赖分析
查看你常用的 ROS2 包，列出它的所有依赖，分类为 build/run/test 依赖。

### 练习 2：添加自定义消息
修改 package.xml 和 CMakeLists.txt，添加消息生成支持（`rosidl_default_generators`，为 03-5 自定义消息章节做准备）。

### 练习 3：多节点包
创建一个包含两个可执行文件的包，使用不同的编译选项。

---

## ❓ 常见问题

**Q: `ament_package()` 是干什么的？**
A: 每个 ROS2 CMakeLists.txt 的**最后一行必须是它**，生成包的配置文件，让 colcon 认识这个包。漏了会编译报错。

**Q: `ament_target_dependencies` 和 `target_link_libraries` 什么关系？**
A: `ament_target_dependencies` 是 ROS2 的便捷封装，一键处理 ROS2 包的 include 路径和链接库；链接非 ROS 的第三方库仍用 `target_link_libraries`。

**Q: 编译报错 "package not found"？**
A: 对应的包没有在 `find_package(... REQUIRED)` 中列出，或没有 `sudo apt install ros-humble-<包名>`。
