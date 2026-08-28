# 02 - Lambda 表达式

## 🎯 学习目标
- 理解 Lambda 表达式的语法
- 掌握捕获列表的使用
- 理解泛型 Lambda（C++14）
- 掌握 Lambda 在 STL 算法中的应用

---

## 📚 核心知识点

### 1. 基本语法
```cpp
// [捕获列表](参数列表) -> 返回类型 { 函数体 }
auto add = [](int a, int b) -> int {
    return a + b;
};

// 省略返回类型（编译器自动推导）
auto multiply = [](int a, int b) {
    return a * b;
};

// 无参数
auto greet = []() {
    std::cout << "Hello!" << std::endl;
};

// 使用
int sum = add(3, 5);  // 8
```

### 2. 捕获列表
```cpp
int x = 10, y = 20;

// 值捕获（拷贝）
auto f1 = [x, y]() { return x + y; };  // x=10, y=20 的副本

// 引用捕获
auto f2 = [&x, &y]() { ++x; ++y; };   // 修改原变量

// 隐式捕获
auto f3 = [=]() { return x + y; };     // 值捕获所有
auto f4 = [&]() { ++x; ++y; };         // 引用捕获所有
auto f5 = [=, &x]() { ++x; return y; }; // 默认值捕获，x 引用捕获
auto f6 = [&, x]() { return x + y; };   // 默认引用捕获，x 值捕获

// this 捕获
class MyClass {
    int value;
public:
    void method() {
        auto f = [this]() { return value; };  // 捕获 this 指针
        auto g = [*this]() { return value; };  // C++17：拷贝整个对象
    }
};

// 初始化捕获（C++14）
auto f7 = [z = x + y]() { return z; };  // z 是 Lambda 内部的变量
```

### 3. 泛型 Lambda（C++14）
```cpp
// 使用 auto 参数
auto add = [](auto a, auto b) {
    return a + b;
};

add(1, 2);        // int
add(1.5, 2.5);    // double
add("Hello, ", std::string("World"));  // 字符串拼接
```

### 4. 立即调用 Lambda
```cpp
// 复杂的初始化
const int value = []() {
    int result = 0;
    for (int i = 1; i <= 10; ++i) {
        result += i;
    }
    return result;
}();  // 定义后立即调用

// 代替复杂的 if-else 初始化
std::string name = [flag]() -> std::string {
    if (flag) return "Alice";
    else return "Bob";
}();
```

---

## 💻 代码示例

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

int main() {
    std::vector<int> nums = {5, 2, 8, 1, 9, 3};
    
    // 排序：降序
    std::sort(nums.begin(), nums.end(), [](int a, int b) {
        return a > b;
    });
    
    // 打印
    std::for_each(nums.begin(), nums.end(), [](int n) {
        std::cout << n << " ";
    });
    std::cout << std::endl;
    
    // 查找第一个大于 5 的元素
    auto it = std::find_if(nums.begin(), nums.end(), [](int n) {
        return n > 5;
    });
    
    // 带捕获的 Lambda
    int threshold = 5;
    int count = std::count_if(nums.begin(), nums.end(), 
        [threshold](int n) {  // 值捕获 threshold
            return n > threshold;
        });
    std::cout << "Numbers > " << threshold << ": " << count << std::endl;
    
    // mutable Lambda
    int sum = 0;
    std::for_each(nums.begin(), nums.end(), 
        [&sum](int n) mutable {  // 如果没有 mutable，sum 不能修改
            sum += n;
        });
    
    return 0;
}
```

---

## ✏️ 练习任务

### 练习 1：自定义排序
有一个 `std::vector<Student>`，用 Lambda 按成绩降序、成绩相同时按姓名升序排序。

### 练习 2：函数工厂
编写一个函数 `make_multiplier(int factor)`，返回一个 Lambda，该 Lambda 将输入乘以 factor。

### 练习 3：回调机制
实现一个简单的 `Event` 类，支持注册 Lambda 回调和触发事件。

### 练习 4：泛型算法
用泛型 Lambda 实现一个通用的 `map` 函数，对容器每个元素应用变换。

---

## ❓ 常见问题

**Q: Lambda 的类型是什么？**
A: 编译器生成的匿名闭包类型，只能用 `auto` 或 `std::function` 存储。

**Q: Lambda 能递归吗？**
A: 不能直接递归（因为类型在定义完成前不确定）。需要用 `std::function` 包装：
```cpp
std::function<int(int)> factorial = [&](int n) -> int {
    return n <= 1 ? 1 : n * factorial(n - 1);
};
```

**Q: 值捕获和引用捕获的变量在 Lambda 中的生命周期？**
A: 值捕获的变量随 Lambda 对象一起；引用捕获的变量必须确保在 Lambda 执行时仍然有效。
