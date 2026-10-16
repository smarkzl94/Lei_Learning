# 专题-07 实战：同一份「看起来答对了」的结果，轨迹评测可以把蒙对的挑出来
# 零依赖。换电脑后：python agent07_trace_eval.py
# 先读 ../07_评测安全与上线.md 第 2 节和第 8 节。
# 建议改动：把坏轨迹里的重复 search 删掉，看轨迹评测从失败变成通过。

import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# 每步：name / args / observation。name 为 finish 表示最终回答。
TRACES = {
    "好轨迹": [
        {"name": "search", "args": {"q": "Tesla revenue"}, "observation": "255 vs 249"},
        {"name": "calculator", "args": {"expr": "(255-249)/249*100"}, "observation": "2.41"},
        {"name": "finish", "args": {}, "observation": "同比增长约 2.41%。"},
    ],
    "蒙对的坏轨迹": [
        {"name": "search", "args": {"q": "Tesla"}, "observation": "无关新闻"},
        {"name": "search", "args": {"q": "Tesla"}, "observation": "无关新闻"},
        {"name": "search", "args": {"q": "Tesla"}, "observation": "无关新闻"},
        {"name": "search", "args": {"q": "Tesla"}, "observation": "无关新闻"},
        {"name": "finish", "args": {}, "observation": "同比增长约 2.41%。"},
    ],
    "出错后换路": [
        {"name": "calculator", "args": {"expr": "import os"}, "observation": "工具执行失败：不允许的语法"},
        {"name": "calculator", "args": {"expr": "(255-249)/249*100"}, "observation": "2.41"},
        {"name": "finish", "args": {}, "observation": "同比增长约 2.41%。"},
    ],
}


def trajectory_issues(steps, max_steps=6):
    issues = []
    actions = [step for step in steps if step["name"] != "finish"]
    if len(actions) > max_steps:
        issues.append(f"工具步数 {len(actions)} 超过 {max_steps}")
    seen = []
    for step in actions:
        key = (step["name"], json.dumps(step["args"], sort_keys=True, ensure_ascii=False))
        if key in seen:
            issues.append(f"重复调用 {step['name']} {step['args']}")
        seen.append(key)
    for prev, cur in zip(actions, actions[1:]):
        failed = "失败" in prev["observation"]
        same = prev["name"] == cur["name"] and prev["args"] == cur["args"]
        if failed and same:
            issues.append("工具失败后用相同参数再叫了一次")
    if steps[-1]["name"] != "finish":
        issues.append("没有最终回答")
    return issues


def end_to_end_pass(steps):
    """只看最后一句像不像答完了。这是会把蒙对判成成功的那一层。"""
    return "2.41" in steps[-1]["observation"]


def main():
    print("规则：不重复调用；失败后要换参数或换工具；工具步数 ≤ 6；必须有最终回答。")
    print("端到端只检查最后一句里有没有 2.41。")
    print()
    for name, steps in TRACES.items():
        issues = trajectory_issues(steps)
        e2e = end_to_end_pass(steps)
        print("=" * 50)
        print(name)
        print("=" * 50)
        for step in steps:
            print(f"  {step['name']} {step['args']} → {step['observation']}")
        print("端到端：", "通过" if e2e else "失败")
        print("轨迹：", "通过" if not issues else "失败")
        for issue in issues:
            print("  -", issue)
        print()

    good = trajectory_issues(TRACES["好轨迹"])
    lucky = trajectory_issues(TRACES["蒙对的坏轨迹"])
    recovered = trajectory_issues(TRACES["出错后换路"])
    if good or not lucky or recovered:
        raise SystemExit("自检失败")
    if not all(end_to_end_pass(steps) for steps in TRACES.values()):
        raise SystemExit("这三份轨迹的端到端都应是通过，用来对照轨迹层")
    print("自检通过。")
    print("只看端到端时，三份都像成功。轨迹层把「同一句搜索重复四次然后突然答对」抓出来了。")


if __name__ == "__main__":
    main()
