# 01 - 话题 Topic

## 🎯 学习目标
- 理解 Topic 的发布/订阅模型
- 掌握 Publisher 和 Subscriber 的编写
- 理解消息类型和队列机制

---

## 📚 核心知识点

### 1. Topic 通信模型

```
Publisher                       Subscriber
   │                                ▲
   │  /chatter (std_msgs/String)   │
   └───────────────┬───────────────┘
                   │
            ┌──────┴──────┐
            │   Topic     │
            │  (多对多)   │
            └─────────────┘
```

- **Publisher**：发布消息到 Topic
- **Subscriber**：从 Topic 接收消息
- **Topic**：消息通道，多对多通信
- 异步通信，发布者不等待订阅者

### 2. ROS1 C++ Publisher

```cpp
#include <ros/ros.h>
#include <std_msgs/String.h>

int main(int argc, char** argv) {
    ros::init(argc, argv, "talker");
    ros::NodeHandle nh;
    
    // 创建 Publisher
    // 参数：话题名、队列大小
    ros::Publisher pub = nh.advertise<std_msgs::String>("chatter", 10);
    
    ros::Rate rate(10);  // 10 Hz
    int count = 0;
    
    while (ros::ok()) {
        std_msgs::String msg;
        msg.data = "Hello " + std::to_string(count);
        
        pub.publish(msg);   // 发布消息
        ROS_INFO("Published: %s", msg.data.c_str());
        
        ros::spinOnce();    // 处理回调
        rate.sleep();
        ++count;
    }
    
    return 0;
}
```

### 3. ROS1 C++ Subscriber

```cpp
#include <ros/ros.h>
#include <std_msgs/String.h>

// 回调函数
void chatterCallback(const std_msgs::String::ConstPtr& msg) {
    ROS_INFO("Received: %s", msg->data.c_str());
}

int main(int argc, char** argv) {
    ros::init(argc, argv, "listener");
    ros::NodeHandle nh;
    
    // 创建 Subscriber
    ros::Subscriber sub = nh.subscribe("chatter", 10, chatterCallback);
    
    ros::spin();  // 阻塞，等待回调
    
    return 0;
}
```

### 4. ROS2 C++ Publisher

```cpp
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>

class Talker : public rclcpp::Node {
public:
    Talker() : Node("talker"), count_(0) {
        pub_ = create_publisher<std_msgs::msg::String>("chatter", 10);
        timer_ = create_wall_timer(
            std::chrono::milliseconds(100),
            std::bind(&Talker::timerCallback, this));
    }
    
private:
    void timerCallback() {
        auto msg = std_msgs::msg::String();
        msg.data = "Hello " + std::to_string(count_++);
        pub_->publish(msg);
        RCLCPP_INFO(get_logger(), "Publishing: '%s'", msg.data.c_str());
    }
    
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr pub_;
    rclcpp::TimerBase::SharedPtr timer_;
    size_t count_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<Talker>());
    rclcpp::shutdown();
    return 0;
}
```

### 5. ROS2 C++ Subscriber

```cpp
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>

class Listener : public rclcpp::Node {
public:
    Listener() : Node("listener") {
        sub_ = create_subscription<std_msgs::msg::String>(
            "chatter", 10,
            std::bind(&Listener::topicCallback, this, std::placeholders::_1));
    }
    
private:
    void topicCallback(const std_msgs::msg::String::SharedPtr msg) {
        RCLCPP_INFO(get_logger(), "Received: '%s'", msg->data.c_str());
    }
    
    rclcpp::Subscription<std_msgs::msg::String>::SharedPtr sub_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<Listener>());
    rclcpp::shutdown();
    return 0;
}
```

### 6. 常用消息类型

| 消息包 | 常用消息 | 说明 |
|--------|----------|------|
| `std_msgs` | String, Int32, Float64, Bool, Header | 基本类型 |
| `geometry_msgs` | Twist, Pose, Point, Quaternion | 几何数据 |
| `sensor_msgs` | LaserScan, Image, PointCloud2 | 传感器数据 |
| `nav_msgs` | Odometry, Path, OccupancyGrid | 导航数据 |
| `tf2_msgs` | TFMessage | 坐标变换 |

### 7. 队列和缓冲区

```cpp
// 队列大小：缓冲多少条消息
ros::Publisher pub = nh.advertise<std_msgs::String>("chatter", 10);

// 队列策略（ROS2）
// KEEP_LAST (默认): 只保留最新 N 条
// KEEP_ALL: 保留所有（可能内存溢出）

// QoS 配置（ROS2）
auto qos = rclcpp::QoS(10)
    .reliable()       // 可靠传输
    .durability_volatile();  // 不保留历史数据
```

---

## 💻 动手实验

### 实验 1：自定义发布频率
修改 Publisher 的频率，观察 Subscriber 的接收情况。

### 实验 2：多 Publisher 单 Subscriber
启动多个 Publisher 发布到同一个 Topic，观察 Subscriber 接收到的数据。

### 实验 3：图像发布
```cpp
#include <sensor_msgs/Image.h>
// 发布一个简单的灰度图像
```

---

## ✏️ 练习任务

### 练习 1：温度传感器模拟
创建 Publisher 模拟温度传感器（随机 20-30°C），Subscriber 接收并打印，超过 28°C 报警。

### 练习 2：速度控制
Publisher 发送 Twist 消息，Subscriber 接收并解析线速度和角速度。

### 练习 3：频率统计
写一个节点订阅任意 Topic，统计并输出该 Topic 的实际发布频率。

---

## ❓ 常见问题

**Q: spin() 和 spinOnce() 的区别？**
A: `spin()` 阻塞直到节点关闭；`spinOnce()` 处理一次回调然后返回。Publisher 通常配合 `spinOnce()` + `rate.sleep()`。

**Q: 为什么 Subscriber 收不到消息？**
A: 检查：1) 话题名是否一致；2) 消息类型是否匹配；3) 是否 source 了正确的环境。

**Q: 队列大小设多少合适？**
A: 实时性要求高设小（1-10）；允许延迟但怕丢数据设大（100+）。
