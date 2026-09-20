# 📋 STL 速查

> 与 [知识速查卡](知识速查卡.md) 并列的专项整理。
>
> **第一章：容器**（有什么容器、每个容器有哪些成员函数）
> **第二章：算法**（`<algorithm>` 和 `<numeric>` 的常用算法、惯用法与陷阱）
>
> 以表格为主，一眼扫到要用的东西。

---

# 第一章：STL 容器速查

## 头文件

| 头文件 | 内容 |
|--------|------|
| `<array>` / `<vector>` / `<deque>` / `<list>` / `<forward_list>` | 序列式容器 |
| `<stack>` / `<queue>` | 容器适配器（stack、queue、priority_queue） |
| `<set>` / `<map>` | 关联式容器 |
| `<unordered_set>` / `<unordered_map>` | 无序关联式容器 |
| `<string>` | string（准容器，用法和容器高度一致） |

---

## 1. 容器总览（三大派系）

| 派系 | 容器 | 底层结构 | 核心特征 |
|------|------|---------|----------|
| **序列式** | `array` | 原生数组 | 定长，栈上，零开销 |
| | `vector` | 动态数组 | **默认首选**，尾部增删 O(1)，随机访问 O(1) |
| | `deque` | 分段数组 | 两端增删 O(1)，随机访问 O(1) |
| | `list` | 双向链表 | 任意位置增删 O(1)，**不支持 `[]`** |
| | `forward_list` | 单向链表 | 比 list 更省内存 |
| **适配器** | `stack` | 套 deque 的壳 | 后进先出（LIFO），只露 `push/pop/top` |
| | `queue` | 套 deque 的壳 | 先进先出（FIFO），只露 `push/pop/front/back` |
| | `priority_queue` | 套 vector 的堆 | 大根堆，top 永远是最大 |
| **关联式** | `set` / `multiset` | 红黑树 | 有序、自动去重（multi 允许重复），查找 O(log n) |
| | `map` / `multimap` | 红黑树 | 键值对，按键排序，查找 O(log n) |
| **无序式** | `unordered_set` / `unordered_map` | 哈希表 | **O(1) 查找**，不排序，不支持 `lower_bound` |

**选型口诀**：默认 `vector`；两头增删用 `deque`；中间频繁增删用 `list`；
要"自动排序去重"用 `set`；要"键查值"用 `map`；只求快不求序用 `unordered_map`；
括号匹配/撤销/DFS 用 `stack`；排队/BFS 用 `queue`；Top K 用 `priority_queue`。

---

## 2. 所有容器通用的成员

| 成员 | 功能 |
|------|------|
| `size()` | 元素个数 |
| `empty()` | 是否为空（比 `size()==0` 更地道） |
| `clear()` | 清空 |
| `begin()` / `end()` | 头迭代器 / 尾后迭代器 |
| `cbegin()` / `cend()` | const 版本 |
| `swap(other)` | 交换两个容器内容 |
| `==` / `!=` / `<` 等 | 比较运算符（逐一比较元素） |

---

## 3. vector（动态数组，默认首选）

| 成员 | 功能 | 复杂度 |
|------|------|--------|
| `push_back(x)` | 尾部追加 | 均摊 O(1) |
| `emplace_back(args...)` | 尾部原地构造（比 push_back 少一次拷贝） | 均摊 O(1) |
| `pop_back()` | 删尾部 | O(1) |
| `operator[i]` | 访问（不检查越界） | O(1) |
| `at(i)` | 访问（越界抛异常） | O(1) |
| `front()` / `back()` | 首 / 尾元素 | O(1) |
| `insert(pos, x)` | 在迭代器 pos 处插入 | O(n) |
| `erase(pos)` / `erase(first,last)` | 删除 | O(n) |
| `resize(n)` | 改元素个数（新增补默认值） | O(n) |
| `reserve(n)` | 只预分配容量，不改个数 | O(n) |
| `capacity()` | 当前容量 | O(1) |
| `data()` | 原始数组指针 | O(1) |

> ⚠️ `reserve` ≠ `resize`：reserve 是"订座位"，resize 是"来人坐好"（这个坑你记过）。

---

## 4. deque（双端队列）

| 成员 | 功能 | 复杂度 |
|------|------|--------|
| `push_back(x)` | 尾部追加 | O(1) |
| `emplace_back(args...)` | 尾部原地构造 | O(1) |
| `pop_back()` | 删尾部 | O(1) |
| `push_front(x)` | 头部追加 | O(1) |
| `emplace_front(args...)` | 头部原地构造 | O(1) |
| `pop_front()` | 删头部 | O(1) |
| `operator[i]` | 访问（不检查越界） | O(1) |
| `at(i)` | 访问（越界抛异常） | O(1) |
| `front()` / `back()` | 首 / 尾元素 | O(1) |
| `insert(pos, x)` | 在迭代器 pos 处插入 | O(n) |
| `erase(pos)` / `erase(first,last)` | 删除 | O(n) |
| `resize(n)` | 改元素个数 | O(n) |
| `size()` / `empty()` / `clear()` | 通用状态 | O(1) |
| `begin()` / `end()` | 迭代器 | O(1) |

> 和 vector 的差别：两头增删都是 O(1)，但没有 `reserve` / `capacity`（分段结构不需要）。

---

## 5. list（双向链表）

| 成员 | 功能 | 复杂度 |
|------|------|--------|
| `push_front` / `emplace_front` | 头部插入 | O(1) |
| `pop_front()` | 删头部 | O(1) |
| `push_back` / `emplace_back` | 尾部插入 | O(1) |
| `pop_back()` | 删尾部 | O(1) |
| `front()` / `back()` | 首 / 尾元素 | O(1) |
| `insert(pos, x)` | 任意位置插入 | **O(1)** |
| `erase(pos)` | 任意位置删除 | **O(1)** |
| `splice(pos, other)` | 整段搬移（元素不拷贝） | O(1) |
| `sort()` / `merge()` / `unique()` / `remove(x)` / `reverse()` | 链表专属成员算法 | — |
| `size()` / `empty()` / `clear()` | 通用状态 | O(1) |
| `begin()` / `end()` | 迭代器 | O(1) |

> ⚠️ 没有 `operator[]` / `at` / 随机访问（要访问第 k 个只能遍历）；
> 也不能用 `std::sort`，必须用**自带的** `.sort()`（你记过这个坑）。

---

## 6. array（定长数组）

```cpp
std::array<int, 5> a = {1, 2, 3, 4, 5};   // 大小是模板参数，编译期定死
```

| 成员 | 功能 |
|------|------|
| `operator[]` / `at` | 访问（at 越界抛异常） |
| `front()` / `back()` | 首 / 尾元素 |
| `fill(x)` | 全部填成 x |
| `data()` | 原始指针 |
| `size()` | **静态成员**（也可实例调用） |
| `empty()` | 是否为空 |
| `begin()` / `end()` | 迭代器 |
| `swap(other)` | 交换 |

> 特点：在栈上，零内存开销，性能与原生数组完全一致。

---

## 7. stack（LIFO 栈）⭐ 适配器

```cpp
std::stack<char> st;
```

| 成员 | 功能 |
|------|------|
| `push(x)` / `emplace(args)` | 压栈 |
| `pop()` | 弹栈顶（**无返回值！**） |
| `top()` | 看栈顶（不弹） |
| `empty()` / `size()` | 状态 |

> ⚠️ `pop()` 不返回元素，想"取出栈顶"必须 `top()` + `pop()` 两句。
> 经典应用：括号匹配（LeetCode 20）、撤销操作、DFS。

---

## 8. queue（FIFO 队列）

```cpp
std::queue<int> q;
```

| 成员 | 功能 |
|------|------|
| `push(x)` / `emplace` | 入队尾 |
| `pop()` | 出队头（无返回值） |
| `front()` | 看队头 |
| `back()` | 看队尾 |
| `empty()` / `size()` | 状态 |

> 经典应用：任务排队、BFS 广度优先搜索。

---

## 9. priority_queue（大根堆）

```cpp
std::priority_queue<int> pq;                              // 大根堆：top 是最大
std::priority_queue<int, std::vector<int>, std::greater<int>> minpq;  // 小根堆
```

| 成员 | 功能 | 复杂度 |
|------|------|--------|
| `push(x)` / `emplace` | 插入并自动上浮 | O(log n) |
| `pop()` | 弹堆顶 | O(log n) |
| `top()` | 看堆顶（最大/最小） | O(1) |
| `empty()` / `size()` | 状态 | O(1) |

> 经典应用：Top K 问题（维护一个 size=k 的小根堆）。

---

## 10. set / multiset（有序集合）

```cpp
std::set<int> s;          // 有序 + 自动去重
std::multiset<int> ms;    // 有序 + 允许重复
```

| 成员 | 功能 | 复杂度 |
|------|------|--------|
| `insert(x)` | 插入（set 中已存在则无效） | O(log n) |
| `erase(x)` / `erase(pos)` | 按值删 / 按迭代器删 | O(log n) |
| `find(x)` | 找元素，返回迭代器（未找到返回 `end()`） | O(log n) |
| `count(x)` | 出现次数（set 只有 0/1；multiset 是真计数） | O(log n) |
| `lower_bound(x)` / `upper_bound(x)` | 第一个 ≥ / > x 的位置 | O(log n) |
| `size()` / `empty()` / `clear()` | 通用 | O(1) |

> 本质：只有 Key 没有 Value 的 map（你记过）。遍历时自动有序。

---

## 11. map / multimap（有序键值对）

```cpp
std::map<std::string, int> m;        // 按键排序
m["apple"] = 3;                       // 键不存在时自动插入默认值！
```

| 成员 | 功能 | 复杂度 |
|------|------|--------|
| `operator[](key)` | 查/插（不存在会**自动插入**默认值） | O(log n) |
| `at(key)` | 查（不存在抛异常） | O(log n) |
| `insert({k, v})` / `emplace(k, v)` | 插入（已存在则无效） | O(log n) |
| `erase(key)` / `erase(pos)` | 删除 | O(log n) |
| `find(key)` | 找键，返回迭代器 | O(log n) |
| `count(key)` | 键是否存在（0/1） | O(log n) |
| `lower_bound` / `upper_bound` | 按键找位置 | O(log n) |

> ⚠️ `operator[]` 大坑：只做"查询"时会污染容器（插入默认值）——查询优先用 `find`/`at`。
> 遍历 `for (const auto& [k, v] : m)`（结构化绑定）。

---

## 12. unordered_set / unordered_map（哈希版）

接口和 set/map **几乎一样**（insert/erase/find/count/at/operator[]），区别：

| | set / map | unordered_set / unordered_map |
|---|---|---|
| 底层 | 红黑树 | 哈希表 |
| 查找 | O(log n) | **O(1)** 平均 |
| 遍历顺序 | 按键排序 | **乱序** |
| `lower_bound` / `upper_bound` | ✅ | ❌ 没有 |

> 只想"快速查有没有 / 键查值"，用 unordered；需要"有序遍历 / 范围查询"，用 set/map。

---

## 13. 容器选型速查表

| 需求 | 选它 |
|------|------|
| 默认场景、频繁尾部增删 | `vector` |
| 频繁头部增删 | `deque` |
| 频繁中间增删 | `list` |
| 大小编译期确定、极致性能 | `array` |
| 后进先出（括号匹配、DFS、撤销） | `stack` |
| 先进先出（排队、BFS） | `queue` |
| 维护最值 / Top K | `priority_queue` |
| 有序 + 去重 | `set` |
| 键值对 + 按键有序 | `map` |
| 只追求查找快 | `unordered_set` / `unordered_map` |

---

# 第二章：STL 算法速查

> 聚焦 `<algorithm>` 和 `<numeric>` 的常用算法、惯用法与陷阱。

## 头文件

| 头文件 | 内容 |
|--------|------|
| `<algorithm>` | 大多数通用算法（查找、排序、修改、集合运算） |
| `<numeric>` | 数值算法（accumulate、inner_product、partial_sum 等） |

---

## 2.1 查找算法

| 算法 | 功能 | 返回值 | 复杂度 | 前提 |
|------|------|--------|--------|------|
| `find` | 找第一个等于 value 的元素 | 迭代器（未找到返回 `end`） | O(n) | 无 |
| `find_if` | 找第一个满足条件的元素 | 迭代器 | O(n) | 无 |
| `find_first_of` | 找第一个出现在另一个集合中的元素 | 迭代器 | O(n·m) | 无 |
| `binary_search` | 判断 value 是否存在 | `bool` | O(log n) | **已排序** |
| `lower_bound` | 第一个 ≥ value 的位置 | 迭代器 | O(log n) | **已排序** |
| `upper_bound` | 第一个 > value 的位置 | 迭代器 | O(log n) | **已排序** |
| `equal_range` | 所有等于 value 的范围 | `pair<迭代器, 迭代器>` | O(log n) | **已排序** |

```cpp
// 常用组合：统计等于 5 的个数
int cnt = std::upper_bound(vec.begin(), vec.end(), 5)
        - std::lower_bound(vec.begin(), vec.end(), 5);
```

---

## 2.2 计数与判断

| 算法 | 功能 | 返回值 | 复杂度 |
|------|------|--------|--------|
| `count` | 统计 value 出现次数 | 整数 | O(n) |
| `count_if` | 统计满足条件的个数 | 整数 | O(n) |
| `all_of` | 是否**全部**满足条件 | `bool` | O(n) |
| `any_of` | 是否有**至少一个**满足 | `bool` | O(n) |
| `none_of` | 是否**全不满足** | `bool` | O(n) |

```cpp
bool all_pos  = std::all_of(v.begin(), v.end(),  [](int x){ return x > 0; });
bool has_neg  = std::any_of(v.begin(), v.end(),  [](int x){ return x < 0; });
bool no_zero  = std::none_of(v.begin(), v.end(), [](int x){ return x == 0; });
```

---

## 2.3 修改式算法

| 算法 | 功能 | 复杂度 | 注意事项 |
|------|------|--------|----------|
| `copy` | 拷贝到目标区间 | O(n) | **目标必须有空间**，建议 `back_inserter` |
| `copy_if` | 条件拷贝（C++11） | O(n) | 同上 |
| `transform` | 逐个变换写入输出 | O(n) | 输出区间有效，支持一元/二元 |
| `replace` | 把 old_val 替换成 new_val | O(n) | 原地修改 |
| `replace_if` | 条件替换 | O(n) | 原地修改 |
| `fill` | 填充为指定值 | O(n) | |
| `generate` | 用生成器填充 | O(n) | 生成器是 callable |
| `remove` | **移动**元素，返回新逻辑末尾 | O(n) | **不真正删除！** |
| `remove_if` | 条件移动 | O(n) | **不真正删除！** |

### ⭐ remove-erase 惯用法

```cpp
// ❌ 错误：vec.size() 不变！
std::remove(vec.begin(), vec.end(), 42);

// ✅ 正确：remove + erase 配合
vec.erase(std::remove(vec.begin(), vec.end(), 42), vec.end());

// 条件删除所有偶数
vec.erase(
    std::remove_if(vec.begin(), vec.end(), [](int x){ return x % 2 == 0; }),
    vec.end()
);
```

### copy 安全写法

```cpp
std::vector<int> dest;
dest.reserve(src.size());                          // 预分配
std::copy(src.begin(), src.end(),
          std::back_inserter(dest));               // 安全插入
```

---

## 2.4 排序算法

| 算法 | 功能 | 复杂度 | 稳定性 | 适用场景 |
|------|------|--------|--------|----------|
| `sort` | 全排序（内省排序） | O(n log n) | ❌ 不稳定 | 通用排序 |
| `stable_sort` | 全排序（保持相等元素顺序） | O(n log n) | ✅ 稳定 | 需要保留原始顺序 |
| `partial_sort` | 前 k 个有序 | O(n log k) | ❌ | 只关心前 k 个 |
| `nth_element` | 第 k 小元素到位 | O(n) | ❌ | 找中位数/Top K |
| `merge` | 归并两个有序区间 | O(n+m) | ✅ | 归并排序子过程 |

```cpp
std::sort(v.begin(), v.end());                          // 升序
std::sort(v.begin(), v.end(), [](int a, int b){ return a > b; });  // 降序

// Top 3 最小的排到前面（且这 3 个内部有序）
std::partial_sort(v.begin(), v.begin() + 3, v.end());

// 找第 k 小（k 从 0 开始）
std::nth_element(v.begin(), v.begin() + k, v.end());
int kth = v[k];  // 第 k 小的元素
```

---

## 2.5 数值算法（`<numeric>`）

| 算法 | 功能 | 示例 | 复杂度 |
|------|------|------|--------|
| `accumulate` | 累加（或自定义二元操作） | `accumulate(v.begin(), v.end(), 0)` | O(n) |
| `inner_product` | 内积/点积 | `inner_product(a.begin(), a.end(), b.begin(), 0)` | O(n) |
| `partial_sum` | 前缀和 | `partial_sum(v.begin(), v.end(), out.begin())` | O(n) |
| `adjacent_difference` | 相邻差分 | `adjacent_difference(v.begin(), v.end(), out.begin())` | O(n) |

### ⚠️ accumulate 类型陷阱

```cpp
std::vector<int> v = {1, 2, 3};

auto avg1 = std::accumulate(v.begin(), v.end(), 0) / v.size();    // ❌ int 除法
auto avg2 = std::accumulate(v.begin(), v.end(), 0.0) / v.size();  // ✅ double

// 累乘
long long prod = std::accumulate(v.begin(), v.end(), 1LL,
                                 std::multiplies<long long>());
```

**核心**：第三个参数的类型决定结果类型和中间计算类型。

---

## 2.6 集合算法（两个容器都必须已排序）

| 算法 | 功能 | 复杂度 |
|------|------|--------|
| `set_union` | 并集 | O(n+m) |
| `set_intersection` | 交集 | O(n+m) |
| `set_difference` | 差集（在 A 不在 B） | O(n+m) |
| `set_symmetric_difference` | 对称差集（只在一边出现） | O(n+m) |
| `includes` | 判断 A 是否包含 B 所有元素 | O(n+m) |

```cpp
// 前提：a 和 b 都已排序
std::vector<int> result;

std::set_union(a.begin(), a.end(), b.begin(), b.end(),
               std::back_inserter(result));

std::set_intersection(a.begin(), a.end(), b.begin(), b.end(),
                      std::back_inserter(result));
```

---

## 2.7 算法选择速查表

| 需求 | 推荐算法 | 复杂度 | 前提 |
|------|---------|--------|------|
| 找第一个匹配值 | `find` | O(n) | 无 |
| 找第一个满足条件 | `find_if` | O(n) | 无 |
| 判断值是否存在 | `binary_search` | O(log n) | 已排序 |
| 找插入位置 | `lower_bound` | O(log n) | 已排序 |
| 统计出现次数 | `count` / `count_if` | O(n) | 无 |
| 拷贝 | `copy` / `copy_if` | O(n) | 目标有空间 |
| 变换 | `transform` | O(n) | 输出区间有效 |
| 真正删除元素 | `remove` + `erase` | O(n) | 顺序容器 |
| 全排序 | `sort` | O(n log n) | 随机访问迭代器 |
| 稳定排序 | `stable_sort` | O(n log n) | 随机访问迭代器 |
| 前 k 个有序 | `partial_sort` | O(n log k) | 随机访问迭代器 |
| 第 k 小元素 | `nth_element` | O(n) | 随机访问迭代器 |
| 求和 | `accumulate` | O(n) | 无 |
| 内积 | `inner_product` | O(n) | 无 |
| 前缀和 | `partial_sum` | O(n) | 无 |
| 集合运算 | `set_*` | O(n+m) | 两个都有序 |

---

## 2.8 常见陷阱清单

| 陷阱 | 正确做法 |
|------|---------|
| `remove` 后直接认为删掉了 | 必须 `erase(remove(...), end())` |
| `copy` 到空 vector | 先 `reserve` + `back_inserter`，或先 `resize` |
| 对未排序容器用 `binary_search` | 先 `sort`，或改用 `find` |
| `accumulate` 初始值传 `0` 却期望浮点 | 想算浮点传 `0.0`，类型决定结果 |
| 对 list 用 `std::sort` | list 有自带 `.sort()` 成员函数 |
| 集合算法前忘记排序 | 两个容器都必须先排序 |
| 以为 `stack.pop()` 会返回栈顶 | `pop()` 无返回值，取栈顶要 `top()` 再 `pop()` |
| 用 `map[k]` 只想查询 | 查询用 `find`/`at`，`operator[]` 会插入默认值 |

---

## Notion 同步

- 本文档为主，算法相关知识点同步到 Notion `📘 C++ 学习知识库` 的 **19. 算法** 条目
- 掌握后可打勾归档，更新状态为「完成」

---

> 📝 **使用说明**：每学一个新容器/新算法，补充到对应章节表格中。复习时遮住"功能"列，看容器名/算法名能想起用法就过。
