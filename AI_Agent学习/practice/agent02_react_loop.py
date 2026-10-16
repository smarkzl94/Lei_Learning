# 专题-03 实战：手写 ReAct 循环，消息格式按真实 API（tool_calls + tool_call_id）
# 零依赖。换电脑后在本目录执行：python agent02_react_loop.py
# 先读 ../03_工具调用与ReAct.md 第 4 节和第 7 节。
# 建议改动：把任务 2 的 max_steps 改成 6；把任务 3 的计算器加回去，看恢复路径消失。

import ast
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def safe_calc(expr):
    """只允许数字和四则运算。不把 eval 暴露给任意字符串。"""
    tree = ast.parse(expr, mode="eval")
    allowed = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.UAdd, ast.USub,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError(f"不允许的语法：{type(node).__name__}")
    return eval(compile(tree, "<calc>", "eval"), {"__builtins__": {}}, {})


def tool_search(q):
    if "Tesla" in q or "特斯拉" in q or "营收" in q:
        return "Tesla 最新季度营收 255 亿美元，去年同期 249 亿美元。"
    return f"没有找到与 {q} 相关的资料。"


def tool_calculator(expr):
    value = safe_calc(expr)
    return f"{expr} = {round(float(value), 2)}"


def tool_weather(city):
    table = {"北京": "晴，26℃", "上海": "小雨，22℃"}
    if city not in table:
        raise ValueError(f"没有 {city} 的天气")
    return f"{city}：{table[city]}"


TOOLS = {
    "search": tool_search,
    "calculator": tool_calculator,
    "get_weather": tool_weather,
}


def mock_llm(messages, tools):
    """按对话里已经出现的工具结果决定下一步。这是在模仿模型，不是框架。"""
    goal = messages[0]["content"]
    observations = [m["content"] for m in messages if m["role"] == "tool"]
    blob = "\n".join(observations)

    if "机票" in goal:
        return {"type": "final", "content": "请补充出发城市和日期。缺这些信息时我不会去查航班。"}

    if "天气" in goal and "北京" in goal and "上海" in goal:
        if not observations:
            return {"type": "calls", "calls": [
                {"name": "get_weather", "args": {"city": "北京"}},
                {"name": "get_weather", "args": {"city": "上海"}},
            ]}
        return {"type": "final", "content": "；".join(observations)}

    if "同比" in goal:
        if "2.41" in blob or "约 2.41" in blob:
            return {"type": "final", "content": "同比增长约 2.41%。"}
        if "不存在工具 calculator" in blob:
            return {"type": "final", "content": "计算器不在工具列表里。根据观察 255 和 249，同比约 (255-249)/249 ≈ 2.41%。"}
        if "255" not in blob:
            return {"type": "calls", "calls": [{"name": "search", "args": {"q": "Tesla revenue"}}]}
        return {"type": "calls", "calls": [{"name": "calculator", "args": {"expr": "(255-249)/249*100"}}]}

    return {"type": "final", "content": "这个练习 mock 只认识同比、天气和订票三类目标。"}


def run_agent(goal, tools, max_steps=6):
    messages = [{"role": "user", "content": goal}]
    for step in range(max_steps):
        decision = mock_llm(messages, tools)
        if decision["type"] == "final":
            messages.append({"role": "assistant", "content": decision["content"]})
            return messages, decision["content"]

        assistant = {"role": "assistant", "content": None, "tool_calls": []}
        for index, call in enumerate(decision["calls"]):
            assistant["tool_calls"].append({
                "id": f"call_{step}_{index}",
                "type": "function",
                "function": {
                    "name": call["name"],
                    "arguments": json.dumps(call["args"], ensure_ascii=False),
                },
            })
        messages.append(assistant)

        for tool_call in assistant["tool_calls"]:
            name = tool_call["function"]["name"]
            call_id = tool_call["id"]
            try:
                args = json.loads(tool_call["function"]["arguments"])
            except json.JSONDecodeError as exc:
                observation = f"参数不是合法 JSON：{exc}"
            else:
                fn = tools.get(name)
                if fn is None:
                    observation = f"错误：不存在工具 {name}，可用工具：{list(tools)}"
                else:
                    try:
                        observation = str(fn(**args))
                    except Exception as exc:
                        observation = f"工具执行失败：{exc}"
            if len(observation) > 180:
                observation = observation[:180] + "…（已截断）"
            messages.append({
                "role": "tool",
                "tool_call_id": call_id,
                "content": observation,
            })
    return messages, "达到最大步数，任务未完成"


def print_trace(title, messages, final):
    print("=" * 50)
    print(title)
    print("=" * 50)
    for message in messages:
        role = message["role"]
        if role == "user":
            print(f"[user] {message['content']}")
        elif role == "assistant" and message.get("tool_calls"):
            for tool_call in message["tool_calls"]:
                fn = tool_call["function"]
                print(f"[assistant tool_call id={tool_call['id']}] {fn['name']} {fn['arguments']}")
        elif role == "assistant":
            print(f"[assistant final] {message['content']}")
        elif role == "tool":
            print(f"[tool {message['tool_call_id']}] {message['content']}")
    print(f"返回值：{final}")
    print()


def main():
    sample = {
        "role": "assistant",
        "content": None,
        "tool_calls": [{
            "id": "call_0_0",
            "type": "function",
            "function": {"name": "search", "arguments": "{\"q\": \"Tesla revenue\"}"},
        }],
    }
    print("真实接口里，模型想调工具时返回的是这种消息。arguments 是字符串，不是对象。")
    print(json.dumps(sample, ensure_ascii=False, indent=2))
    print("下一条必须是 role=tool，而且 tool_call_id 对得上 call_0_0。对不上，模型就看不到结果。")
    print()

    messages, final = run_agent(
        "特斯拉营收 255 亿美元，去年同期 249 亿，同比涨了多少？",
        TOOLS,
    )
    print_trace("任务 1：先搜索，再计算", messages, final)

    messages, final = run_agent(
        "特斯拉营收 255 亿美元，去年同期 249 亿，同比涨了多少？",
        TOOLS,
        max_steps=1,
    )
    print_trace("任务 2：max_steps=1，刹车", messages, final)

    no_calc = {name: fn for name, fn in TOOLS.items() if name != "calculator"}
    messages, final = run_agent(
        "特斯拉营收 255 亿美元，去年同期 249 亿，同比涨了多少？",
        no_calc,
    )
    print_trace("任务 3：删掉计算器，错误回灌后改走直接回答", messages, final)

    messages, final = run_agent("今天北京和上海的天气怎么样？", TOOLS)
    print_trace("任务 4：互不依赖的两件天气，同一轮并行", messages, final)

    messages, final = run_agent("帮我订一张去上海的机票", TOOLS)
    print_trace("任务 5：目标缺字段，先问人，不调工具", messages, final)

    _, task1_final = run_agent(
        "特斯拉营收 255 亿美元，去年同期 249 亿，同比涨了多少？",
        TOOLS,
    )
    _, stopped = run_agent(
        "特斯拉营收 255 亿美元，去年同期 249 亿，同比涨了多少？",
        TOOLS,
        max_steps=1,
    )
    if "2.41" not in task1_final or "最大步数" not in stopped:
        raise SystemExit("自检失败")
    print("自检通过。")


if __name__ == "__main__":
    main()
