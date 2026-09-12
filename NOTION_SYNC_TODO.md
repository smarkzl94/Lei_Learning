# Notion 同步与重排序 · 执行手册

> 给下一个会话的 Kimi：请按本手册执行 Notion 同步。所有物料已备齐，无需再问用户。
> 触发语：用户说「执行 Notion 同步和重排序」或「读 NOTION_SYNC_TODO.md 并执行」。

## 背景

- 本地仓库：`C:\Users\Lei\Code\Learn`（GitHub: smarkzl94/Lei_Learning）
- Notion 侧是一个**数据库**，条目属性：`知识点`（标题）、`阶段`、`优先级`（P0-核心/P1-重要/P2-了解）
- 已有 C++ 26 条 + ROS 27 条（页面 ID 见 `notion_sync_map.py`）
- **问题 1**：PyTorch 16 章从未同步到 Notion
- **问题 2**：C++/ROS 条目编号按「阶段+优先级」排的，与本地章节学习顺序不一致

## 执行步骤

### 第 0 步：定位数据库
1. 用 Notion MCP `fetch` 拉取任一已知页面，例如 `3c9503fb-d69f-8186-a635-c7dde92d1b39`（什么是ROS），从其 parent 拿到数据库 / data source URL（`collection://...`）
2. `fetch` 该数据库拿到 data source schema，确认属性名（知识点/阶段/优先级）

### 第 1 步：创建 PyTorch 16 条记录
- 数据源：`pytorch_sync_manifest.json`（16 条，含 知识点/阶段/优先级/顺序）
- 内容源：`pytorch_notes_content.json`（知识点 -> 笔记全文 markdown）
- 用 `create-pages`（parent = 第 0 步的 data_source_id）分批创建，每批 ≤ 5 条
- 标题格式：`NN 知识点`（两位序号，如 `01 张量与运算`），序号 = manifest 里的 order
- 属性：阶段、优先级 按 manifest 填写

### 第 2 步：重命名 ROS 27 条标题
- 按 `ros_reorder_manifest.json`：对每条记录用 `update-page`（command=update_properties）把标题改为 `建议新标题`（`NN 知识点`，如 `04 第一个ROS程序小海龟`）
- page_id 已在清单中给出

### 第 3 步：重命名 C++ 26 条标题
- 按 `cpp_reorder_manifest.json`，同第 2 步

### 第 4 步：回写与收尾
1. 把新建的 16 个 PyTorch 页面 ID 追加到 `notion_sync_map.py`，新增 `PYTORCH_PAGE_IDS = {...}` 字典，并并入 `ALL_PAGE_IDS`
2. `git add -A && git commit -m "feat: PyTorch同步Notion(16章) + C++/ROS标题按本地顺序重编号" && git push origin main`
3. 向用户汇报：创建/重命名各多少条、有无失败、Notion 数据库链接

## 注意事项

- 每步执行前先核对数量（16/27/26），缺 page_id 就停下来报告
- 写操作前把计划简要给用户看一眼（本手册即计划，用户触发语即确认）
- 不要删除任何已有页面；只新增和重命名
- 如果 Notion MCP 调用失败，立即停止并如实报告，不要空转重试
