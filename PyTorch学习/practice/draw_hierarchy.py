# 绘制「人工智能 ⊃ 机器学习 ⊃ 深度学习」三层嵌套图
# 输出: D:\Lei_learning\PyTorch学习\00_理论基础\assets\ai_ml_dl_hierarchy.png
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.font_manager as fm

# 找可用的中文字体
for name in ('Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei'):
    if any(name.lower() in f.name.lower() for f in fm.fontManager.ttflist):
        plt.rcParams['font.family'] = name
        break
plt.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(13.2, 7.2), dpi=150)
ax.set_xlim(0, 132); ax.set_ylim(0, 72); ax.axis('off')
fig.patch.set_facecolor('white')

INK    = '#1a1a1a'   # 主文字
GRAY   = '#6b6b6b'   # 次要文字
BORDER = '#9a9a9a'   # 边框
BLUE   = '#2f6fde'   # 强调（深度学习层）
BLUEBG = '#eef3fd'

def box(x, y, w, h, lw=1.2, ec=BORDER, fc='white', style='round,pad=0,rounding_size=1.2', dashed=False):
    p = FancyBboxPatch((x, y), w, h, boxstyle=style,
                       linewidth=lw, edgecolor=ec, facecolor=fc,
                       linestyle=(0, (4, 3)) if dashed else 'solid')
    ax.add_patch(p)
    return p

def text(x, y, s, size=12, color=INK, weight='normal', ha='left', va='top'):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va)

# ============ 第一层：人工智能（最外框）============
box(2, 3, 128, 60, lw=1.4)
text(5, 59.5, '人工智能', size=17, weight='bold')
text(24, 59.2, '目标：让机器表现得聪明（下棋、认图、对话、开车）', size=11.5, color=GRAY)

# AI 层的兄弟分支面板（左侧）
box(5, 10, 30, 42, dashed=True)
text(8, 48, '机器学习的兄弟分支', size=10.5, color=GRAY)
text(8, 42, '符号主义', size=13, weight='bold')
text(8, 37.5, '人写规则做推理', size=10.5, color=GRAY)
text(8, 34, '专家系统 · 知识图谱 · 搜索规划', size=10, color=GRAY)
text(8, 26, '行为主义', size=13, weight='bold')
text(8, 21.5, '感知-行动闭环', size=10.5, color=GRAY)
text(8, 18, '机器人控制，强化学习的源头', size=10, color=GRAY)

# ============ 第二层：机器学习 ============
box(38, 10, 89, 42, lw=1.4)
text(41, 48.5, '机器学习', size=15, weight='bold')
text(58, 48.2, '不手写规则，让机器从数据里学规则', size=11, color=GRAY)

# ML 层的兄弟分支面板（左侧）
box(41, 13.5, 28, 30, dashed=True)
text(43.5, 40.5, '深度学习的兄弟分支', size=10, color=GRAY)
text(43.5, 35.5, '传统监督学习', size=11.5, weight='bold')
text(43.5, 31.5, '决策树 · 随机森林', size=9.5, color=GRAY)
text(43.5, 28.5, 'XGBoost · SVM · KNN', size=9.5, color=GRAY)
text(43.5, 23.5, '无监督学习', size=11.5, weight='bold')
text(43.5, 19.5, 'K-Means 聚类 · PCA 降维', size=9.5, color=GRAY)
text(43.5, 16.5, '异常检测', size=9.5, color=GRAY)

# ============ 第三层：深度学习（高亮）============
box(72, 13.5, 52, 30, lw=1.6, ec=BLUE, fc=BLUEBG)
text(75, 40.5, '深度学习', size=14, weight='bold', color=BLUE)
text(91, 40.2, '用很多层神经网络来学，逐层抽象', size=10.5, color=GRAY)

# 结构分支 chips
chips = [('CNN · 图像', 75, 33.5, 14), ('RNN/LSTM · 序列', 90.5, 33.5, 17),
         ('Transformer · 大模型', 75, 26.5, 21), ('GNN · 图结构', 97.5, 26.5, 15),
         ('DQN/PPO · 强化学习', 75, 19.5, 21),]
for label, cx, cy, w in chips:
    box(cx, cy - 1.2, w, 4.6, lw=0.9, ec='#8aa7e8', fc='white', style='round,pad=0,rounding_size=0.9')
    text(cx + w / 2, cy + 1.1, label, size=10, ha='center', va='center')

text(100.5, 22, '特征不用人设计，\n网络自己逐层学出来', size=9.5, color=GRAY)
text(124, 17, '← 你在这里（PyTorch）', size=11.5, weight='bold', color=BLUE, ha='right')

# 底部总结
text(5, 6.5, '共同套路：模型 + 损失 + 优化——无论什么分支，"训练"都是调参数让损失变小。', size=11, color=GRAY)

plt.savefig(r'D:\Lei_learning\PyTorch学习\00_理论基础\assets\ai_ml_dl_hierarchy.png',
            bbox_inches='tight', facecolor='white')
print('saved')
