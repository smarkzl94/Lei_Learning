# 专题-03 - 工具调用：Function Calling 与 ReAct

## 🎯 学习目标
- 理解 Function Calling 的完整机制：模型"决定"，程序"执行"
- 会写工具描述（JSON Schema），理解描述质量为什么决定调用质量
- 不用任何框架手写一个 ReAct Agent 循环（核心 < 50 行）
- 掌握工程护栏：最大圈数、超时、错误回灌、并行调用

---

## 📚 核心知识点

### 1. 核心认知：模型永远不会自己执行工具

先破除最大的误解：**Function Calling 不是模型去调函数，而是模型"说"它想调函数**。

模型是下一个词预测机（专题 05 学透了），它能做的只有输出文本——哪怕这段文本长得像一个函数调用。真正解析这段文本、找到对应函数、执行、拿到结果的，**永远是你的程序**。这个分工是一张安全闸门：执行权在程序手里，你可以在执行前检查、拒绝、记录、限权。

### 2. 完整时序：一图看懂

![Function Calling 时序](assets/react_loop_detail.png)

对应的消息序列（简化）：

```python
messages = [
    {"role": "user", "content": "特斯拉最新季度营收多少？"},
]
# 第 1 次请求：问题 + 工具清单一起发
resp = llm(messages, tools=[search_schema, calc_schema])
# 模型返回：tool_call{name: "search", args: {"q": "Tesla Q2 2026 revenue"}}
result = search(q="Tesla Q2 2026 revenue")     # ← 你的程序真的执行
messages += [resp.tool_call_message,
             {"role": "tool", "content": result}]  # 结果追加进对话
# 第 2 次请求：模型看到结果，决定"还要查去年同期"或"信息够了"
```

注意对话是**累积**的：每轮的请求都包含之前全部消息。这就是 01 篇说的"上下文随循环累积"。

### 3. 工具描述：写给人话看的接口文档

模型选择工具的唯一依据是**工具名 + 描述 + 参数说明**（都在 JSON Schema 里）：

```python
search_schema = {
    "name": "search",
    "description": "搜索互联网获取实时信息。当问题涉及当前事件、股价、天气等训练数据之后的信息时使用。不要用于常识问题。",  # ← 边界写清楚！
    "parameters": {
        "type": "object",
        "properties": {
            "q": {"type": "string", "description": "搜索关键词，用英文效果更好"}
        },
        "required": ["q"]
    }
}
```

三个经验法则：

- **描述里写"什么时候用、什么时候别用"**——没有边界，模型会对常识题也调搜索（浪费）或对实时问题硬答（幻觉）
- **参数说明写到"模型能独立填对"的程度**——单位、格式、示例都给
- **工具要原子化**：一个工具干一件事。"查天气"和"查天气然后发邮件"应该是两个工具，组合交给模型的规划能力

### 4. 手写 ReAct 循环：核心不到 50 行

把 01 篇的循环 + 本篇的工具机制拼起来：

```python
def run_agent(goal, tools, llm, max_steps=10):
    """最小 Agent 循环：思考 → 行动 → 观察，直到出答案或撞上限。"""
    messages = [{"role": "user", "content": goal}]
    for step in range(max_steps):                    # 刹车①：最大圈数
        resp = llm(messages, tools=tools.schemas)    # 思考：模型决定下一步
        if resp.is_final_answer:                     # 模型说"信息够了"
            return resp.content
        call = resp.tool_call                        # 模型说"我要调工具"
        fn = tools.get(call.name)
        if fn is None:                               # 护栏：模型瞎编了工具名
            observation = f"错误：不存在工具 {call.name}，可用工具：{tools.names}"
        else:
            try:
                observation = fn(**call.args)        # 行动：真的执行
            except Exception as e:                   # 护栏：工具本身出错
                observation = f"工具执行失败：{e}"    # 错误也喂回，让模型想办法
        messages += [resp.message, {"role": "tool", "content": str(observation)}]  # 观察
    return "达到最大步数，任务未完成"                  # 刹车②：兜底退出
```

每个部件都对应前面学过的：结构化输出（02 篇）保证 `call.name / call.args` 能解析；错误回灌让模型看到失败可以换路；`max_steps` 是防死循环的刹车。**LangChain/LangGraph 的 Agent 本质上就是这个循环加上百个工程细节。**

### 5. 工程护栏清单

| 护栏 | 防什么 | 做法 |
|---|---|---|
| 最大圈数 | 死循环 | `max_steps=10`，撞线返回"未完成" |
| 重复检测 | 原地打转 | 同工具同参数连续出现 → 提示模型换路 |
| 工具超时 | 卡死 | 每个工具调用包 `timeout` |
| 错误回灌 | 一次失败就放弃 | 异常信息喂回，让模型重试/换工具 |
| 危险操作人审 | 删库/发钱 | 这类工具执行前暂停，等人工确认（07 篇细讲） |

### 6. 进阶：并行工具调用

模型有时一次决定要调多个**互不依赖**的工具（"查北京天气 + 查上海天气"）。现代 API 支持一次返回多个 tool_call，程序用线程池并行执行，结果一起回灌——省一整轮往返。注意：有依赖关系的（"先搜股价，再算涨幅"）必须串行，模型通常会分轮要。

---

## 💻 实战练习（agent02_react_loop.py）

离线可跑：mock 一个"按规则回答的伪 LLM"+ 三个真工具（计算器、模拟搜索、当前时间），跑通本文的循环：
- 任务：「特斯拉营收 255 亿美元，去年同期 249 亿，同比涨了多少？」→ 观察它先调 search 再调 calculator
- 把 `max_steps` 调成 1 → 看兜底退出
- 删掉计算器工具 → 看"工具不存在"错误如何被回灌和修正

---

## ⚠️ 常见坑

1. 以为模型会自己执行工具——它只输出"想调什么"，执行是你的代码
2. 工具描述只有名字没有边界——模型乱调或不敢调
3. 把工具报错直接抛异常炸掉循环——错误应该回灌给模型，它常常能自己绕过去
4. 忘记上下文累积——每轮只发最新消息，模型瞬间"失忆"
5. 一个工具包打天下——巨型工具参数复杂，模型填不对；拆小才稳

---

## 📝 小结

- Function Calling 本质：模型输出结构化的"调用意图"，程序解析并执行，结果回灌
- 工具描述是写给人话看的接口文档，边界和参数说明决定调用质量
- ReAct 循环 = 结构化输出 + 工具执行 + 错误回灌 + 最大圈数，核心 < 50 行
- 框架 = 这个循环 + 状态管理 + 可视化 + 持久化（05 篇见）
- 下一步：专题-04，给 Agent 接上"外部记忆"——RAG 检索增强
