# 专题-06 实战：教学用的 MCP 报文。不安装官方 SDK，不启子进程。
# 零依赖。换电脑后：python agent06_mini_mcp.py
# 字段名沿用 MCP：initialize、tools/list、tools/call。不是逐字节的协议实现。
# 先读 ../06_多智能体与MCP生态.md 第 4 节和第 7 节。
# 建议改动：把 ALLOW 里的 delete_note 加进去，看宿主过滤消失之后模型能看见删除工具。

import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

NOTES = {"周报": "本周读完 Agent 01 到 03，练习还没跑。"}
ALLOW = {"read_note", "add"}


def dump(obj):
    return json.dumps(obj, ensure_ascii=False)


class Server:
    def __init__(self):
        self.tools = {
            "add": {
                "description": "把两个数相加",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"},
                    },
                    "required": ["a", "b"],
                },
                "fn": lambda a, b: str(a + b),
            },
            "read_note": {
                "description": "按标题读一条本地笔记",
                "inputSchema": {
                    "type": "object",
                    "properties": {"title": {"type": "string"}},
                    "required": ["title"],
                },
                "fn": lambda title: NOTES.get(title, f"没有标题为 {title} 的笔记"),
            },
            "delete_note": {
                "description": "按标题删除笔记。危险：不可恢复。",
                "inputSchema": {
                    "type": "object",
                    "properties": {"title": {"type": "string"}},
                    "required": ["title"],
                },
                "fn": lambda title: NOTES.pop(title, None) or "已删除",
            },
        }

    def handle(self, message):
        method = message["method"]
        if method == "initialize":
            return {"protocolVersion": "2025-03-26", "capabilities": {"tools": {}}}
        if method == "tools/list":
            listed = []
            for name, spec in self.tools.items():
                listed.append({
                    "name": name,
                    "description": spec["description"],
                    "inputSchema": spec["inputSchema"],
                })
            return {"tools": listed}
        if method == "tools/call":
            name = message["params"]["name"]
            args = message["params"].get("arguments") or {}
            spec = self.tools.get(name)
            if spec is None:
                return {"content": [{"type": "text", "text": f"未知工具 {name}"}], "isError": True}
            try:
                text = spec["fn"](**args)
            except TypeError as exc:
                return {"content": [{"type": "text", "text": f"参数错误：{exc}"}], "isError": True}
            return {"content": [{"type": "text", "text": text}], "isError": False}
        raise ValueError(f"未实现的方法 {method}")


def rpc(method, params, rpc_id):
    return {"jsonrpc": "2.0", "id": rpc_id, "method": method, "params": params}


def main():
    server = Server()
    print("下面每一对都是：宿主发出的请求，然后是服务端的结果。")
    print("真接 MCP 时，这两段 JSON 走 stdio 或 HTTP，不走 import。")
    print()

    batches = [
        rpc("initialize", {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "study-host", "version": "0.1"},
        }, 1),
        rpc("tools/list", {}, 2),
        rpc("tools/call", {"name": "add", "arguments": {"a": 255, "b": -249}}, 3),
        rpc("tools/call", {"name": "read_note", "arguments": {"title": "周报"}}, 4),
        rpc("tools/call", {"name": "no_such_tool", "arguments": {}}, 5),
    ]
    results = {}
    for request in batches:
        result = server.handle(request)
        results[request["id"]] = result
        print("宿主 →", dump(request))
        print("服务端 ←", dump({"jsonrpc": "2.0", "id": request["id"], "result": result}))
        print()

    all_names = [tool["name"] for tool in results[2]["tools"]]
    visible = [name for name in all_names if name in ALLOW]
    print("=" * 50)
    print("权限：服务端有的工具，不等于模型看得到的工具")
    print("=" * 50)
    print("服务端 tools/list：", all_names)
    print("宿主允许放进模型上下文的：", visible)
    print("delete_note 留在服务端，但不放进这一轮的工具清单。")
    print()
    print("和 03 篇的关系：tools/list 拿回来的 inputSchema 就是 Function Calling 的 JSON Schema。")
    print("模型选定名字和参数之后，宿主再发 tools/call，结果照样用 tool_call_id 回灌。")

    add_text = results[3]["content"][0]["text"]
    if add_text != "6" or "delete_note" not in all_names or "delete_note" in visible:
        raise SystemExit("自检失败")
    if not results[5]["isError"]:
        raise SystemExit("未知工具应返回 isError")
    print("自检通过。")


if __name__ == "__main__":
    main()
