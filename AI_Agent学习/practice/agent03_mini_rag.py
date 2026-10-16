# 专题-04 实战：切分、粗向量检索、关键词检索、混合、检索不到就说不知道
# 零依赖。换电脑后在本目录执行：python agent03_mini_rag.py
# 先读 ../04_RAG检索增强.md 第 3～5 节和第 9～10 节。
# 向量这里故意把数字抹掉，用来模仿「语义很像、但型号错了」。真 Embedding 模型没这么笨，精确编号仍然经常看走眼。
# 建议改动：把 hybrid 里的 0.45 / 0.55 换成 1/0，只看向量，型号题会更差。

import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

DOCS = [
    "员工年假：入职满一年 5 天，满三年 10 天，满十年 15 天。",
    "报销制度：差旅需在出差结束后 30 天内提交发票。",
    "远程办公：每周最多两天，需要提前在系统里登记。",
    "iPhone 16 Pro 的价格：7999 元。",
    "iPhone 17 Pro 官方售价 8999 元，256GB 起。",
    "会议室预定：至少提前一天在系统里预约。",
    "密码策略：90 天更换一次，长度至少 12 位。",
    "新人培训：入职第一周必须完成安全考试。",
    "加班制度：工作日加班可调休，法定节假日按 3 倍工资。",
    "设备申领：电脑故障找 IT，工单号必填。",
]


def bigrams(text):
    compact = re.sub(r"\s+", "", text)
    return [compact[i:i + 2] for i in range(len(compact) - 1)]


def coarse(text):
    """抹掉数字，让 16 和 17 在向量空间里变得很像。"""
    return re.sub(r"\d+", "#", text)


def build_vocab(docs):
    vocab = []
    seen = set()
    for doc in docs:
        for gram in bigrams(coarse(doc)):
            if gram not in seen:
                seen.add(gram)
                vocab.append(gram)
    return vocab


VOCAB = build_vocab(DOCS)


def vectorize(text):
    counts = Counter(bigrams(coarse(text)))
    return [counts[token] for token in VOCAB]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def keyword_score(query, doc):
    """英文和数字按整词计；中文按查询里出现过的二字片段计。数字权重大，用来抓住型号。"""
    score = 0.0
    for token in re.findall(r"[A-Za-z]+|\d+", query):
        if token in doc:
            score += 5.0 if token.isdigit() else 1.0
    compact = re.sub(r"\s+", "", query)
    for i in range(len(compact) - 1):
        gram = compact[i:i + 2]
        if re.search(r"[\u4e00-\u9fff]{2}", gram) and gram in doc:
            score += 1.0
    return score


DOC_VECTORS = [vectorize(doc) for doc in DOCS]


def score_all(query):
    qv = vectorize(query)
    rows = []
    for doc, dv in zip(DOCS, DOC_VECTORS):
        vec = cosine(qv, dv)
        kw = keyword_score(query, doc)
        # 用绝对分。不要做 min-max：那样第一名永远变成 1，检索失败也像满分。
        hybrid = vec + 0.2 * kw
        rows.append((doc, vec, kw, hybrid))
    return rows


def rank(query, mode="hybrid", k=3):
    index = {"vector": 1, "keyword": 2, "hybrid": 3}[mode]
    rows = sorted(score_all(query), key=lambda row: row[index], reverse=True)
    return [(row[0], row[index]) for row in rows[:k]]


def print_rank(title, query):
    print("=" * 50)
    print(title)
    print(f"问题：{query}")
    print("=" * 50)
    for mode in ("vector", "keyword", "hybrid"):
        print(f"[{mode}]")
        for text, score in rank(query, mode=mode):
            print(f"  {score:.3f}  {text}")
    print()


def grounded(query):
    """第一名要在关键词上明显领先，并且向量分不是 0。并列第一视为没把握。"""
    rows = sorted(score_all(query), key=lambda row: (row[2], row[1]), reverse=True)
    best, second = rows[0], rows[1]
    ok = best[2] >= 1 and best[2] > second[2] and best[1] >= 0.05
    return best, ok


def answer(question):
    """分不够就改写再查一次；仍然分不清就承认不知道。"""
    best, ok = grounded(question)
    used_query = question
    if not ok:
        used_query = rewrite(question)
        print(f"首次没有把握（关键词 {best[2]:.0f}，向量 {best[1]:.3f}），改写查询：{used_query}")
        best, ok = grounded(used_query)
    if not ok:
        return f"资料里没有足以回答的内容（改写后关键词 {best[2]:.0f}）。我不知道。", used_query
    return f"根据资料（关键词 {best[2]:.0f}，向量 {best[1]:.3f}）：{best[0]}", used_query


def rewrite(question):
    if "病假" in question:
        return "病假 请假 休假 假期 制度"
    if "年假" in question:
        return "员工年假 天数 入职"
    return question


def show_chunking():
    print("=" * 50)
    print("切分：按句号切开，相邻块重叠一句")
    print("=" * 50)
    raw = "员工年假入职满一年 5 天。满三年 10 天。满十年 15 天。请假需提前邮件审批。"
    parts = [p for p in raw.split("。") if p]
    chunks = []
    for i, part in enumerate(parts):
        prev = parts[i - 1] + "。" if i else ""
        chunks.append(prev + part + "。")
    for i, chunk in enumerate(chunks, 1):
        print(f"块 {i}：{chunk}")
    print()


def main():
    show_chunking()
    print_rank("对照：年假题，两路都应该找到年假那条", "年假有几天")
    print_rank("对照：型号题。粗向量分不清 16/17，关键词吃到数字 17", "iPhone 17 Pro 的价格")

    print("=" * 50)
    print("检索不到就停：病假不在这 10 条制度里")
    print("=" * 50)
    sick, _ = answer("病假怎么开")
    print(sick)
    print()
    print("=" * 50)
    print("库里有的问题：年假")
    print("=" * 50)
    leave, _ = answer("休年假要满足什么")
    print(leave)
    print()

    price_q = "iPhone 17 Pro 的价格"
    price_vector = rank(price_q, mode="vector", k=1)[0][0]
    price_keyword = rank(price_q, mode="keyword", k=1)[0][0]
    price_hybrid = rank(price_q, mode="hybrid", k=1)[0][0]
    if "16 Pro" not in price_vector:
        raise SystemExit("自检失败：抹掉数字后的向量应更偏向 16 那条测评。")
    if "17 Pro" not in price_keyword or "17 Pro" not in price_hybrid:
        raise SystemExit("自检失败：关键词和混合结果应落到 17 Pro 的售价。")
    if "不知道" not in sick or "年假" not in leave:
        raise SystemExit("自检失败：病假应拒答，年假应命中。")
    print("自检通过。")
    print("价格题向量第一名：", price_vector)
    print("价格题关键词第一名：", price_keyword)
    print("价格题混合第一名：", price_hybrid)


if __name__ == "__main__":
    main()
