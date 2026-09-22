# 📓 ROS 速查笔记

> 高频命令和易忘概念的个人速查手册，和 [知识盲区](../知识盲区.md) 配合使用。
> 用法：写代码卡住时先查这里；这里没有的再记入知识盲区。

---

## 1. 三板斧（工作空间生命周期，最高频）

```bash
# ① 建：创建工作空间
mkdir -p ~/ros2_ws/src

# ② 编：编译（改了代码就跑这个）
cd ~/ros2_ws && colcon build
colcon build --packages-select <包名>    # 只编一个包
rm -rf build install log && colcon build # 彻底重编（玄学问题先试试这个）

# ③ 配：加载环境（每个新终端都要！）
source ~/ros2_ws/install/setup.bash
```

---

## 2. 工作空间目录结构

```
~/ros2_ws/
├── src/     ← 唯一要碰的目录：自己写的功能包放这里
├── build/   ← 编译中间文件（别管，出问题可删）
├── install/ ← 编译产物 + setup.bash（ros2 run 从这里找可执行文件）
└── log/     ← 编译日志（别管）
```

---

## 3. Overlay（叠加）原则

**后 source 的覆盖先 source 的**，同左往右查找：

```bash
source /opt/ros/humble/setup.bash       # 第1层：系统包
source ~/ros2_ws/install/setup.bash     # 第2层：自己的包（同名时覆盖系统）
echo $AMENT_PREFIX_PATH
# → /home/lei/ros2_ws/install:/opt/ros/humble   （左优先）
```

---

## 4. ROS 五大核心概念（八股文，面试/复盘必背）

| 概念 | 一句话定义 | 类比 | 通信方式 |
|------|-----------|------|----------|
| **Node 节点** | 执行计算的最小进程单元 | 节目组 | - |
| **Topic 话题** | 节点间**异步**的发布/订阅通道 | 电视频道 | 单向、持续广播、多对多 |
| **Message 消息** | Topic 里传输的数据结构（.msg 定义） | 频道节目内容 | - |
| **Service 服务** | 节点间**同步**的请求/响应 | 打电话 | 双向、一问一答、一对一 |
| **Action 动作** | 带进度反馈和取消的长任务 | 点外卖 | Goal + Feedback + Result + Cancel |
| **参数服务器** | 全局共享的配置字典 | 公告栏 | 静态/准静态配置 |

必背要点：

1. **Topic vs Service**：Topic 是"一直广播，爱听不听"（传感器数据）；Service 是"问了才答，必有回应"（拍照、查询）。
2. **ROS2 没有 Master**（区别 ROS1 的最大点）：基于 DDS 自动发现，节点互相找人不需要中心注册；启动任何节点前**不需要先跑 roscore 之类的东西**。
3. **松耦合**：发布者和订阅者互不知道对方存在，只认话题名。

配套命令：

```bash
ros2 node list / info <节点>      # 节点
ros2 topic list / echo <话题>     # 话题
ros2 service list / call <服务>   # 服务
ros2 interface show <消息类型>    # 消息
```

---

## 5. 调试先查的环境变量

| 命令 | 用途 |
|------|------|
| `echo $AMENT_PREFIX_PATH` | 包搜索路径（"找不到包"先看它 source 没） |
| `echo $ROS_DISTRO` | 确认版本（应为 humble） |

---

## 5. 海龟三件套（环境自检标准流程）

```bash
ros2 run turtlesim turtlesim_node      # 终端1：仿真器（不用先启动任何核心！）
ros2 run turtlesim turtle_teleop_key   # 终端2：键盘控制（方向键）
```

配套检查命令：

```bash
ros2 node list        # 看活着的节点
ros2 topic list       # 看话题
rqt_graph             # 看节点关系图
```

---

## 6. 常见报错速查

| 现象 | 原因 | 解法 |
|------|------|------|
| `ros2: command not found` | 没 source | `source /opt/ros/humble/setup.bash` 或重开终端 |
| `ros2 run` 找不到自己的包 | 没 colcon build 或没 source install | 编译 + `source install/setup.bash` |
| 改了代码运行结果没变 | 没重新编译 | `colcon build` 后再跑（ros2 run 跑的是 install/ 里的旧产物） |
| DDS 发现慢/节点互相看不见 | 多网卡或防火墙 | 设置 `ROS_LOCALHOST_ONLY=1`（单机调试常用） |

---

## 记录区

> 以下由学习过程中追加（格式同 [知识盲区](../知识盲区.md)）

### ROS2 节点一生 · 五步链（建包→编译→运行全链路）

- **类型**：流程梳理
- **发现日期**：2026-09-16
- **关联知识点**：ROS 02 章 工作空间与功能包（03 创建功能包 / 04 launch）

**问题描述**：
建包、写代码、colcon build、source、ros2 run 分开看都懂，但串不起来——不知道每一步的产物是什么、出错该回查哪一步。

**正解/笔记**：

```
① 建包    ros2 pkg create my_package --build-type ament_cmake --node-name my_node
          └─→ 在 src/ 下生成  package.xml + CMakeLists.txt + src/my_node.cpp

② 写代码  编辑 my_node.cpp（init → Node → 循环 → shutdown）

③ 编译    colcon build
          └─→ 读两个配置文件 → 编译 → 放进 install/

④ 注册    source install/setup.bash
          └─→ 告诉终端：my_package 的存在、my_node 的路径（每个新终端都要！）

⑤ 运行    ros2 run my_package my_node
          └─→ 从 install/lib/my_package/ 找到可执行文件，启动节点
```

**排错对照表**：

| 现象 | 回查步骤 |
|------|---------|
| ros2 run 找不到包 | ④ source（99% 是这个） |
| 编译报错 | ② 代码 或 ① 的 package.xml / CMakeLists.txt |
| 节点启动无反应 | ⑤ spin 漏写 / 话题没对上 |
| launch 找不到文件 | ③ CMakeLists 漏 install(DIRECTORY launch ...) |

**核心记忆**：①② 是"写"，③ 是"编译"，④ 是"环境"，⑤ 是"跑"。launch 文件 = 把 ⑤ 自动化 + 附加参数/重映射。
（配图画布：「ROS 学习图解」Canvas 中的《ROS2 节点一生·五步链》）

---

### Topic 发布/订阅通信模型（多对多异步广播）

- **类型**：概念梳理
- **发现日期**：2026-09-16
- **关联知识点**：ROS 03 章 核心通信机制（01 话题 Topic）

**模型要点**：

```
Publisher A ─┐
Publisher B ─┼─→ /chatter (std_msgs/msg/String) ─→ Subscriber X
             │      ↑ Topic：单向·异步·多对多        ─→ Subscriber Y
             │                                      ─→ ros2 topic echo（也是订阅者）
```

| 特性 | 含义 |
|------|------|
| 单向 | 数据只从 Pub → Sub，没有回程 |
| 异步 | 发布者 publish() 完就走，不等订阅者处理 |
| 解耦 | 双方只认话题名，互不知道对方存在 |
| 多对多 | N 个发布者、M 个订阅者同时接同一个 Topic |

**与 Service 的边界**：要"一问一答"（如 /spawn 生成海龟）不能用 Topic，要用 Service（03-2）。
（配图画布：「ROS 学习图解」Canvas 中的《ROS Topic 多对多通信模型》）

---

### RCLCPP_INFO 的 printf 风格格式化日志

- **类型**：语法不懂
- **发现日期**：2026-09-16
- **关联知识点**：ROS 03 章 01 话题（节点打印）

**问题描述**：
`RCLCPP_INFO(get_logger(), "Publishing: '%s'", msg.data.c_str())` 这种写法没见过，不知道各部分是什么。

**正解/笔记**：

```cpp
RCLCPP_INFO( get_logger(), "Publishing: '%s'", msg.data.c_str() )
//   ④宏        ①日志器         ②格式字符串        ③填入的数据
```

- ① `get_logger()`：取本节点的日志器，日志要知道是哪个节点打的
- ② 格式字符串：和 `printf` 完全同一套，`%s`=字符串 `%d`=整数 `%f`=浮点 `%zu`=size_t
- ③ `msg.data.c_str()`：`%s` 只认 `const char*`，std::string 要转一下
- ④ `RCLCPP_INFO` 是**宏**，自动带级别 + 时间戳 + 节点名前缀；WARN/ERROR 用法相同

**为什么不用 std::cout**：日志要分级过滤、自动带前缀，cout 做不到。

---

### rclcpp 句柄的 SharedPtr 别名一族（`XXX::SharedPtr`）

- **类型**：语法不懂
- **发现日期**：2026-09-16
- **关联知识点**：ROS 03 章 01 话题（类风格节点的成员声明）

**问题描述**：
`rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_;` 这种写法不懂，`::SharedPtr` 是什么、为什么可以这么用。

**正解/笔记**（分三层）：

1. `rclcpp::Publisher<MessageT>` 是**类模板**，必须传消息类型实例化
2. Publisher 类内部定义了别名 `using SharedPtr = std::shared_ptr<Publisher<MessageT>>;`
   所以 `Publisher<...>::SharedPtr` ≡ `std::shared_ptr<Publisher<...>>`
3. 声明成员变量：智能指针管理句柄，用 `->` 调用成员（如 `pub_->publish(msg)`），节点析构时自动释放（RAII）

**alias 一族速查**（看到 `XXX::SharedPtr` 就翻译成 `std::shared_ptr<XXX>`）：

| 写法 | 等价于 |
|------|--------|
| `rclcpp::Publisher<T>::SharedPtr` | `std::shared_ptr<Publisher<T>>` |
| `rclcpp::Subscription<T>::SharedPtr` | `std::shared_ptr<Subscription<T>>` |
| `rclcpp::TimerBase::SharedPtr` | `std::shared_ptr<TimerBase>` |
| `rclcpp::Node::SharedPtr` | `std::shared_ptr<Node>` |

**为什么用别名不裸写**：换消息类型只改一处；与官方教程/源码写法一致。

---

### Talker / Listener 代码框架模板（背这个）

- **类型**：框架速记
- **发现日期**：2026-09-16
- **关联知识点**：ROS 03 章 01 话题（发布者与订阅者完整写法）

**核心框架（所有节点都长这样）**：

```cpp
// src/xxx.cpp
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>      // ① 按消息类型换头文件
#include <functional>                   // std::bind 需要

class XxxNode : public rclcpp::Node {   // ② 类名自定义
public:
    XxxNode() : Node("xxx_node") {      // ③ 构造时定节点名
        // ④ 在这里建 publisher / subscription / timer
    }
private:
    // ⑤ 回调函数
    // ⑥ 成员变量（别名一族句柄）
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<XxxNode>());  // ⑦ 四件套，背下来
    rclcpp::shutdown();
    return 0;
}
```

**Talker（发布者）在 ④⑤⑥ 填什么**：

```cpp
④  pub_ = create_publisher<std_msgs::msg::String>("chatter", 10);
    timer_ = create_wall_timer(                          // 定时器：多久发一次
        std::chrono::milliseconds(100),                  // 100ms = 10Hz
        std::bind(&Talker::timeCallback, this));
⑤  void timeCallback() {                                // 到点就被调用
        auto msg = std_msgs::msg::String();
        msg.data = "Hello " + std::to_string(count_++);
        pub_->publish(msg);
    }
⑥  size_t count_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_;
    rclcpp::TimerBase::SharedPtr timer_;
```

**Listener（订阅者）在 ④⑤⑥ 填什么**：

```cpp
④  sub_ = create_subscription<std_msgs::msg::String>(
        "chatter", 10,                                 // 话题名必须和 Talker 一致
        std::bind(&Listener::topicCallback, this,
                  std::placeholders::_1));             // _1 = 消息从这个坑位传入
⑤  void topicCallback(const std_msgs::msg::String::SharedPtr msg) {
        RCLCPP_INFO(get_logger(), "I heard: '%s'", msg->data.c_str());
    }
⑥  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr sub_;
```

**记忆口诀**：

| 角色 | 主动/被动 | 核心三件套 |
|------|----------|-----------|
| Talker | 主动：定时器驱动 | `create_publisher` + `timer` + `publish()` |
| Listener | 被动：回调驱动 | `create_subscription` + `_1` 占位 + `msg->` |

- 发布者像**闹钟**：定时自己响（timer 触发）
- 订阅者像**门铃**：有人按才响（消息触发回调）
- 两者唯一连接点 = **话题名字符串**，代码互不引用


---

### Service 的"几板斧"（对照 Topic 框架）

- **类型**：框架速记
- **发现日期**：2026-09-20
- **关联知识点**：ROS 03 章 02 服务 Service

**骨架不变**：main() 四件套、spin、SharedPtr 别名——和 Topic 完全同一副。差别全在下面两套板斧里。

**Server 三件套（被动，像"柜员"）**：

```cpp
① 创建：service_ = create_service<SrvType>("服务名",
        std::bind(&类::回调, this, _1, _2));   // 双坑位！_1=请求 _2=响应
② 回调：void cb(const std::shared_ptr<Request> req,
                     std::shared_ptr<Response> res) {
        res->字段 = 处理(req->字段);           // 填响应
    }                                          // 函数返回 = 答复自动送达，没有 publish
③ 成员：rclcpp::Service<SrvType>::SharedPtr service_;
```

**Client 三板斧（主动，像"顾客"，future 三步）**：

```cpp
① 等开门：while (!client->wait_for_service(1s)) { ... }   // Server 没起就循环等
② 下单：  auto future = client->async_send_request(request);  // 不等，拿"取货单"
③ 取货：  spin_until_future_complete(node, future);          // 等货（节点照常活着）
         future.get()->结果;                                  // 凭单取结果
```

**与 Topic 的对仗记忆**：

| | Topic | Service |
|---|-------|---------|
| 被动端 | Listener：`_1` 消息 | Server：`_1`请求 + `_2`响应 |
| 主动端 | Talker：publish 完就走 | Client：必须等 future 取货 |
| 连接点 | 话题名字符串 | 服务名字符串 |
| 语义 | 喊话（单向、异步） | 打电话（双向、同步） |

**口诀**：柜员"收请求、填响应、返回即送达"；顾客"等开门、下单、凭单取货"。


---

### ROS2 命令行速查表（截至 03-2 Service）

- **类型**：命令速查
- **发现日期**：2026-09-20
- **关联知识点**：ROS 03 章 核心通信机制（Topic + Service 实操调试）

**节点 node**：

| 命令 | 作用 |
|------|------|
| `ros2 run <包名> <可执行名>` | 跑节点（最常用） |
| `ros2 node list` | 当前活着的节点 |
| `ros2 node info /节点名` | 节点户口：订阅/发布了什么 |

**话题 topic**：

| 命令 | 作用 |
|------|------|
| `ros2 topic list` | 有哪些话题 |
| `ros2 topic echo /xxx` | 偷看数据（最常用调试） |
| `ros2 topic hz /xxx` | 实际发布频率 |
| `ros2 topic info /xxx` | 类型 + Pub/Sub 数量（排查静默失联第一招） |
| `ros2 topic pub /xxx 包/msg/类型 "{字段: 值}"` | 手动发一条（没发布者也能测订阅端） |

**服务 service**（与 topic 对称）：

| 命令 | 作用 |
|------|------|
| `ros2 service list` | 有哪些服务 |
| `ros2 service type /xxx` | 服务类型 |
| `ros2 service call /xxx 包/srv/类型 "{字段: 值}"` | 手动调一次（不写代码测服务） |

**工程**：

| 命令 | 作用 |
|------|------|
| `ros2 pkg create <包名> --build-type ament_cmake --node-name <节点>` | 建包 |
| `colcon build --packages-select <包名>` | 编译 |
| `source install/setup.bash` | 注册（每个新终端都要！） |

**记忆规律**：
1. 全家一个妈：`ros2 <对象> <动作>`，对象 4 个（node/topic/service/pkg）
2. topic ↔ service 对称：topic 的 `echo`（偷看）对应 service 的 `call`（试打）
3. 调试三板斧：`list` 看名字 → `info` 看数量 → `echo/call` 看内容


---

### ROS2 C++ 代码一页纸（Topic + Service 合并版）

- **类型**：框架速记
- **发现日期**：2026-09-20
- **关联知识点**：ROS 03 章 核心通信机制（全部通信代码的合并速查）

**0. 不变骨架（所有节点通用）**：

```cpp
#include <rclcpp/rclcpp.hpp>
// + 你用的消息/服务头文件

class 类名 : public rclcpp::Node {
public:
    类名() : Node("节点名") {
        // 在这里建 pub / sub / service / timer
    }
private:
    // 回调函数
    // 成员句柄（alias 一族）
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<类名>());
    rclcpp::shutdown();
    return 0;
}
```

**1. Topic 两套**：

```cpp
// Talker（闹钟式·主动）三件套
pub_   = create_publisher<Msg>("话题名", 10);
timer_ = create_wall_timer(间隔, bind(&类::回调, this));
回调里:  msg.data = ...;  pub_->publish(msg);

// Listener（门铃式·被动）三件套
sub_ = create_subscription<Msg>("话题名", 10,
        bind(&类::回调, this, _1));      // 单坑位
回调里:  msg->字段;
```

**2. Service 两套**：

```cpp
// Server（柜员式·被动）三件套
service_ = create_service<Srv>("服务名",
            bind(&类::回调, this, _1, _2));   // 双坑位：_1请求 _2响应
回调里:  response->字段 = 处理(request->字段);   // 填完即送达，无 publish

// Client（顾客式·主动）三板斧 future
client->wait_for_service(1s);                   // ① 等开门
auto future = client->async_send_request(req);  // ② 下单拿取货单
spin_until_future_complete(node, future);       // ③ 等货（节点照常活着）
future.get()->字段;                              //   取货
```

**3. alias 一族速查**（`Xxx::SharedPtr` ≡ `std::shared_ptr<Xxx>`，句柄一律 `->` 调用）：

| 句柄 | 用于 |
|------|------|
| `rclcpp::Publisher<T>::SharedPtr` | 发布 |
| `rclcpp::Subscription<T>::SharedPtr` | 订阅 |
| `rclcpp::Service<Srv>::SharedPtr` | 服务 |
| `rclcpp::TimerBase::SharedPtr` | 定时器 |
| `rclcpp::Node::SharedPtr` | 节点（Client 用） |

**4. 类型命名规律**：

```
std_msgs/msg/String                 →  std_msgs::msg::String
example_interfaces/srv/AddTwoInts   →  example_interfaces::srv::AddTwoInts
my_package/srv/Xxx（自定义）         →  my_package::srv::Xxx
```
