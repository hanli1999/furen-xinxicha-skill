# generate_page3.py — 富人认知加油包 · 剪纸笔记风（文字为主版）
#
# 设计原则：图轻字重。色块只作小筹码（≤40px），文字字号+30%，
#           份额数字作 hero（42pt），段编号 01-03 强化目录感。
#
# 画布 1080×1440 · 3 段结构：
#   顶部 4 色彩条（细）
#   标题区（无大黑底，文字即主）
#   01 产业链 5 大环节 — 文字行 + 小编号圆
#   02 关键数字怎么读 — 5 张速查卡,指标名/阈值/标准值/作用
#   03 分析方法速查 — 3 件工具箱,工具名/适用场景/使用步骤/案例
#   底部 — 红色收藏引导条
#
# v1.2.0 变更: §03 从「政策工具全家福」改为「分析方法速查」(通用方法论,规避合规风险)
#
# 用法（每日启动）：
#   1. cp generate_page3.py "D:/盛喜工效/华鑫/YYYYMMDD_富人信息差/generate_page3.py"
#   2. 改 TITLE / SUBTITLE / CHAIN / SIGNAL_CARDS / TOOL_BOX / DATA_SOURCES / FOOTER
#   3. PYTHONIOENCODING=utf-8 python generate_page3.py
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
SUBTITLE = "5 个关键指标 + 3 个分析方法·速查手册"

# 01 产业链/逻辑链 5 大环节（保留·已是干货骨架）
CHAIN = [
    ("1", "设备", "光刻 / 刻蚀 / 薄膜沉积", YELLOW),
    ("2", "材料", "硅片 / 光刻胶 / 电子气体", GREEN),
    ("3", "设计", "主控芯片 / 接口 IP",      PINK),
    ("4", "制造", "晶圆厂 / 光刻 / 良率",     RED),
    ("5", "封测", "封装 / 测试",             BLUE),
]

# 02 关键数字怎么读：5 张速查卡（指标名 + 阈值 + 业内标准 + 作用）
# 设计：每个数字 = 指标名 + 阈值 + 标准值 + 作用，下次看到新闻直接套
# 收藏价值：工具表型·跨场景复用
SIGNAL_CARDS = [
    # (指标名, 阈值, 标准值/对比, 作用, 筹码色)
    ("市场集中度",     "TOP3 > 70%",   "国际警戒线 75%", "测供应链垄断程度",         BLUE),
    ("国产化率",      "突破 10%",     "替代拐点门槛",    "测国产替代进度",           GREEN),
    ("量产良率",      "< 80%",        "盈利线 85%",      "测产能爬坡成熟度",         RED),
    ("资本开支增速",  "同比 > 30%",   "周期顶 50%",      "测行业扩产热度",           PINK),
    ("价格走势",      "连降 3 个月",   "反转信号",        "测库存出清/反弹时机",      YELLOW),
]

# 03 分析方法速查：3 件套（工具名 + 适用场景 + 使用步骤 + 经典案例）
# v1.2.0 起改用通用方法论,避开政策类合规风险
TOOL_BOX = [
    # (工具名, 适用场景, 使用步骤, 经典案例, 筹码色)
    ("波特五力",
     "判断行业赚钱难度",
     "画 5 维度打分",
     "智能手机 5 维评分",
     BLUE),
    ("生命周期",
     "判断赛道所处阶段",
     "导入→成长→成熟→衰退",
     "新能源车卡成长后期",
     RED),
    ("杜邦三因子",
     "拆解 ROE 来源",
     "净利 × 周转 × 杠杆",
     "ROE 20% 的拆解",
     YELLOW),
]

# 04 数据源（一行紧凑文字）
DATA_SOURCES = "TrendForce · DRAMeXchange · 集邦咨询 · 财联社"

# 底部 CTA
FOOTER = "★ 建议收藏  ·  数字工具表 3 年不过时"

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

    # ============ 02 关键数字怎么读（5 张速查卡） ============
    sec2_y = 700
    d.text((margin, sec2_y), "02", font=SEC_NUM, fill=RED)
    d.text((margin + 80, sec2_y + 6), "关键数字怎么读", font=SEC_NAME, fill=INK)
    d.text((margin + 80 + text_width("关键数字怎么读", SEC_NAME) + 24, sec2_y + 12),
           "指标名 · 阈值 · 标准值 · 作用", font=SEC_DESC, fill=GRAY)

    # 5 张速查卡（上 2 下 3 排布，避免横向太挤）
    cx0 = margin
    cx1 = W - margin
    cy0 = 770
    card_gap = 14
    n_cards = len(SIGNAL_CARDS)
    # 第一行 2 张，第二行 3 张
    row1_n = 2
    row2_n = n_cards - row1_n
    row1_w = (cx1 - cx0 - card_gap * (row1_n - 1)) / row1_n
    row2_w = (cx1 - cx0 - card_gap * (row2_n - 1)) / row2_n
    card_h = 140
    row_gap = 8

    for i, (indicator, threshold, std, role, color) in enumerate(SIGNAL_CARDS):
        if i < row1_n:
            x0 = cx0 + i * (row1_w + card_gap)
            x1 = x0 + row1_w
            y0 = cy0
        else:
            idx = i - row1_n
            x0 = cx0 + idx * (row2_w + card_gap)
            x1 = x0 + row2_w
            y0 = cy0 + card_h + row_gap
        y1 = y0 + card_h
        # 卡片底
        d.rectangle([x0, y0, x1, y1], fill=LIGHT)
        # 左侧色条
        d.rectangle([x0, y0, x0 + 6, y1], fill=color)
        # 指标名（黑体加粗·一行）
        d.text((x0 + 20, y0 + 14), indicator, font=ROW_NAME, fill=INK)
        # 阈值（筹码色·中等字）
        d.text((x0 + 20, y0 + 52), threshold, font=TABLE_LBL, fill=color)
        # 标准值/对比（小灰字·含对比基准）
        d.text((x0 + 20, y0 + 86), "标准值：" + std, font=ROW_BODY, fill=INK_SOFT)
        # 作用（小灰字）
        d.text((x0 + 20, y0 + 114), "作用：" + role, font=PLAYER_SUB, fill=GRAY)

    # === 撕纸分隔 3 ===
    torn_line(d, 1080, color=GRAY_LT, sw=2)

    # ============ 03 分析方法速查 ============
    sec3_y = 1106
    d.text((margin, sec3_y), "03", font=SEC_NUM, fill=RED)
    d.text((margin + 80, sec3_y + 6), "分析方法速查", font=SEC_NAME, fill=INK)
    d.text((margin + 80 + text_width("分析方法速查", SEC_NAME) + 24, sec3_y + 12),
           "工具名 · 适用场景 · 使用步骤 · 经典案例", font=SEC_DESC, fill=GRAY)

    # 3 件工具箱（3 行堆叠·左右两栏·标题左·详情右·行内宽松）
    tl_y0 = 1156
    tl_row_h = 76
    n_tl = len(TOOL_BOX)
    tl_w = W - margin * 2
    for ti, (title, goal, mechanism, case_, color) in enumerate(TOOL_BOX):
        ty = tl_y0 + ti * tl_row_h
        # 行底（极浅）
        d.rectangle([margin, ty, margin + tl_w, ty + tl_row_h - 6], fill=LIGHT)
        # 左侧色条
        d.rectangle([margin, ty, margin + 6, ty + tl_row_h - 6], fill=color)
        # 工具名（黑体·左半·单行·靠上）
        d.text((margin + 20, ty + 10), title, font=ROW_NAME, fill=INK)
        # 工具注解（小灰·副标题位·与标题间隔开）
        tool_desc = {
            "波特五力":   "Porter's Five Forces",
            "生命周期":   "Industry Life Cycle",
            "杜邦三因子": "DuPont Identity",
        }
        if title in tool_desc:
            d.text((margin + 20, ty + 46), "「" + tool_desc[title] + "」",
                   font=PLAYER_SUB, fill=GRAY)
        # 分隔细线（左/右）
        d.line([(margin + 280, ty + 8), (margin + 280, ty + tl_row_h - 14)],
               fill=GRAY_LT, width=1)
        # 适用场景 + 使用步骤 + 案例（右半·三行·每行间隔开）
        d.text((margin + 300, ty + 10), "适用：" + goal,
               font=PLAYER_SUB, fill=INK_SOFT)
        d.text((margin + 300, ty + 32), "步骤：" + mechanism,
               font=PLAYER_SUB, fill=INK_SOFT)
        d.text((margin + 300, ty + 54), "案例：" + case_,
               font=PLAYER_SUB, fill=GRAY)

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