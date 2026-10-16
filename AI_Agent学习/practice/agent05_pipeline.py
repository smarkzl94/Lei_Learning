# 专题-06 实战：两个 Agent 的流水线。写手只收到结论，不接收研究员的检索流水
# 零依赖，不安装 CrewAI。换电脑后：python agent05_pipeline.py
# 先读 ../06_多智能体与MCP生态.md 第 1～3 节。
# 有 API key 之后再把 role/goal 搬进 CrewAI。本文件先把「上下文隔离」跑明白。
# 建议改动：把 writer 的入参改成 research_log，看上下文膨胀多少。

import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


def researcher(topic):
    """自己的上下文里有三次搜索的原文。交出去的只有 5 条结论。"""
    searches = [
        (f"{topic} 定义", "Agent 是模型加工具、记忆、规划，按观察结果多步执行。"),
        (f"{topic} 工具协议", "MCP 把工具接口收成一套，应用和工具不必两两对接。"),
        (f"{topic} 常见失败", "死循环、工具选错、检索不到还硬答，是上线后最常见的三类事故。"),
    ]
    research_log = [f"角色：行业研究员。目标：收集 {topic} 的事实。"]
    for query, hit in searches:
        research_log.append(f"调用 search({query!r})")
        research_log.append("原文：" + (hit * 8))
    findings = [
        "Agent = 大脑（LLM）+ 工具 + 记忆 + 规划。",
        "执行权在程序，模型只输出调用意图。",
        "MCP 解决的是工具接口不统一，不是又一个聊天框架。",
        "单 Agent 加清楚的工具，覆盖大多数办公任务。",
        "上线前要有步数上限、轨迹记录和危险操作的人审。",
    ]
    research_log.append("结论已抽出，原文不必传给写手。")
    return findings, research_log


def writer(findings):
    context = ["角色：报告写手。只根据下面 5 条结论写，不要补没给的数字。"]
    context.extend(findings)
    report = [
        "AI Agent 开发简报",
        "1. 它和聊天机器人的差别在工具、拆步和根据结果改下一步。",
        "2. 模型不执行工具，程序执行，所以权限可以卡在程序里。",
        "3. 工具接口用统一协议接，避免每个产品和每个工具各写一套。",
        "4. 多数任务不必拆成一群 Agent。",
        "5. 没有步数上限和人审，就不算能上线。",
    ]
    return report, context


def chars(lines):
    return sum(len(line) for line in lines)


def main():
    findings, research_log = researcher("AI Agent 开发")
    report, writer_context = writer(findings)
    leaked = writer(research_log)[1]

    print("=" * 50)
    print("研究员自己的上下文（含三次搜索原文）")
    print("=" * 50)
    print(f"条数 {len(research_log)}，字符 {chars(research_log)}")
    print()
    print("=" * 50)
    print("写手实际收到的上下文（只有结论）")
    print("=" * 50)
    for line in writer_context:
        print("-", line)
    print(f"字符 {chars(writer_context)}")
    print()
    print("=" * 50)
    print("如果把检索流水整段塞给写手")
    print("=" * 50)
    print(f"字符 {chars(leaked)}，大约是结论版的 {chars(leaked) / chars(writer_context):.1f} 倍")
    print()
    print("=" * 50)
    print("写手产出")
    print("=" * 50)
    print("\n".join(report))
    print()

    if chars(leaked) <= chars(writer_context):
        raise SystemExit("自检失败：全量转交应该更长。")
    if any("原文：" in line for line in writer_context):
        raise SystemExit("自检失败：写手不应看到搜索原文。")
    print("自检通过。")
    print("CrewAI 里的 context=[task1] 就应该传这种结论，而不是整个 messages。")


if __name__ == "__main__":
    main()
