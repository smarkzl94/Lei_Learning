# 专题-08 实战：模型写出代码，你在子进程里跑，标准输出变成 Observation
# 零依赖。换电脑后：python agent08_code_sandbox.py
# 先读 ../08_代码执行与上下文工程.md。
# 静态检查挡 import / open；子进程超时挡住死循环。
# 子进程挡不住「代码本身去读磁盘」——那要靠别给权限。本练习把这件事演示清楚，不去读敏感文件。
# 建议改动：把静态检查临时注释掉，再跑「import os」那条，看子进程里它是能成功的。

import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BLOCKED = ("import ", "import\t", "open(", "exec(", "eval(", "__")


def run_model_code(code, timeout=1.0, check=True):
    if check:
        hit = [word for word in BLOCKED if word in code]
        if hit:
            return {
                "ok": False,
                "stdout": "",
                "stderr": "静态检查拒绝，命中：" + "、".join(hit),
            }
    try:
        completed = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "stdout": "", "stderr": f"超过 {timeout} 秒，子进程已放弃等待"}
    return {
        "ok": completed.returncode == 0,
        "stdout": (completed.stdout or "").strip(),
        "stderr": (completed.stderr or "").strip(),
    }


def show(title, code, **kwargs):
    print("=" * 50)
    print(title)
    print("=" * 50)
    print("代码：", code)
    result = run_model_code(code, **kwargs)
    print("ok：", result["ok"])
    print("stdout：", result["stdout"] or "（空）")
    print("stderr：", result["stderr"] or "（空）")
    print()
    return result


def main():
    growth = show(
        "任务 1：计算同比，标准输出就是观察",
        "print(round((255 - 249) / 249 * 100, 2))",
    )
    blocked = show(
        "任务 2：带 import 的代码在进子进程之前被拒绝",
        "import os\nprint(os.name)",
    )
    timed = show(
        "任务 3：死循环被超时截住，当前这个练习进程还在",
        "while True:\n    pass",
        timeout=0.5,
    )
    unchecked = show(
        "任务 4：关掉静态检查后，子进程里 import os 是成功的",
        "import os\nprint(os.name)",
        check=False,
    )
    print("读结果时注意：")
    print("- 任务 4 只打印了操作系统名字（Windows 上一般是 nt）。没有列目录，没有读文件。")
    print("- 它说明：子进程的作用是别让用户代码弄垮你的 Agent 进程，以及可以超时杀掉。")
    print("- 它不能代替权限。不检查的话，同一段代码也可以去读盘。生产环境还要只读目录、禁网、单独的系统用户。")

    if growth["stdout"] != "2.41":
        raise SystemExit("自检失败：同比计算应为 2.41")
    if blocked["ok"] or "静态检查" not in blocked["stderr"]:
        raise SystemExit("自检失败：import 应被静态检查拒绝")
    if timed["ok"] or "超过" not in timed["stderr"]:
        raise SystemExit("自检失败：死循环应超时")
    if not unchecked["ok"]:
        raise SystemExit("自检失败：关闭检查后的 import os 应该能跑完")
    print()
    print("自检通过。")


if __name__ == "__main__":
    main()
