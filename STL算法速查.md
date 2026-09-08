# 📋 STL 算法速查

> 与 [知识速查卡](知识速查卡.md) 并列的专项整理，聚焦 `<algorithm>` 和 `<numeric>` 的常用算法、惯用法与陷阱。
> 
> 以表格为主，一眼扫到想用的算法。

---

## 头文件

| 头文件 | 内容 |
|--------|------|
| `<algorithm>` | 大多数通用算法（查找、排序、修改、集合运算） |
| `<numeric>` | 数值算法（accumulate、inner_product、partial_sum 等） |

---

## 1. 查找算法

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

## 2. 计数与判断

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

## 3. 修改式算法

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

## 4. 排序算法

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

## 5. 数值算法（`<numeric>`）

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

## 6. 集合算法（两个容器都必须已排序）

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

## 7. 算法选择速查表

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

## 8. 常见陷阱清单

| 陷阱 | 正确做法 |
|------|---------|
| `remove` 后直接认为删掉了 | 必须 `erase(remove(...), end())` |
| `copy` 到空 vector | 先 `reserve` + `back_inserter`，或先 `resize` |
| 对未排序容器用 `binary_search` | 先 `sort`，或改用 `find` |
| `accumulate` 初始值传 `0` 却期望浮点 | 想算浮点传 `0.0`，类型决定结果 |
| 对 list 用 `std::sort` | list 有自带 `.sort()` 成员函数 |
| 集合算法前忘记排序 | 两个容器都必须先排序 |

---

## Notion 同步

- 本文档为主，算法相关知识点同步到 Notion `📘 C++ 学习知识库` 的 **19. 算法** 条目
- 掌握后可打勾归档，更新状态为「完成」

---

> 📝 **使用说明**：每学一个新算法，补充到对应分类表格中。复习时遮住代码列，看算法名和功能描述能想起用法就过。
