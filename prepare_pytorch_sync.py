# -*- coding: utf-8 -*-
"""提取 PyTorch 学习笔记，生成 Notion 同步准备文件。

产物：
1. pytorch_notes_content.json  —— 知识点名 -> 笔记全文（与 notes_content.json 同格式）
2. pytorch_sync_manifest.json  —— 16 个页面的同步清单（标题/阶段/优先级/顺序），
   阶段与优先级命名沿用 sort_notion_pages.py 中 C++/ROS 的约定。
"""
import os, json, glob

base = os.path.dirname(os.path.abspath(__file__))

# 阶段映射：本地章节目录 -> Notion 数据库「阶段」属性值
STAGE_MAP = {
    "01_基础入门": "基础入门",
    "02_神经网络基础": "神经网络基础",
    "03_数据加载与处理": "数据加载与处理",
    "04_卷积神经网络": "卷积神经网络",
    "05_序列模型": "序列模型",
    "06_实战项目": "实战项目",
    "07_强化学习": "强化学习",
}

# 优先级约定（沿用 C++/ROS：P0-核心 / P1-重要 / P2-了解）
PRIORITY_MAP = {
    "01_基础入门": "P0-核心",
    "02_神经网络基础": "P0-核心",
    "03_数据加载与处理": "P0-核心",
    "04_卷积神经网络": "P1-重要",
    "05_序列模型": "P1-重要",
    "06_实战项目": "P1-重要",
    "07_强化学习": "P2-了解",
}

def key_from_filename(path):
    key = os.path.splitext(os.path.basename(path))[0]
    if '_' in key:
        parts = key.split('_', 1)
        if parts[0].isdigit():
            return parts[1]
    return key

notes = {}
manifest = []
order = 0
for section_dir in sorted(STAGE_MAP.keys()):
    pattern = os.path.join(base, 'PyTorch学习', section_dir, '*.md')
    for p in sorted(glob.glob(pattern)):
        if os.path.basename(p) == 'README.md':
            continue
        key = key_from_filename(p)
        with open(p, 'r', encoding='utf-8') as f:
            notes[key] = f.read()
        order += 1
        manifest.append({
            "order": order,
            "知识点": key,
            "阶段": STAGE_MAP[section_dir],
            "优先级": PRIORITY_MAP[section_dir],
            "本地路径": os.path.relpath(p, base),
        })

with open('pytorch_notes_content.json', 'w', encoding='utf-8') as f:
    json.dump(notes, f, ensure_ascii=False, indent=2)

with open('pytorch_sync_manifest.json', 'w', encoding='utf-8') as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

print(f"提取 {len(notes)} 篇笔记 -> pytorch_notes_content.json")
print(f"生成 {len(manifest)} 条同步清单 -> pytorch_sync_manifest.json")
for m in manifest:
    print(f"  {m['order']:>2}. [{m['阶段']}|{m['优先级']}] {m['知识点']}")
