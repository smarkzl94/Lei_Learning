# 05 - 范围 for 与初始化列表

## 🎯 学习目标
- 掌握范围 for 循环的使用
- 理解 initializer_list
- 掌握列表初始化（C++11）
- 了解结构化绑定（C++17）

---

## 📚 核心知识点

### 1. 范围 for 循环
```cpp
std::vector<int> vec = {1, 2, 3, 4, 5};

// 值拷贝
for (int x : vec) {
    x *= 2;  // 修改的是副本，原 vec 不变
}

// 引用（可修改）
for (int& x : vec) {
    x *= 2;  // 修改原 vec
}

// const 引用（只读，推荐）
for (const auto& x : vec) {
    std::cout << x << " ";
}

// 数组也支持
int arr[] = {1, 2, 3};
for (auto x : arr) {
    std::cout << x;
}

// 初始化列表
for (auto x : {1, 2, 3, 4, 5}) {
    std::cout << x;
}
```

### 2. 列表初始化
```cpp
// 统一初始化语法（C++11）
int a{10};           // 直接列表初始化
int b = {20};        // 拷贝列表初始化
std::vector<int> v{1, 2, 3, 4, 5};

// 防止窄化转换
int x = 3.14;        // OK，截断为 3
// int y{3.14};      // 错误！double 到 int 是窄化转换

// 类对象列表初始化
class Point {
public:
    int x, y;
};

Point p{10, 20};     // 聚合初始化
Point p2 = {30, 40}; // 等价
```

### 3. initializer_list
```cpp
#include <initializer_list>

class MyVector {
public:
    // 接受初始化列表的构造函数
    MyVector(std::initializer_list<int> list) {
        data.reserve(list.size());
        for (int x : list) {
            data.push_back(x);
        }
    }
    
    // 接受初始化列表的赋值运算符
    MyVector& operator=(std::initializer_list<int> list) {
        data.clear();
        for (int x : list) {
            data.push_back(x);
        }
        return *this;
    }
    
private:
    std::vector<int> data;
};

// 使用
MyVector v1 = {1, 2, 3, 4, 5};  // 列表构造
v1 = {10, 20, 30};               // 列表赋值
```

### 4. 结构化绑定（C++17）
```cpp
// 绑定 pair
std::pair<int, std::string> p = {1, "one"};
auto [id, name] = p;  // id = 1, name = "one"

// 绑定 tuple
std::tuple<int, double, char> t = {1, 3.14, 'a'};
auto [x, y, z] = t;

// 绑定数组
int arr[3] = {1, 2, 3};
auto [a, b, c] = arr;

// 绑定结构体（需要是公开数据成员）
struct Point { int x; int y; };
Point pt{10, 20};
auto [px, py] = pt;

// 引用绑定
auto& [rx, ry] = pt;  // 可以修改 pt
rx = 100;  // pt.x = 100
```

### 5. if/switch 带初始化（C++17）
```cpp
// if 带初始化
if (auto it = map.find(key); it != map.end()) {
    // it 在这里可用
    std::cout << it->second;
} else {
    // it 在这里也可用
    std::cout << "Not found";
}
// it 在这里不可用（出了作用域）

// switch 带初始化
switch (auto ch = getchar(); ch) {
    case 'y': /* ... */ break;
    case 'n': /* ... */ break;
    default: /* ... */ break;
}
```

---

## 💻 代码示例

```cpp
#include <iostream>
#include <vector>
#include <map>
#include <string>

int main() {
    // 范围 for + 结构化绑定遍历 map
    std::map<int, std::string> students = {
        {1001, "Alice"},
        {1002, "Bob"},
        {1003, "Charlie"}
    };
    
    for (const auto& [id, name] : students) {
        std::cout << "ID: " << id << ", Name: " << name << std::endl;
    }
    
    // if 带初始化
    std::vector<int> nums = {1, 2, 3, 4, 5};
    if (auto size = nums.size(); size > 0) {
        std::cout << "Vector has " << size << " elements" << std::endl;
    }
    
    // 列表初始化防止窄化
    // int bad{3.14};  // 编译错误
    int good{3};       // OK
    
    return 0;
}
```

---

## ✏️ 练习任务

### 练习 1：遍历容器
用范围 for 遍历各种容器（vector、map、set、string），比较值拷贝和引用的性能差异。

### 练习 2：自定义类的列表初始化
让自己的类支持 `{a, b, c}` 形式的初始化。

### 练习 3：结构化绑定应用
有一个 `std::vector<std::tuple<int, std::string, double>>`，用结构化绑定遍历输出每个元素。

### 练习 4：安全的查找
用 C++17 的 `if` 带初始化，实现一个安全的 map 查找函数，避免在作用域外使用迭代器。

---

## ❓ 常见问题

**Q: 范围 for 中用什么：`auto`、`auto&` 还是 `const auto&`？**
A: 默认用 `const auto&`（只读不拷贝）；需要修改时用 `auto&`；基本类型小对象可以用 `auto`（值拷贝）。

**Q: 列表初始化和普通初始化有什么区别？**
A: 列表初始化更严格，禁止窄化转换，且语法统一（可用于各种场景）。

**Q: 结构化绑定能绑定私有成员吗？**
A: 不能，只能绑定公开的、非静态的数据成员。
