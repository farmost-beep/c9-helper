#!/usr/bin/env python3
"""Generate 考研高价值信息清单 PDF via reportlab."""

import re, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Font
FONT_DIR = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8"
stheit_path = None
for root, dirs, files in os.walk(FONT_DIR):
    for f in files:
        if f == "STHEITI.ttf":
            stheit_path = os.path.join(root, f)
            break
    if stheit_path: break
pdfmetrics.registerFont(TTFont("F", stheit_path))
F = "F"

def clean(t):
    t = re.sub(r'[\U0001F600-\U0001F9FF\U0001FA00-\U0001FAFF\U0000FE00-\U0000FE0F]', '', t)
    t = re.sub(r'\*\*(.*?)\*\*', r'\1', t)
    return t

def build_pdf(out, md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    doc = SimpleDocTemplate(out, pagesize=A4, topMargin=20*mm, bottomMargin=16*mm,
                            leftMargin=18*mm, rightMargin=18*mm)

    s_title = ParagraphStyle("t", fontName=F, fontSize=15, leading=22, alignment=TA_CENTER, spaceAfter=2*mm, textColor=colors.HexColor("#b91c1c"))
    s_sub = ParagraphStyle("sb", fontName=F, fontSize=8, leading=12, alignment=TA_CENTER, spaceAfter=4*mm, textColor=colors.HexColor("#666"))
    s_h1 = ParagraphStyle("h1", fontName=F, fontSize=13, leading=18, spaceBefore=4*mm, spaceAfter=1.5*mm, textColor=colors.HexColor("#b91c1c"))
    s_h2 = ParagraphStyle("h2", fontName=F, fontSize=11, leading=16, spaceBefore=3*mm, spaceAfter=1*mm, textColor=colors.HexColor("#1d4ed8"))
    s_h3 = ParagraphStyle("h3", fontName=F, fontSize=10, leading=15, spaceBefore=2*mm, spaceAfter=0.5*mm, textColor=colors.HexColor("#333"))
    s_body = ParagraphStyle("bd", fontName=F, fontSize=8.5, leading=13, spaceBefore=0.5, spaceAfter=1*mm, alignment=TA_JUSTIFY)
    s_bullet = ParagraphStyle("bl", fontName=F, fontSize=8.5, leading=13, spaceBefore=0, spaceAfter=0.3*mm, leftIndent=4*mm)
    s_th = ParagraphStyle("th", fontName=F, fontSize=7.5, leading=11, alignment=TA_CENTER, textColor=colors.white)
    s_td = ParagraphStyle("td", fontName=F, fontSize=7.5, leading=11, alignment=TA_LEFT)
    s_footer = ParagraphStyle("ft", fontName=F, fontSize=6.5, leading=10, alignment=TA_CENTER, textColor=colors.HexColor("#999"))

    elements = []

    def emit(t, style):
        t = clean(t)
        if t.strip():
            elements.append(Paragraph(t.strip(), style))

    emit("考研高价值信息清单", s_title)
    emit("聚焦上海大学应数大二 -> C9考研 | 2026-06-02 | 基于VIX框架", s_sub)
    elements.append(HRFlowable(width="100%", thickness=0.3, color=colors.HexColor("#e0e0e0")))
    elements.append(Spacer(1, 2*mm))

    # Parse markdown
    for line in lines:
        s = line.strip()
        if not s or s == '---':
            continue
        if s.startswith('# ') or s.startswith('>'):
            continue
        if s.startswith('## ') and 'VIX≥80' in s:
            emit("最高价值发现（VIX>=80）", s_h1)
        elif s.startswith('## ') and 'VIX 60' in s:
            emit("高价值信号（VIX 60-79）", s_h1)
        elif s.startswith('## ') and 'VIX 40' in s:
            emit("中等价值（VIX 40-59）", s_h1)
        elif s.startswith('## ') and '噪音' in s:
            emit("噪音（可忽略）", s_h1)
        elif s.startswith('## ') and '行动' in s:
            emit("家长行动清单", s_h1)
        elif s.startswith('## ') and '信源' in s:
            emit("附录：信源质量评估", s_h1)
        elif s.startswith('## '):
            emit(s[3:], s_h1)
        elif s.startswith('### '):
            emit(s[4:], s_h2)
        elif s.startswith('**') and '**' in s[2:]:
            emit(s.replace('**', ''), s_h3)
        elif s.startswith('- '):
            emit("  " + s[2:], s_bullet)
        elif s.startswith('| '):
            # Skip table separator lines
            if all(c in '|:- ' for c in s):
                continue
            cells = [c.strip() for c in s.strip('|').split('|')]
            cells = [clean(c) for c in cells]
            # Check if it's a header row or data row
            is_header = any(c in ['VIX', '维度', '学校', '课程', '信息', '优先级', '信源', '标签'] for c in cells)
            # Render as simple paragraphs for now (complex tables are hard)
            sep = ' | '.join(cells)
            if is_header:
                emit("[ " + sep + " ]", s_th)
            else:
                emit(sep, s_td)
        else:
            emit(s, s_body)

    elements.append(Spacer(1, 8*mm))
    elements.append(HRFlowable(width="100%", thickness=0.3, color=colors.HexColor("#cccccc")))
    emit("数据来源：复旦官网/研招网/各校招生简章/多源交叉验证 | 仅供参考", s_footer)
    emit("验证标签：🟢 V:v2 已验证 🟡 V:v2 需核实 🔵 V:v2 估算值", s_footer)

    doc.build(elements)
    return out

if __name__ == "__main__":
    dir = os.path.dirname(os.path.abspath(__file__))
    md = os.path.join(dir, "考研高价值信息清单.md")
    out = os.path.join(dir, "考研高价值信息清单.pdf")
    if os.path.exists(out):
        os.remove(out)
    build_pdf(out, md)
    print(f"PDF generated: {out} ({os.path.getsize(out):,} bytes)")
