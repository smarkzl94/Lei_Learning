# 02 - 服务 Service

## 🎯 学习目标
- 理解 Service 的请求/响应模型
- 掌握 Service Server 和 Client 的编写
- 理解 Service 与 Topic 的区别

---

## 📚 核心知识点

### 1. Service vs Topic

| 特性 | Topic | Service |
|------|-------|---------|
| 通信模型 | 发布/订阅 | 请求/响应 |
| 同步性 | 异步 | 同步 |
| 多对多 | 是 | 否（一个 Server） |
| 适用场景 | 连续数据流 | 偶尔调用的功能 |
| 示例 | 传感器数据 | 获取参数、执行动作 |

### 2. 常用系统服务

```bash
# 查询服务列表
ros2 service list

# 查看服务类型
ros2 service type /spawn   # turtlesim/srv/Spawn

# 调用服务
ros2 service call /spawn turtlesim/srv/Spawn "{x: 5, y: 5, theta: 0.5, name: 'turtle2'}"
```

### 3. ROS2 C++ Service Server

```cpp
#include <rclcpp/rclcpp.hpp>
#include <example_interfaces/srv/add_two_ints.hpp>

using AddTwoInts = example_interfaces::srv::AddTwoInts;

class AddServer : public rclcpp::Node {
public:
    AddServer() : Node("add_server") {
        service_ = create_service<AddTwoInts>(
            "add_two_ints",
            std::bind(&AddServer::handleRequest, this,
                      std::placeholders::_1, std::placeholders::_2));
    }
    
private:
    void handleRequest(
        const std::shared_ptr<AddTwoInts::Request> request,
        std::shared_ptr<AddTwoInts::Response> response) {
        response->sum = request->a + request->b;
        RCLCPP_INFO(get_logger(), "%ld + %ld = %ld",
                    request->a, request->b, response->sum);
    }
    
    rclcpp::Service<AddTwoInts>::SharedPtr service_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<AddServer>());
    rclcpp::shutdown();
    return 0;
}
```

### 4. ROS2 C++ Service Client

```cpp
#include <rclcpp/rclcpp.hpp>
#include <example_interfaces/srv/add_two_ints.hpp>

using AddTwoInts = example_interfaces::srv::AddTwoInts;

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = rclcpp::Node::make_shared("add_client");
    
    auto client = node->create_client<AddTwoInts>("add_two_ints");
    
    // 等待服务
    while (!client->wait_for_service(std::chrono::seconds(1))) {
        if (!rclcpp::ok()) {
            RCLCPP_ERROR(node->get_logger(), "Interrupted");
            return 1;
        }
        RCLCPP_INFO(node->get_logger(), "Waiting for service...");
    }
    
    // 发送请求
    auto request = std::make_shared<AddTwoInts::Request>();
    request->a = 5;
    request->b = 3;
    
    auto future = client->async_send_request(request);
    
    // 等待响应
    if (rclcpp::spin_until_future_complete(node, future) ==
        rclcpp::FutureReturnCode::SUCCESS) {
        RCLCPP_INFO(node->get_logger(), "Result: %ld", future.get()->sum);
    } else {
        RCLCPP_ERROR(node->get_logger(), "Failed");
    }
    
    rclcpp::shutdown();
    return 0;
}
```

---

## 💻 动手实验

### 实验 1：加法服务
实现一个 AddTwoInts 服务，客户端发送两个整数，服务端返回和。

### 实验 2：获取机器人状态
实现一个服务，返回机器人的当前位置、电量、状态等信息。

### 实验 3：异步服务调用
ROS2 中尝试异步调用多个服务，并汇总结果。

---

## ✏️ 练习任务

### 练习 1：字符串处理服务
服务端提供字符串反转、大写转换、长度计算等功能，客户端选择操作。

### 练习 2：参数查询服务
服务端维护一组参数，客户端可以查询和修改参数值。

### 练习 3：Service + Topic 结合
编写一个节点：
- 通过 Service 接收目标位置
- 通过 Topic 发布当前移动状态
- 模拟移动到目标位置的过程

---

## ❓ 常见问题

**Q: Service 调用超时怎么办？**
A: `wait_for_service` 可设置等待超时；正式调用用 `async_send_request` + `spin_until_future_complete`，拿不到响应就按失败处理。

**Q: 一个 Service 可以被多个 Client 同时调用吗？**
A: Server 会排队处理请求，一次处理一个。如果需要并行，考虑用 Topic 或 Action。

**Q: Service 适合传输大数据吗？**
A: 不适合。Service 适合小数据、快速响应的场景。大数据用 Topic。
