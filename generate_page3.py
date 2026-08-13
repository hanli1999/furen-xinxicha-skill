# generate_page3.py — 富人认知加油包 · 剪纸笔记风（文字为主版）
#
# 设计原则：图轻字重。色块只作小筹码（≤40px），文字字号+30%，
#           份额数字作 hero（42pt），段编号 01-04 强化目录感。
#
# 画布 1080×1440 · 5 段结构：
#   顶部 4 色彩条（细）
#   标题区（无大黑底，文字即主）
#   01 产业链 5 大环节 — 文字行 + 小编号圆
#   02 三厂横评 — 5 行真对比表，份额数字 hero
#   03 中国玩家三大梯队 — 大字玩家名 + 小色点 tier 标
#   04 去哪查数据 — 文字列表
#   底部 — 红色收藏引导条
#
# 用法（每日启动）：
#   1. cp template_page3.py "D:/盛喜工效/华鑫/YYYYMMDD_富人信息差/generate_page3.py"
#   2. 改 TITLE / SUBTITLE / CHAIN / TABLE_DATA / TIERS / DATA_SOURCES / FOOTER
#   3. PYTHONIOENCODING=utf-8 /d/.venvs/ai-audio/Scripts/python.exe generate_page3.py
#   4. 验收：1080×1440 · 文字主导 · ≤250KB

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import math
import os

# ============ 路径（cp 后只需改 BASE_DIR） ============
BASE_DIR = r"D:\盛喜工效\华鑫\YYYYMMDD_富人信息差"
FONT_DIR = r"C:\Windows\Fonts"
OUT_PATH = os.path.join(BASE_DIR, "page3.png")

# ============ 字体（字号全部为文字优先版） ============
H_TITLE    = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 56)
H_SUB      = ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), 32)
SEC_NUM    = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 38)
SEC_NAME   = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 36)
SEC_DESC   = ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), 24)
ROW_NAME   = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 32)
ROW_BODY   = ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), 22)
TABLE_LBL  = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 28)
TABLE_HD   = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 30)
TABLE_TXT  = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 28)
TABLE_HERO = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 42)
TABLE_MARK = ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), 18)
TIER_NAME  = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 24)
PLAYER     = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 30)
PLAYER_SUB = ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), 20)
SEC_LIST   = ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), 22)
BOTTOM     = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 30)

# ============ 配色（克制使用，色块只作 accent） ============
BG       = (245, 239, 224)
INK      = (26, 26, 26)
INK_SOFT = (74, 52, 32)
RED      = (232, 74, 31)
YELLOW   = (242, 184, 60)
GREEN    = (61, 107, 71)
BLUE     = (43, 76, 126)
PINK     = (233, 30, 99)
CREAM    = (250, 243, 224)
LIGHT    = (255, 250, 232)
GRAY     = (160, 145, 120)
GRAY_LT  = (200, 188, 165)

W, H = 1080, 1440


def torn_line(d, y, color=INK, sw=2, amp=3, segs=140):
    """细撕纸分隔"""
    pts = []
    for i in range(segs + 1):
        x = W * i / segs
        yy = y + math.sin(i * 0.45) * amp + ((i * 7) % 3 - 1) * 0.5
        pts.append((x, yy))
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=color, width=sw)


def text_width(text, font):
    return font.getbbox(text)[2] - font.getbbox(text)[0]


def chip(d, cx, cy, r, fill, outline=INK, sw=3):
    """小圆筹码（≤40px 直径）"""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=sw)


def make_paper_bg(skeleton_path):
    """可选：AI 骨架做底纹（消除所有色块结构，只留纸感）"""
    if not skeleton_path or not os.path.exists(skeleton_path):
        return Image.new("RGB", (W, H), BG)
    sk = Image.open(skeleton_path).convert("RGB").resize((W, H), Image.LANCZOS)
    gray = sk.convert("L").filter(ImageFilter.GaussianBlur(8))
    warm = Image.new("RGB", (W, H), (240, 230, 210))
    tex = Image.blend(gray.convert("RGB"), warm, 0.88)
    tex = ImageEnhance.Brightness(tex).enhance(1.05)
    return tex


# ============ 内容区（每日只需改这里） ============

# 顶部标题
TITLE    = "富人认知加油包"
SUBTITLE = "1 张图看懂存储芯片产业链"

# 01 产业链 5 大环节：编号 + 名称 + 描述 + 筹码颜色
CHAIN = [
    ("1", "设备", "光刻 / 刻蚀 / 薄膜沉积", YELLOW),
    ("2", "材料", "硅片 / 光刻胶 / 电子气体", GREEN),
    ("3", "设计", "主控芯片 / 接口 IP",      PINK),
    ("4", "制造", "晶圆厂 / 光刻 / 良率",     RED),
    ("5", "封测", "封装 / 测试",             BLUE),
]

# 02 全球供给格局：3 张统计卡片（不点名公司，只描述行业结构）
# 合规要求：纯市场份额/集中度/应用场景拆分数据，无任何公司名
SHARE_CARDS = [
    # (大数字, 单位, 标签, 副说明, 筹码色)
    ("85", "%",  "TOP3 海外集中度 2019",  "三家海外合计份额",   BLUE),
    ("60", "%",  "TOP3 海外集中度 2025E", "国产入局后下行",     RED),
    ("14", "%",  "国产份额 2025E",        "从 0 到 14% 七年",  GREEN),
]

# 03 国产替代四阶段时间表：行业里程碑，不点名公司
# 合规要求：每阶段描述行业级事件（基金成立/量产/客户验证/规模替代），无任何公司名
TIMELINE = [
    # (时间段, 阶段名, 关键事件, 筹码色)
    ("2014-2017", "技术启动期", "国家大基金成立 · 设备引进",      YELLOW),
    ("2018-2020", "量产爬坡期", "32 层 3D NAND 量产 · 良率爬升",  GREEN),
    ("2021-2023", "客户验证期", "进入旗舰手机供应链",            PINK),
    ("2024+",     "规模替代期", "全球份额突破 10% 关口",         RED),
]

# 04 数据源（一行紧凑文字）
DATA_SOURCES = "TrendForce · DRAMeXchange · 集邦咨询 · 财联社"

# 底部 CTA
FOOTER = "★ 建议收藏  ·  产业链结构 3 年不过时"

# 可选：纸感底纹（None 或路径）
PAPER_BG = None  # 如要用 AI 骨架底纹，设为 "path/to/page3_skeleton.jpg"


def main():
    img = make_paper_bg(PAPER_BG) if PAPER_BG else Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")
    margin = 48

    # === 顶部 4 色彩条（细，4×12px） ===
    for i, c in enumerate([RED, YELLOW, GREEN, BLUE]):
        d.rectangle([0, i * 12, W, (i + 1) * 12], fill=c)

    # === 标题区（无大黑底，文字即主） ===
    title_y = 80
    d.text((margin, title_y), TITLE, font=H_TITLE, fill=INK)
    # 右侧 P3 小角标
    d.polygon([(W - margin - 60, title_y),
               (W - margin, title_y),
               (W - margin, title_y + 60)], fill=YELLOW)
    pn = d.textbbox((0, 0), "P3", font=H_TITLE)
    pnw = pn[2] - pn[0]
    pnh = pn[3] - pn[1]
    d.text((W - margin - 50 - pnw // 2, title_y + 30 - pnh // 2 - 4),
           "P3", font=H_TITLE, fill=INK)
    # 副标题
    d.text((margin, title_y + 70), SUBTITLE, font=H_SUB, fill=INK_SOFT)
    # 装饰短横线
    d.rectangle([margin, title_y + 70 + 50, margin + 80, title_y + 70 + 56], fill=RED)

    # === 撕纸分隔 1 ===
    torn_line(d, 244, color=GRAY_LT, sw=2)

    # ============ 01 产业链 5 大环节 ============
    sec1_y = 278
    d.text((margin, sec1_y), "01", font=SEC_NUM, fill=RED)
    d.text((margin + 80, sec1_y + 6), "产业链 5 大环节", font=SEC_NAME, fill=INK)
    d.text((margin + 80 + text_width("产业链 5 大环节", SEC_NAME) + 24, sec1_y + 12),
           "从沙子到 AI 算力", font=SEC_DESC, fill=GRAY)

    rows_y0 = 350
    row_h = 56
    for i, (num, name, desc, color) in enumerate(CHAIN):
        y = rows_y0 + i * row_h
        # 编号筹码
        chip(d, margin + 22, y + row_h // 2, 22, color, outline=INK, sw=3)
        nb = d.textbbox((0, 0), num, font=TABLE_MARK)
        nw, nh = nb[2] - nb[0], nb[3] - nb[1]
        d.text((margin + 22 - nw // 2, y + row_h // 2 - nh // 2 - 3),
               num, font=TABLE_MARK, fill=INK)
        # 行名（大）
        d.text((margin + 64, y + 6), name, font=ROW_NAME, fill=INK)
        # 行说明
        d.text((margin + 200, y + 14), desc, font=ROW_BODY, fill=INK_SOFT)
        if i < len(CHAIN) - 1:
            d.line([(margin + 64, y + row_h - 4),
                    (W - margin, y + row_h - 4)], fill=GRAY_LT, width=1)

    # === 撕纸分隔 2 ===
    torn_line(d, 670, color=GRAY_LT, sw=2)

    # ============ 02 全球供给格局 ============
    sec2_y = 700
    d.text((margin, sec2_y), "02", font=SEC_NUM, fill=RED)
    d.text((margin + 80, sec2_y + 6), "全球供给格局", font=SEC_NAME, fill=INK)
    d.text((margin + 80 + text_width("全球供给格局", SEC_NAME) + 24, sec2_y + 12),
           "集中度持续下行", font=SEC_DESC, fill=GRAY)

    # 3 张统计卡片
    cx0 = margin
    cx1 = W - margin
    cy0 = 778
    card_gap = 16
    n_cards = len(SHARE_CARDS)
    card_w = (cx1 - cx0 - card_gap * (n_cards - 1)) / n_cards
    card_h = 240
    for ci, (big, unit, label, sub, color) in enumerate(SHARE_CARDS):
        x0 = cx0 + ci * (card_w + card_gap)
        x1 = x0 + card_w
        # 卡片底（极浅底色）
        d.rectangle([x0, cy0, x1, cy0 + card_h], fill=LIGHT)
        # 顶部色条
        d.rectangle([x0, cy0, x1, cy0 + 8], fill=color)
        # 大数字（hero）+ 单位
        big_text = big + unit
        bb = d.textbbox((0, 0), big_text, font=TABLE_HERO)
        bw = bb[2] - bb[0]
        bh = bb[3] - bb[1]
        d.text((x0 + (card_w - bw) / 2, cy0 + 50),
               big_text, font=TABLE_HERO, fill=INK)
        # 标签（小标题）
        bb = d.textbbox((0, 0), label, font=TABLE_LBL)
        lw = bb[2] - bb[0]
        d.text((x0 + (card_w - lw) / 2, cy0 + 130),
               label, font=TABLE_LBL, fill=INK)
        # 副说明
        bb = d.textbbox((0, 0), sub, font=PLAYER_SUB)
        sw = bb[2] - bb[0]
        d.text((x0 + (card_w - sw) / 2, cy0 + 175),
               sub, font=PLAYER_SUB, fill=GRAY)

    # === 撕纸分隔 3 ===
    torn_line(d, 1050, color=GRAY_LT, sw=2)

    # ============ 03 国产替代四阶段时间表 ============
    sec3_y = 1080
    d.text((margin, sec3_y), "03", font=SEC_NUM, fill=RED)
    d.text((margin + 80, sec3_y + 6), "国产替代四阶段", font=SEC_NAME, fill=INK)
    d.text((margin + 80 + text_width("国产替代四阶段", SEC_NAME) + 24, sec3_y + 12),
           "从技术启动到规模替代", font=SEC_DESC, fill=GRAY)

    # 4 段时间轴
    tl_y0 = 1156
    tl_h = 174
    n_tl = len(TIMELINE)
    tl_card_w = (W - margin * 2 - card_gap * (n_tl - 1)) / n_tl
    for ti, (period, phase, event, color) in enumerate(TIMELINE):
        tx0 = margin + ti * (tl_card_w + card_gap)
        tx1 = tx0 + tl_card_w
        # 卡片底
        d.rectangle([tx0, tl_y0, tx1, tl_y0 + tl_h], fill=LIGHT)
        # 左侧色条
        d.rectangle([tx0, tl_y0, tx0 + 6, tl_y0 + tl_h], fill=color)
        # 阶段编号（顶部圆形）
        phase_num = str(ti + 1)
        chip(d, tx0 + 30, tl_y0 + 24, 16, color, outline=INK, sw=2)
        nb = d.textbbox((0, 0), phase_num, font=TABLE_MARK)
        nw, nh = nb[2] - nb[0], nb[3] - nb[1]
        d.text((tx0 + 30 - nw // 2, tl_y0 + 24 - nh // 2 - 2),
               phase_num, font=TABLE_MARK, fill=INK)
        # 时间段（小灰字）
        d.text((tx0 + 56, tl_y0 + 12), period, font=PLAYER_SUB, fill=GRAY)
        # 阶段名（黑体大字）
        d.text((tx0 + 14, tl_y0 + 56), phase, font=TIER_NAME, fill=INK)
        # 关键事件（描述文字）
        # 自动换行：按 char 拆
        max_w = tl_card_w - 28
        lines, cur = [], ""
        for ch in event:
            test = cur + ch
            if PLAYER_SUB.getbbox(test)[2] - PLAYER_SUB.getbbox(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = ch
        if cur:
            lines.append(cur)
        for li, line in enumerate(lines):
            d.text((tx0 + 14, tl_y0 + 96 + li * 26), line, font=PLAYER_SUB, fill=INK_SOFT)

    # === 撕纸分隔 4 ===
    torn_line(d, 1342, color=GRAY_LT, sw=2)

    # ============ 04 去哪查数据 ============
    sec4_y = 1362
    d.text((margin, sec4_y), "04", font=SEC_NUM, fill=RED)
    d.text((margin + 80, sec4_y + 4), "数据源", font=SEC_NAME, fill=INK)
    d.text((margin + 80 + text_width("数据源", SEC_NAME) + 24, sec4_y + 8),
           DATA_SOURCES, font=SEC_DESC, fill=INK_SOFT)

    # === 底部红条 ===
    d.rectangle([0, 1396, W, 1440], fill=RED)
    d.text((margin, 1404), FOOTER, font=BOTTOM, fill=CREAM)
    pg = d.textbbox((0, 0), "3 / 3", font=PLAYER_SUB)
    pgw = pg[2] - pg[0]
    d.text((W - margin - pgw, 1408), "3 / 3", font=PLAYER_SUB, fill=CREAM)

    os.makedirs(BASE_DIR, exist_ok=True)
    img.save(OUT_PATH, "PNG", optimize=True)
    print(f"page3 text-led: {OUT_PATH}")


if __name__ == "__main__":
    main()