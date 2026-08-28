# 02 - Catkin 编译系统

## 🎯 学习目标
- 理解 ROS 的编译系统
- 掌握 package.xml 的配置
- 理解 CMakeLists.txt 的关键指令

---

## 📚 核心知识点

### 1. package.xml

package.xml 定义了包的元信息和依赖关系。

```xml
<?xml version="1.0"?>
<package format="2">
  <name>my_package</name>
  <version>0.0.1</version>
  <description>My first ROS package</description>
  
  <maintainer email="user@example.com">My Name</maintainer>
  <license>MIT</license>
  
  <!-- 构建依赖 -->
  <buildtool_depend>catkin</buildtool_depend>
  <build_depend>roscpp</build_depend>
  <build_depend>std_msgs</build_depend>
  
  <!-- 运行依赖 -->
  <exec_depend>roscpp</exec_depend>
  <exec_depend>std_msgs</exec_depend>
  
  <!-- 同时是构建和运行依赖（format 2） -->
  <depend>geometry_msgs</depend>
</package>
```

| 标签 | 说明 |
|------|------|
| `<buildtool_depend>` | 构建工具（catkin/colcon） |
| `<build_depend>` | 编译时需要 |
| `<build_export_depend>` | 其他包编译本包时需要 |
| `<exec_depend>` | 运行时需要 |
| `<test_depend>` | 测试时需要 |
| `<depend>` | build + build_export + exec（format 2） |

### 2. CMakeLists.txt（ROS1）

```cmake
cmake_minimum_required(VERSION 3.0.2)
project(my_package)

# 1. 查找依赖包
find_package(catkin REQUIRED COMPONENTS
  roscpp
  std_msgs
  geometry_msgs
)

# 2. 声明 catkin 包
catkin_package(
  INCLUDE_DIRS include
  LIBRARIES my_library
  CATKIN_DEPENDS roscpp std_msgs
)

# 3. 包含目录
include_directories(
  include
  ${catkin_INCLUDE_DIRS}
)

# 4. 编译可执行文件
add_executable(my_node src/my_node.cpp)
target_link_libraries(my_node ${catkin_LIBRARIES})

# 5. 安装规则
install(TARGETS my_node
  RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
```

### 3. CMakeLists.txt（ROS2）

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

### 4. 常用 CMake 指令

```cmake
# 添加库
add_library(my_lib src/my_lib.cpp)
target_link_libraries(my_lib ${catkin_LIBRARIES})

# 添加依赖（确保编译顺序）
add_dependencies(my_node other_pkg_generate_messages_cpp)

# 链接外部库
find_package(Boost REQUIRED COMPONENTS system)
target_link_libraries(my_node ${Boost_LIBRARIES})

# 条件编译
if(CATKIN_ENABLE_TESTING)
  catkin_add_gtest(my_test test/test_my.cpp)
endif()
```

---

## 💻 动手实验

### 实验 1：分析现有包的配置
```bash
# 找一个系统包分析其配置
cat /opt/ros/noetic/share/turtlesim/package.xml
cat /opt/ros/noetic/share/turtlesim/CMakeLists.txt
```

### 实验 2：手动创建最小包
```bash
cd ~/catkin_ws/src
mkdir my_minimal_pkg
cd my_minimal_pkg

# 创建 package.xml
cat > package.xml << 'EOF'
<?xml version="1.0"?>
<package format="2">
  <name>my_minimal_pkg</name>
  <version>0.0.1</version>
  <description>Minimal package</description>
  <maintainer email="test@test.com">Test</maintainer>
  <license>MIT</license>
  <buildtool_depend>catkin</buildtool_depend>
  <depend>roscpp</depend>
</package>
EOF

# 创建 CMakeLists.txt
cat > CMakeLists.txt << 'EOF'
cmake_minimum_required(VERSION 3.0.2)
project(my_minimal_pkg)
find_package(catkin REQUIRED)
catkin_package()
EOF

# 编译
cd ~/catkin_ws
catkin_make
```

---

## ✏️ 练习任务

### 练习 1：依赖分析
查看你常用的 ROS 包，列出它的所有依赖，分类为 build/run/test 依赖。

### 练习 2：添加自定义消息
修改 package.xml 和 CMakeLists.txt，添加消息生成支持（为后续章节做准备）。

### 练习 3：多节点包
创建一个包含两个可执行文件的包，使用不同的编译选项。

---

## ❓ 常见问题

**Q: `catkin_package()` 和 `find_package(catkin)` 的区别？**
A: `find_package` 查找依赖；`catkin_package` 声明本包对外提供的依赖。

**Q: 编译报错 "catkin_package() CATKIN_DEPENDS ... not found"？**
A: 对应的包没有在 `find_package(catkin REQUIRED COMPONENTS ...)` 中列出。

**Q: ROS2 为什么用 `ament` 而不是 `catkin`？**
A: `ament` 是 ROS2 的新一代构建系统，更现代、更灵活、支持更多构建工具（cmake、python 等）。
