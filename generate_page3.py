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

# 02 三厂横评：(对比项, 厂1数据, 厂2数据, 厂3数据)
# 第二个元组中的 "25" → 自动渲染成 42pt hero "25%"
# 注意：合规要求——使用匿名描述（海外老牌 NAND / 海外 HBM 强 / 国产 NAND 新军），不带具体公司名
TABLE_HEADERS = ["海外老牌 NAND", "海外 HBM 强", "国产 NAND 新军"]
TABLE_DATA = [
    ("市场地位",   "老牌霸主",   "AI 算力王",   "国产新星"),
    ("NAND 份额",  "25",         "22",          "14"),
    ("核心优势",   "全链自主",   "HBM 全球第一", "新架构突破"),
    ("致命弱点",   "HBM 落后",   "NAND 偏弱",   "先进制程受限"),
    ("代表客户",   "海外整机厂", "海外算力厂",  "国产手机/SSD"),
]

# 03 中国玩家梯队：(筹码色, 梯队名, [(匿名代号, 产业描述), ...])
# 合规要求：不出现具体公司全称，使用"龙头 A/B" + 产业定位描述
TIERS = [
    (RED, "龙头",    [("龙头 A", "国产 NAND 唯一"), ("龙头 B", "国产 DRAM 突破")]),
    (BLUE, "挑战者", [("挑战者 A", "NOR 全球第三"), ("挑战者 B", "FPGA + 存储"), ("挑战者 C", "接口芯片龙头")]),
    (GREEN, "配套",   [("配套 A", "封测代工"), ("配套 B", "测试设备"), ("配套 C", "存储 IC 设计")]),
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

    # ============ 02 三厂横评 ============
    sec2_y = 700
    d.text((margin, sec2_y), "02", font=SEC_NUM, fill=RED)
    d.text((margin + 80, sec2_y + 6), "三厂横评", font=SEC_NAME, fill=INK)
    d.text((margin + 80 + text_width("三厂横评", SEC_NAME) + 24, sec2_y + 12),
           "谁强谁弱一眼看懂", font=SEC_DESC, fill=GRAY)

    tx0, tx1 = margin, W - margin
    ty0 = 778
    col_label_w = 220
    n_cols = 3
    col_w = (tx1 - tx0 - col_label_w) / n_cols
    hd_h = 50
    row_th = 50

    # 表头（深色细带）
    d.rectangle([tx0, ty0, tx1, ty0 + hd_h], fill=INK)
    d.text((tx0 + 24, ty0 + 12), "对比项", font=TABLE_HD, fill=CREAM)
    for ci, h in enumerate(TABLE_HEADERS):
        cx = tx0 + col_label_w + ci * col_w + col_w / 2
        bb = d.textbbox((0, 0), h, font=TABLE_HD)
        bw = bb[2] - bb[0]
        bh = bb[3] - bb[1]
        d.text((cx - bw / 2, ty0 + 12 - bh // 2 + 1), h, font=TABLE_HD, fill=CREAM)

    # 数据行
    for ri, row in enumerate(TABLE_DATA):
        ry0 = ty0 + hd_h + ri * row_th
        ry1 = ry0 + row_th
        if ri % 2 == 0:
            d.rectangle([tx0, ry0, tx1, ry1], fill=LIGHT)
        d.line([(tx0, ry1), (tx1, ry1)], fill=GRAY_LT, width=1)
        d.text((tx0 + 24, ry0 + (row_th - TABLE_LBL.size) // 2),
               row[0], font=TABLE_LBL, fill=INK)
        for ci, txt in enumerate(row[1:]):
            cx0 = tx0 + col_label_w + ci * col_w
            cx1 = cx0 + col_w
            if ci > 0:
                d.line([(cx0, ry0 + 8), (cx0, ry1 - 8)], fill=GRAY_LT, width=1)
            # 份额行（第二个元组）作 hero
            if ri == 1:
                big = txt + "%"
                bb = d.textbbox((0, 0), big, font=TABLE_HERO)
                bw = bb[2] - bb[0]
                bh = bb[3] - bb[1]
                d.text((cx0 + (col_w - bw) / 2, ry0 + (row_th - bh) / 2 - 4),
                       big, font=TABLE_HERO, fill=INK)
            else:
                bb = d.textbbox((0, 0), txt, font=TABLE_TXT)
                bw = bb[2] - bb[0]
                bh = bb[3] - bb[1]
                d.text((cx0 + (col_w - bw) / 2, ry0 + (row_th - bh) / 2 - 4),
                       txt, font=TABLE_TXT, fill=INK)

    # === 撕纸分隔 3 ===
    torn_line(d, 1060, color=GRAY_LT, sw=2)

    # ============ 03 中国玩家三大梯队 ============
    sec3_y = 1088
    d.text((margin, sec3_y), "03", font=SEC_NUM, fill=RED)
    d.text((margin + 80, sec3_y + 6), "中国玩家梯队", font=SEC_NAME, fill=INK)
    d.text((margin + 80 + text_width("中国玩家梯队", SEC_NAME) + 24, sec3_y + 12),
           "国产替代谁在扛旗", font=SEC_DESC, fill=GRAY)

    tier_y0 = 1158
    tier_gap = 8
    tier_h = 56
    for ti, (color, tname, players) in enumerate(TIERS):
        ty = tier_y0 + ti * (tier_h + tier_gap)
        # 左侧小筹码 + 梯队名
        chip(d, margin + 22, ty + tier_h // 2, 18, color, outline=INK, sw=3)
        d.text((margin + 56, ty + tier_h // 2 - TIER_NAME.size // 2 - 3),
               tname, font=TIER_NAME, fill=INK)
        # 右侧玩家名（大字）
        n_p = len(players)
        p_x0 = margin + 180
        p_w = (W - margin - p_x0) / n_p
        for pi, (pname, psub) in enumerate(players):
            px = p_x0 + pi * p_w
            d.text((px + 8, ty + 4), pname, font=PLAYER, fill=INK)
            d.text((px + 8, ty + 36), psub, font=PLAYER_SUB, fill=GRAY)

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