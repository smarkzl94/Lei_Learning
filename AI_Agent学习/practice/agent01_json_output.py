# 专题-02 实战：解析 → 校验 → 把错误喂回去 → 最多重试 3 次
# 零依赖。换电脑后在本目录执行：python agent01_json_output.py
# 先读 ../02_Prompt工程与结构化输出.md 第 4～5 节，再跑。
# 建议改动：把 feed_error 的实验关掉，对比「最终失败次数」。

import json
import random
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

GOOD = '{"action": "search", "args": {"q": "tesla revenue"}}'
BASE = "请严格输出 JSON，不要输出其他文字。"


def mock_llm(prompt, kind):
    """假装是一个偶尔说废话、偶尔写出坏 JSON 的模型。kind 固定，方便复现。"""
    if "上次输出有误" in prompt:
        return GOOD
    if kind == 0:
        return GOOD
    if kind == 1:
        return "好的，以下是 JSON：\n" + GOOD
    if kind == 2:
        return GOOD[:-1]
    return '{"foo": 1}'


def validate(data):
    if not isinstance(data, dict):
        raise ValueError("顶层必须是对象")
    if data.get("action") not in {"search", "calculator", "finish"}:
        raise ValueError(f"action 不在允许列表：{data.get('action')}")
    args = data.get("args")
    if not isinstance(args, dict) or "q" not in args:
        raise ValueError("args 里缺少字符串字段 q")
    return data


def run_once(kind, feed_error, max_attempts=3):
    prompt = BASE
    last_error = ""
    for _ in range(max_attempts):
        raw = mock_llm(prompt, kind)
        try:
            validate(json.loads(raw))
            return True, last_error
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = str(exc)
            if feed_error:
                prompt = BASE + f"\n上次输出有误：{last_error}，请修正"
    return False, last_error


def trial(feed_error, seed=0, n=100):
    rng = random.Random(seed)
    kinds = [rng.choices([0, 1, 2, 3], weights=[40, 25, 20, 15])[0] for _ in range(n)]
    fails = 0
    for kind in kinds:
        ok, _ = run_once(kind, feed_error=feed_error)
        if not ok:
            fails += 1
    return fails, n


def show_one_bad_case():
    print("=" * 50)
    print("单个坏例子：模型先说了一句人话")
    print("=" * 50)
    raw = mock_llm(BASE, kind=1)
    print("模型输出：")
    print(raw)
    try:
        json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"json.loads 失败：{exc}")
    fixed_prompt = BASE + "\n上次输出有误：Expecting value，请修正"
    print("把错误喂回去之后，模型输出：")
    print(mock_llm(fixed_prompt, kind=1))


def main():
    show_one_bad_case()
    print()
    print("=" * 50)
    print("100 次：同一种坏输出分布，两种重试策略")
    print("=" * 50)
    bad_no_feedback, n = trial(feed_error=False)
    bad_feedback, _ = trial(feed_error=True)
    print(f"不把错误喂回去：{n} 次里最终失败 {bad_no_feedback} 次")
    print(f"把错误喂回去：{n} 次里最终失败 {bad_feedback} 次")
    print()
    print("怎么读这个结果：")
    print("- 合法 JSON 还不等于结构对。{\"foo\": 1} 能解析，但过不了 validate。")
    print("- 不喂错误时，三次看到的是同一份输出，重试没有新信息。失败比例接近「第一次就写坏」的比例。")
    print("- 喂错误后，这个 mock 第二次就改对。真模型通常也会好一截，但不会永远改对，所以要有上限。")
    if bad_feedback != 0 or bad_no_feedback == 0:
        raise SystemExit("自检失败：喂回错误后失败次数应为 0，且不喂回时应该留下失败。")
    print("自检通过。")


if __name__ == "__main__":
    main()
