# 03 - 动作 Action

## 🎯 学习目标
- 理解 Action 的适用场景
- 掌握 Action Server 和 Client 的编写
- 理解 Goal、Feedback、Result 的关系

---

## 📚 核心知识点

### 1. 为什么需要 Action

Service 是同步阻塞的，不适合长时间任务：
- 任务执行时间长，Client 一直等待不合理
- 需要知道任务执行进度
- 任务可以被取消

Action = Service（发送目标） + Topic（反馈进度） + 取消机制

```
Action Client                    Action Server
     │                                │
     ├────── Goal ─────────────────►│
     │◄──── Accept/Reject ──────────┤
     │◄──── Feedback (周期性) ──────┤
     │◄──── Result ─────────────────┤
     │                                │
     ├──── Cancel ─────────────────►│ (可选)
```

### 2. Action 文件定义

```action
# 文件名: MoveTo.action

# Goal
double x
double y
---
# Result
bool success
string message
---
# Feedback
double current_x
double current_y
double progress  # 0.0 ~ 1.0
```

### 3. ROS2 Action

ROS2 的 Action 更现代化，集成在 rclcpp 中。

```cpp
// Server
#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>
#include <my_pkg/action/move_to.hpp>

using MoveTo = my_pkg::action::MoveTo;
using GoalHandleMoveTo = rclcpp_action::ServerGoalHandle<MoveTo>;

class MoveToActionServer : public rclcpp::Node {
public:
    MoveToActionServer() : Node("move_to_server") {
        action_server_ = rclcpp_action::create_server<MoveTo>(
            this, "move_to",
            std::bind(&MoveToActionServer::handleGoal, this, _1, _2),
            std::bind(&MoveToActionServer::handleCancel, this, _1),
            std::bind(&MoveToActionServer::handleAccepted, this, _1));
    }
    
private:
    rclcpp_action::Server<MoveTo>::SharedPtr action_server_;
    
    rclcpp_action::GoalResponse handleGoal(
        const rclcpp_action::GoalUUID& uuid,
        std::shared_ptr<const MoveTo::Goal> goal) {
        RCLCPP_INFO(get_logger(), "Goal received");
        return rclcpp_action::GoalResponse::ACCEPT_AND_EXECUTE;
    }
    
    rclcpp_action::CancelResponse handleCancel(
        const std::shared_ptr<GoalHandleMoveTo> goal_handle) {
        return rclcpp_action::CancelResponse::ACCEPT;
    }
    
    void handleAccepted(const std::shared_ptr<GoalHandleMoveTo> goal_handle) {
        std::thread{std::bind(&MoveToActionServer::execute, this, goal_handle)}.detach();
    }
    
    void execute(const std::shared_ptr<GoalHandleMoveTo> goal_handle) {
        const auto goal = goal_handle->get_goal();
        auto feedback = std::make_shared<MoveTo::Feedback>();
        auto result = std::make_shared<MoveTo::Result>();
        
        for (int i = 0; i <= 100 && rclcpp::ok(); ++i) {
            if (goal_handle->is_canceling()) {
                result->success = false;
                goal_handle->canceled(result);
                return;
            }
            
            feedback->progress = i / 100.0;
            goal_handle->publish_feedback(feedback);
            
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
        
        result->success = true;
        goal_handle->succeed(result);
    }
};
```

### 3.1 标准范本逐行解剖

#### 第 1 块：头文件与别名

```cpp
#include <rclcpp_action/rclcpp_action.hpp>   // Action 专属头文件（Topic 用 rclcpp 就够，Action 多引一个）
#include <my_pkg/action/move_to.hpp>         // 编译器根据 MoveTo.action 自动生成的头文件
```

**重点**：你写的是 `MoveTo.action`（文本），colcon 编译时自动生成 `move_to.hpp`，里面有 `MoveTo::Goal` / `MoveTo::Feedback` / `MoveTo::Result` 三个类——**.action 三段式 = 三个类，一一对应**。

```cpp
using MoveTo = my_pkg::action::MoveTo;
using GoalHandleMoveTo = rclcpp_action::ServerGoalHandle<MoveTo>;
```

纯图省事，不起别名的话每个函数签名都要拖一长串模板参数。

#### 第 2 块：注册三回调

```cpp
action_server_ = rclcpp_action::create_server<MoveTo>(
    this, "move_to",
    std::bind(&MoveToActionServer::handleGoal,     this, _1, _2),
    std::bind(&MoveToActionServer::handleCancel,   this, _1),
    std::bind(&MoveToActionServer::handleAccepted, this, _1));
```

三个参数 = 三个回调，**顺序固定：Goal → Cancel → Accepted**。

`std::bind` = "别现在调用，先打包好，到时候由系统来调"（和 Topic 里 `create_wall_timer` 的用法同款）。

**占位符规则（核心）**：

> **占位符数量 = 调用那一刻还缺几个参数**

| 回调 | 缺的参数 | 占位符 |
|---|---|---|
| `handleGoal(uuid, goal)` | uuid、goal（等 Client 发 Goal 才到） | `_1, _2` |
| `handleCancel(goal_handle)` | goal_handle（等消息进来） | `_1` |
| `handleAccepted(goal_handle)` | goal_handle | `_1` |
| 开线程跑 `execute`（参数已齐全） | 不缺 | 无 |

⚠️ `_1` 的真名是 `std::placeholders::_1`，文件顶部要加 `using namespace std::placeholders;`，否则编译报错（教材省略了，真实会踩的坑）。

#### 第 3 块：三个回调

**handleGoal —— 前台接待**

- `uuid`：本次 Goal 的唯一编号（同时收多个 Goal 时靠它区分）
- `goal`：客户端传来的目标，`goal->x`、`goal->y` 取值
- 返回值：`ACCEPT_AND_EXECUTE`（接单）/ `REJECT`（拒单，如目标超出范围）
- demo 无条件接单；真实项目应在这里校验目标合法性

**handleCancel —— 盖章员**

只表态 `ACCEPT`（同意取消），**不动手停任务**。真正停手的是 execute 循环。

**handleAccepted —— 派单员（全段最微妙）**

```cpp
std::thread{std::bind(&MoveToActionServer::execute, this, goal_handle)}.detach();
```

三步拆解：

1. `std::bind(...)` 把 `execute` 打包成可调用对象（goal_handle 已绑死，所以不需要占位符）
2. `std::thread{...}` 创建新线程，线程一出生就跑 execute
3. `.detach()` 主线程撒手，让它在后台跑到任务结束

**为什么必须开线程**：`handleAccepted` 是回调，跑在 ROS 的回调线程上。直接在里面执行 5 秒任务循环 = 把回调线程堵死，这期间新的 Goal、Cancel 全进不来。**回调里只派活，干活去后台**。

#### 第 4 块：execute——真正干活的地方

```cpp
const auto goal = goal_handle->get_goal();              // 取目标：goal->x, goal->y
auto feedback = std::make_shared<MoveTo::Feedback>();   // 反复填的进度对象
auto result   = std::make_shared<MoveTo::Result>();     // 结束时填一次的结果对象
```

为什么 `make_shared` 不用栈对象？——`publish_feedback()` / `succeed()` 的参数类型就是 `shared_ptr`，API 硬性要求。

循环本体：

```cpp
for (int i = 0; i <= 100 && rclcpp::ok(); ++i) {
```

两个退出条件：

- `i <= 100`：进度 0% → 100%
- `rclcpp::ok()`：整个节点还活着吗（被 Ctrl+C 杀掉就赶紧退）

```cpp
if (goal_handle->is_canceling()) {       // 轮询：有人喊停吗？（每轮都查！）
    result->success = false;
    goal_handle->canceled(result);       // 向 Client 汇报"已取消"
    return;                              // 自己收摊
}
feedback->progress = i / 100.0;          // ⚠️ 100.0 的 .0 不能省！
goal_handle->publish_feedback(feedback); // 播报进度
std::this_thread::sleep_for(std::chrono::milliseconds(50));  // 模拟移动耗时
```

⚠️ **隐藏 bug 预警**：`i / 100` 是整数除法，`5/100 = 0`，101 轮报的全是 0%。

**取消是协商式**：`is_canceling()` 每轮都查 = 轮询（polling），保证取消请求最多一个循环周期内被响应。只查一次 = Cancel 可能被无视，任务跑到底。

收尾三终态（一个 Goal 必须有且只有一个）：`succeed`（成功）/ `canceled`（被取消）/ `abort`（异常失败，demo 未演示）。

#### 这段 demo 不完整，补全清单

1. **缺 main 函数**（四件套不能少）：

```cpp
int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MoveToActionServer>());
    rclcpp::shutdown();
    return 0;
}
```

2. 缺 `using namespace std::placeholders;`（`_1`/`_2` 才能用）
3. Feedback 只填了 `progress`，`.action` 里的 `current_x/current_y` 没填——demo 偷懒，实验时应补上让反馈更像"真在移动"

---

## 💻 动手实验

### 实验 1：简单的移动 Action
实现一个 Action，模拟机器人从 (0,0) 移动到目标位置，期间发送进度反馈。

### 实验 2：取消任务
启动 Action Client 后，在任务完成前发送取消请求，观察处理流程。

---

## ✏️ 练习任务

### 练习 1：导航 Action
实现一个完整的导航 Action：
- 接收目标位姿（x, y, theta）
- 计算路径（简化版，直线）
- 发布当前位姿反馈
- 到达后返回结果

### 练习 2：多目标队列
Client 发送多个目标，Server 依次执行，支持中途取消当前任务。

---

## ❓ 常见问题

**Q: Action 和 Service 怎么选？**
A: 短时间（<1秒）用 Service；长时间、需要进度反馈、可取消的用 Action。

**Q: ROS2 Action 为什么需要单独线程执行？**
A: `handleAccepted` 中如果直接执行会阻塞回调处理，所以需要用新线程。
