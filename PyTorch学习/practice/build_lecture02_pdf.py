# -*- coding: utf-8 -*-
"""把「02 神经网络如何学习」精读讲稿生成 A5 手机阅读版 PDF"""
import os
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Preformatted, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ---------- 字体 ----------
pdfmetrics.registerFont(TTFont('CJK', os.environ['DAIMON_CJK_FONT_REGULAR']))
pdfmetrics.registerFont(TTFont('CJK-Bold', os.environ['DAIMON_CJK_FONT_BOLD']))
pdfmetrics.registerFontFamily('CJK', normal='CJK', bold='CJK-Bold',
                              italic='CJK', boldItalic='CJK-Bold')

INK = HexColor('#333333')
GRAY = HexColor('#666666')
ACCENT = HexColor('#1a4a8a')

S = {
    'title': ParagraphStyle('t', fontName='CJK-Bold', fontSize=20, leading=28,
                            alignment=1, textColor=HexColor('#111111')),
    'subtitle': ParagraphStyle('st', fontName='CJK', fontSize=10.5, leading=15,
                               alignment=1, textColor=GRAY),
    'h2': ParagraphStyle('h2', fontName='CJK-Bold', fontSize=14, leading=20,
                         textColor=ACCENT, spaceBefore=14, spaceAfter=6),
    'body': ParagraphStyle('b', fontName='CJK', fontSize=11, leading=17.5,
                           textColor=INK, spaceAfter=6),
    'quote': ParagraphStyle('q', fontName='CJK', fontSize=10.5, leading=16,
                            textColor=GRAY, leftIndent=12, spaceAfter=6,
                            borderPadding=4),
    'bullet': ParagraphStyle('bl', fontName='CJK', fontSize=11, leading=17,
                             textColor=INK, leftIndent=14, spaceAfter=3,
                             bulletIndent=2),
    'code': ParagraphStyle('c', fontName='CJK', fontSize=8.5, leading=12,
                           textColor=HexColor('#222222'),
                           backColor=HexColor('#f5f5f5'), borderPadding=6,
                           spaceBefore=4, spaceAfter=8),
    'cell': ParagraphStyle('tc', fontName='CJK', fontSize=9.5, leading=13,
                           textColor=INK),
    'cellh': ParagraphStyle('th', fontName='CJK-Bold', fontSize=9.5, leading=13,
                            textColor=HexColor('#111111')),
}


def inline(text):
    """转义 + 极简 markdown 行内标记：粗体、行内代码"""
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`',
                  r'<font color="#1a4a8a">\1</font>', text)
    return text


def md_to_story(md):
    story, lines = [], md.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        # 代码块
        if line.strip().startswith('```'):
            buf, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                buf.append(lines[i]); i += 1
            i += 1
            code = '\n'.join(buf).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(KeepTogether(Preformatted(code, S['code'])))
            continue
        # 表格
        if line.strip().startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(set(c) <= set('-: ') for c in cells):  # 跳过分隔行
                    rows.append(cells)
                i += 1
            if rows:
                data = [[Paragraph(inline(c), S['cellh'] if r == 0 else S['cell'])
                         for c in row] for r, row in enumerate(rows)]
                ncol = len(rows[0])
                width = 11.8 * cm
                t = Table(data, colWidths=[width / ncol] * ncol)
                t.setStyle(TableStyle([
                    ('LINEABOVE', (0, 0), (-1, 0), 1.2, HexColor('#000000')),
                    ('LINEBELOW', (0, 0), (-1, 0), 0.6, HexColor('#000000')),
                    ('LINEBELOW', (0, -1), (-1, -1), 1.2, HexColor('#000000')),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(Spacer(1, 4))
                story.append(t)
                story.append(Spacer(1, 8))
            continue
        s = line.strip()
        if not s or s == '---':
            i += 1
            continue
        if s.startswith('## '):
            story.append(Paragraph(inline(s[3:]), S['h2']))
        elif s.startswith('> '):
            story.append(Paragraph(inline(s[2:]), S['quote']))
        elif s.startswith('- '):
            story.append(Paragraph('· ' + inline(s[2:]), S['bullet']))
        elif len(s) > 2 and s[0].isdigit() and '. ' in s[:4]:
            story.append(Paragraph(inline(s), S['bullet']))
        else:
            story.append(Paragraph(inline(s), S['body']))
        i += 1
    return story


import sys

# 用法: python build_lecture02_pdf.py <输入md> <输出pdf> <标题> <副标题>
# 无参数时默认构建 02 章讲稿（兼容旧用法）
if len(sys.argv) == 5:
    md_path, out_path, title, subtitle = sys.argv[1:5]
    MD = open(md_path, encoding='utf-8').read()
else:
    MD = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'lecture02.txt'), encoding='utf-8').read()
    # 去掉讲稿开头两句口语和结尾的提问句
    MD = MD.split('## 一、', 1)[1]
    MD = '## 一、' + MD
    MD = MD.rsplit('**要不要我出', 1)[0].rstrip().rstrip('---').rstrip()
    out_path = r'D:\Lei_learning\PyTorch学习\00_理论基础\02_神经网络如何学习_精读.pdf'
    title = '神经网络是怎么"学会"的'
    subtitle = 'PyTorch 理论精读 · 00-2 章配套讲稿'

doc = SimpleDocTemplate(
    out_path,
    pagesize=A5, topMargin=1.6 * cm, bottomMargin=1.6 * cm,
    leftMargin=1.5 * cm, rightMargin=1.5 * cm,
    title=title,
    author='Lei')

story = [
    Spacer(1, 40),
    Paragraph(title, S['title']),
    Spacer(1, 10),
    Paragraph(subtitle, S['subtitle']),
    Paragraph('整理于 2026-10-09', S['subtitle']),
    Spacer(1, 24),
]
story += md_to_story(MD)


def footer(canvas, d):
    canvas.saveState()
    w, h = A5
    canvas.setFont('CJK', 8)
    canvas.setFillColor(GRAY)
    canvas.drawCentredString(w / 2, 1.0 * cm, f'{d.page}')
    canvas.restoreState()


doc.build(story, onFirstPage=footer, onLaterPages=footer)
print('PDF built')
