# AI Agent 练习（离线，零依赖）

换电脑后只需要 Python 3.11 及以上。不要先装 LangChain、LangGraph、CrewAI。这些脚本用标准库演示原理，跑通再考虑框架和 API key。

在本目录执行：

```text
python agent01_json_output.py
python agent02_react_loop.py
python agent03_mini_rag.py
python agent04_state_graph.py
python agent05_pipeline.py
python agent06_mini_mcp.py
python agent07_trace_eval.py
python agent08_code_sandbox.py
```

每份脚本末尾打印「自检通过」才算这次跑对了。自检失败就先别改业务逻辑，把报错那一行和对应课文对一下。

## 和课文的对应

| 脚本 | 课文 | 跑完你应该能指着输出说出 |
|---|---|---|
| agent01 | 02 篇 | 同一份坏 JSON，不把错误喂回去会留下一大批最终失败；喂回去之后这一版 mock 的失败次数变成 0 |
| agent02 | 03 篇 | `tool_calls[].id` 和后面的 `tool_call_id` 成对；`max_steps=1` 会停；删掉计算器后错误被写回，模型改口 |
| agent03 | 04 篇 | 问价格时，抹掉数字的向量把「16 的价格」排第一，关键词把「17 的售价」排第一；问病假得到「我不知道」 |
| agent04 | 05 篇 | 节点按 agent → tools → agent 走；发邮件前能停住；从存盘的 next_node 续跑 |
| agent05 | 06 篇 | 写手只有 5 条结论；把检索流水塞过去，字符数大约变成 5.6 倍 |
| agent06 | 06 篇 | 报文是 initialize、tools/list、tools/call；delete_note 在服务端存在，但宿主没把它放进模型可见列表 |
| agent07 | 07 篇 | 三份轨迹的端到端都「通过」；重复搜索四次那份，轨迹评测失败 |
| agent08 | 08 篇 | 同比计算打出 2.41；`import os` 被静态检查拒绝；死循环超时；关掉检查后子进程里 `import os` 能跑完 |

## 每份脚本建议只改一处

脚本顶部注释里写了「建议改动」。一次只改那一处，再跑，看自检或打印哪里变了。同时改两处，就分不清是哪一处造成的。

## 真 API 以后再接

02 篇第 8 节有 DeepSeek 和 Ollama 的最小调用。Key 放环境变量，不要写进这个仓库。离线脚本没全部打印「自检通过」之前，先不要花钱调接口。
