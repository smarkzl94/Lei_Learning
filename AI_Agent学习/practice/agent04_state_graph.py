# 专题-05 实战：不用 LangGraph，手写 State / Node / Edge / 断点
# 零依赖。换电脑后在本目录执行：python agent04_state_graph.py
# 先读 ../05_记忆与规划.md 第 5 节和第 7～9 节。
# 装了 langgraph 之后，节点函数可以原样搬进 StateGraph，不必重写业务。
# 建议改动：把 step > 5 改成 step > 2，看条件边如何强制结束。

import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

END = "__end__"


class MemorySaver:
    """每个 thread_id 一份快照。进程还在时，可以停下来再续。"""

    def __init__(self):
        self.snapshots = {}

    def save(self, thread_id, state, next_node):
        self.snapshots[thread_id] = {"state": dict(state), "next_node": next_node}

    def load(self, thread_id):
        return self.snapshots.get(thread_id)


class StateGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.entry = None

    def add_node(self, name, fn):
        self.nodes[name] = fn

    def set_entry_point(self, name):
        self.entry = name

    def add_edge(self, src, dst):
        self.edges[src] = dst

    def add_conditional_edges(self, src, router):
        self.edges[src] = router

    def compile(self, checkpointer):
        return CompiledGraph(self, checkpointer)


class CompiledGraph:
    def __init__(self, graph, checkpointer):
        self.graph = graph
        self.checkpointer = checkpointer

    def invoke(self, state, thread_id, interrupt_before=None, resume=False):
        if resume:
            snap = self.checkpointer.load(thread_id)
            if snap is None:
                raise RuntimeError(f"没有 thread_id={thread_id} 的断点")
            state = snap["state"]
            node = snap["next_node"]
        else:
            node = self.graph.entry

        while node != END:
            if interrupt_before == node and not state.get("approved"):
                self.checkpointer.save(thread_id, state, node)
                print(f"  停在 {node} 之前，等待人工确认。thread_id={thread_id}")
                return {**state, "__interrupt__": node}

            update = self.graph.nodes[node](state)
            state = {**state, **update}
            shown = [
                f"{key}={state.get(key)}"
                for key in ("step", "pending", "answer", "draft", "sent")
                if state.get(key) is not None
            ]
            print(f"  节点 {node} 之后：" + " ".join(shown))
            nxt = self.graph.edges[node]
            node = nxt(state) if callable(nxt) else nxt
            self.checkpointer.save(thread_id, state, node)
        return state


def agent_node(state):
    step = state["step"] + 1
    if step > 5:
        return {"step": step, "pending": None, "answer": "步数超过 5，强制结束"}
    if state.get("revenue") is None:
        return {"step": step, "pending": "search"}
    if state.get("growth") is None:
        return {"step": step, "pending": "calculator"}
    return {"step": step, "pending": None, "answer": f"同比增长约 {state['growth']}%。"}


def tools_node(state):
    pending = state.get("pending")
    if pending == "search":
        return {"revenue": (255, 249), "pending": None}
    if pending == "calculator":
        cur, prev = state["revenue"]
        growth = round((cur - prev) / prev * 100, 2)
        return {"growth": growth, "pending": None}
    return {}


def route_after_agent(state):
    if state.get("answer"):
        return END
    if state.get("pending"):
        return "tools"
    return END


def draft_email_node(state):
    return {"draft": f"邮件草稿：{state['topic']}"}


def send_email_node(state):
    return {"sent": True, "answer": "已发送：" + state["draft"]}


def build_agent_graph(saver):
    graph = StateGraph()
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tools_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", route_after_agent)
    graph.add_edge("tools", "agent")
    return graph.compile(saver)


def build_email_graph(saver):
    graph = StateGraph()
    graph.add_node("draft", draft_email_node)
    graph.add_node("send", send_email_node)
    graph.set_entry_point("draft")
    graph.add_edge("draft", "send")
    graph.add_edge("send", END)
    return graph.compile(saver)


def main():
    print("=" * 50)
    print("任务 1：03 篇的循环写成状态图")
    print("=" * 50)
    saver = MemorySaver()
    app = build_agent_graph(saver)
    final = app.invoke({"step": 0, "revenue": None, "growth": None, "pending": None, "answer": None}, thread_id="t1")
    print("结束：", final.get("answer"))
    print()

    print("=" * 50)
    print("任务 2：发邮件前打断，确认后再续跑")
    print("=" * 50)
    mail_saver = MemorySaver()
    mail = build_email_graph(mail_saver)
    paused = mail.invoke({"topic": "周报", "approved": False}, thread_id="mail", interrupt_before="send")
    print("打断时还没发送，sent =", paused.get("sent"))
    paused["approved"] = True
    mail_saver.save("mail", paused, "send")
    done = mail.invoke({}, thread_id="mail", resume=True)
    print("确认之后：", done.get("answer"))
    print()

    print("=" * 50)
    print("任务 3：只跑到第一次存盘，换一次 invoke 从断点继续")
    print("=" * 50)
    saver2 = MemorySaver()
    app2 = build_agent_graph(saver2)

    def agent_once(state):
        update = agent_node(state)
        update["answer"] = None
        return update

    # 手动走一拍，模拟进程在第一圈之后停掉。
    state = {"step": 0, "revenue": None, "growth": None, "pending": None, "answer": None}
    state = {**state, **agent_node(state)}
    saver2.save("t2", state, "tools")
    print("存盘时 next_node=tools，revenue 仍是", state["revenue"])
    continued = app2.invoke({}, thread_id="t2", resume=True)
    print("续跑结束：", continued.get("answer"))

    if "2.41" not in str(final.get("answer")) or not done.get("sent"):
        raise SystemExit("自检失败")
    if "2.41" not in str(continued.get("answer")):
        raise SystemExit("断点续跑自检失败")
    print()
    print("自检通过。")
    print("和 05 篇 LangGraph 骨架的对应：add_node / add_conditional_edges / checkpointer。")
    print("以后 pip install langgraph，把 agent_node 和 tools_node 填进官方 StateGraph 即可。")


if __name__ == "__main__":
    main()
