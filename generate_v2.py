# generate_v2.py — 小红书「富人信息差」v2 ·砂糖橘护眼·3:1横排·宋体·列边界清晰
# 画布 1080x1440 · 动态铺满 · 新闻｜信号明确分割
# 用法：PYTHONIOENCODING=utf-8 python generate_v2.py

from PIL import Image, ImageDraw, ImageFont
import os

# ============ 路径（按需修改） ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = r"C:\Windows\Fonts"  # macOS/Linux 改对应系统字体路径
OUT_1 = os.path.join(BASE_DIR, "page1_v2.png")
OUT_2 = os.path.join(BASE_DIR, "page2_v2.png")

# ============ 砂糖橘护眼配色 ============
BG            = (253, 235, 208)  # #FDEBD0 砂糖橘暖杏底
TABLE_HEAD_BG = (255, 228, 194)  # #FFE4C2 表头浅橘
NEWS_BG       = (255, 255, 255)  # 新闻区白底
SIGNAL_BG     = (255, 237, 213)  # #FFEDD5 信号区略深橘底(与白底形成反差)
TEXT_DARK     = (80, 50, 30)     # 主文字暖棕
TEXT_BODY     = (90, 60, 40)     # 正文暖棕
TEXT_SRC      = (175, 145, 115)  # 来源浅棕
ORANGE        = (255, 130, 50)   # #FF8232 砂糖橘 accent
SIGNAL_TEXT   = (210, 95, 25)    # 信号字深橘
PAGE_GRAY     = (200, 175, 150)
DIVIDER       = (240, 210, 175)  # 列间分割线

W, H = 1080, 1440

# 固定区
TITLE_H = 320
HEADER_H = 64
HEADER_GAP = 28
PAGE_H = 80
ROW_GAP = 18
NUM_COL_W = 110                    # 序号列宽(含圆+间距)

# 3:1 列宽
MARGIN = 56
TOTAL_W = W - MARGIN * 2          # 968
GAP = 28                           # 列间沟
SIG_W = (TOTAL_W - GAP) // 4       # 235
NEWS_W = TOTAL_W - GAP - SIG_W     # 705
NEWS_PAD_X = 24
SIG_PAD_X = 22
ROW_RADIUS = 16
STROKE_W = 2


def get_fonts(body_pt):
    """所有字体从 body_pt 派生,宋体/仿宋系"""
    return {
        "title": ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), body_pt + 40),
        "date":  ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), body_pt + 40),
        "head":  ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), body_pt),
        "num":   ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), body_pt + 10),
        "body":  ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), body_pt),
        "src":   ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), max(16, body_pt - 6)),
        "sig":   ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), body_pt),
        "page":  ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), max(18, body_pt - 4)),
    }


def count_lines(text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            if cur: lines.append(cur); cur = ""
            else: lines.append("")
            continue
        test = cur + ch
        if font.getbbox(test)[2] - font.getbbox(test)[0] <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = ch
    if cur: lines.append(cur)
    return len(lines)


def wrap_text(text, font, max_width):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            if cur: lines.append(cur); cur = ""
            else: lines.append("")
            continue
        test = cur + ch
        if font.getbbox(test)[2] - font.getbbox(test)[0] <= max_width:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = ch
    if cur: lines.append(cur)
    return lines


def scale_fonts(items, base_body_pt):
    num = len(items)
    available = H - TITLE_H - HEADER_H - HEADER_GAP - PAGE_H - (num - 1) * ROW_GAP
    target_row_h = available / num

    body_pt = base_body_pt
    while body_pt >= 18:
        f = get_fonts(body_pt)
        body_max_w = NEWS_W - NUM_COL_W - NEWS_PAD_X
        worst_nl, worst_sl = 0, 0
        for _, news, src, _ in items:
            nl = count_lines(news, f["body"], body_max_w)
            sl = count_lines("— " + src, f["src"], body_max_w)
            if nl + sl > worst_nl + worst_sl:
                worst_nl, worst_sl = nl, sl

        body_line_h = int(body_pt * 1.45)
        src_line_h = int(max(16, body_pt - 6) * 1.35)
        sig_line_h = int(body_pt * 1.4)

        content_h = worst_nl * body_line_h + worst_sl * src_line_h + 16
        row_pad_y = int(body_pt * 0.9)
        estimated = content_h + row_pad_y * 2

        if estimated <= target_row_h:
            return f, target_row_h, row_pad_y, body_line_h, src_line_h, sig_line_h
        body_pt -= 2

    f = get_fonts(18)
    return f, target_row_h, int(18 * 0.9), int(18 * 1.45), int(16 * 1.35), int(18 * 1.4)


def draw_title(img, title_text, date_text, fonts):
    d = ImageDraw.Draw(img)
    ft = fonts["title"]
    tb = d.textbbox((0, 0), title_text, font=ft)
    tw = tb[2] - tb[0]
    d.text(((W - tw) / 2, 80), title_text, font=ft, fill=TEXT_DARK,
           stroke_width=STROKE_W, stroke_fill=TEXT_DARK)

    fd = fonts["date"]
    db = d.textbbox((0, 0), date_text, font=fd)
    dw = db[2] - db[0]
    date_y = 80 + ft.size + 28
    d.text(((W - dw) / 2, date_y), date_text, font=fd, fill=TEXT_DARK,
           stroke_width=STROKE_W, stroke_fill=TEXT_DARK)

    line_y = date_y + fd.size + 32
    d.rectangle([100, line_y, W - 100, line_y + 3], fill=ORANGE)
    return line_y + 36


def draw_table_header(img, y0, fonts):
    d = ImageDraw.Draw(img)
    h = HEADER_H
    x0, x1 = MARGIN, MARGIN + TOTAL_W
    d.rounded_rectangle([x0, y0, x1, y0 + h], radius=14, fill=TABLE_HEAD_BG)
    fh = fonts["head"]
    th = fh.size
    text_y = y0 + (h - th) // 2
    # 序号
    d.text((x0 + 16, text_y), "序号", font=fh, fill=TEXT_DARK)
    # 新闻事实
    d.text((x0 + NUM_COL_W, text_y), "新闻事实", font=fh, fill=TEXT_DARK)
    # 信号解读
    sig_hdr_x = MARGIN + NEWS_W + GAP + SIG_PAD_X
    d.text((sig_hdr_x, text_y), "信号解读", font=fh, fill=TEXT_DARK)
    return y0 + h + HEADER_GAP


def draw_row(img, y0, target_h, idx, news_text, source_text, signal_text, fonts, row_pad_y, body_lh, src_lh, sig_lh):
    d = ImageDraw.Draw(img)
    row_x0, row_x1 = MARGIN, MARGIN + TOTAL_W

    # ==== 整行白底 ====
    d.rounded_rectangle([row_x0, y0, row_x1, y0 + target_h], radius=ROW_RADIUS, fill=NEWS_BG)

    # ==== 列间分割线（垂直细线,新闻区和信号区之间） ====
    div_x = MARGIN + NEWS_W + GAP // 2
    div_y0 = y0 + 14
    div_y1 = y0 + target_h - 14
    d.line([(div_x, div_y0), (div_x, div_y1)], fill=DIVIDER, width=1)

    # ==== 序号圆（垂直居中） ====
    fb = fonts["num"]
    circle_r = int(fb.size * 0.50)
    circle_cx = row_x0 + NUM_COL_W - circle_r - 14  # 圆右留 14px 到正文
    circle_cy = y0 + target_h // 2
    d.ellipse([circle_cx - circle_r, circle_cy - circle_r,
               circle_cx + circle_r, circle_cy + circle_r], fill=ORANGE)
    nb = d.textbbox((0, 0), str(idx), font=fb)
    nw, nh = nb[2] - nb[0], nb[3] - nb[1]
    d.text((circle_cx - nw // 2, circle_cy - nh // 2 - 1),
           str(idx), font=fb, fill=(255, 255, 255))

    # ==== 新闻区（3/4 · 白底 · 垂直居中） ====
    fbody = fonts["body"]
    fsrc = fonts["src"]
    body_max_w = NEWS_W - NUM_COL_W - NEWS_PAD_X
    news_lines = wrap_text(news_text, fbody, body_max_w)
    src_lines  = wrap_text("— " + source_text, fsrc, body_max_w)
    news_x0 = row_x0 + NUM_COL_W
    news_total_h = len(news_lines) * body_lh + len(src_lines) * src_lh + 16
    news_y0 = y0 + (target_h - news_total_h) / 2
    ty = news_y0
    for line in news_lines:
        d.text((news_x0, ty), line, font=fbody, fill=TEXT_BODY)
        ty += body_lh
    ty += 16  # 正文→来源间距
    for line in src_lines:
        d.text((news_x0, ty), line, font=fsrc, fill=TEXT_SRC)
        ty += src_lh

    # ==== 信号区（1/4 · 浅橘底圆角 · 居中） ====
    fsig = fonts["sig"]
    sig_x0 = MARGIN + NEWS_W + GAP
    sig_x1 = sig_x0 + SIG_W
    # 信号区独立圆角卡片（浅橘底,与白底新闻区形成明确边界）
    d.rounded_rectangle([sig_x0, y0 + 8, sig_x1, y0 + target_h - 8],
                        radius=12, fill=SIGNAL_BG)

    sig_lines = wrap_text(signal_text, fsig, SIG_W - SIG_PAD_X * 2)
    sig_total_h = len(sig_lines) * sig_lh
    sig_start_y = y0 + (target_h - sig_total_h) / 2
    for i, line in enumerate(sig_lines):
        tb = d.textbbox((0, 0), line, font=fsig)
        lw = tb[2] - tb[0]
        lx = sig_x0 + (SIG_W - lw) / 2
        d.text((lx, sig_start_y + i * sig_lh), line, font=fsig, fill=SIGNAL_TEXT)

    return y0 + target_h + ROW_GAP


def draw_pagination(img, page, fonts):
    d = ImageDraw.Draw(img)
    fp = fonts["page"]
    txt = f"{page} / 3"
    b = d.textbbox((0, 0), txt, font=fp)
    d.text((W - 60 - b[2] + b[0], H - 40), txt, font=fp, fill=PAGE_GRAY)


# ============ 0804 今日 7 条 ============
NEWS = [
    (1, "美方称霍尔木兹海峡可能 8 月 4 日重开,伊朗正式拒绝,重申海峡不会恢复到冲突前状态。",
     "央视新闻 2026-08-04", "说过要开也开不了"),
    (2, "美国 7 月 ISM 制造业 PMI 报 48.5,连续四个月低于 50 荣枯线,CME 工具 9 月降息概率升至 65%。",
     "路透社/ISM 2026-08-04", "衰退预期压降息"),
    (3, "阿里 Qwen3.8 大模型正式发布,2.4 万亿参数,编程与办公能力跻身全球第一梯队。",
     "36氪 2026-08-04", "国产大模型又赶一档"),
    (4, "美日联手干预汇市支撑日元为 15 年来首次,美方称或进一步动作,日元短线回到 162 关口。",
     "日经新闻/华尔街日报 2026-08-04", "汇市干预不常有"),
]

NEWS_P2 = [
    (5, "欧洲天然气因北溪管道维护消息单日涨 3%,TTF 基准首破 45 欧元/兆瓦时,工业气价同步走高。",
     "欧洲时报/ICE 2026-08-04", "气价就是欧洲命门"),
    (6, "国内黄金储备连续 21 个月增持,7 月单月再增 64 万盎司,对应同期金价累计上行 38%。",
     "央行公开数据/WGC 2026-08-04", "央行囤金节奏未停"),
    (7, "国内具身智能赛道半年融资 438 亿元,其中具身大脑公司吸纳 222 亿,占比突破 50%。",
     "IT桔子/36氪 2026-08-04", "机器人风口往脑上走"),
]


def render_page(page_num, items, title_text, date_text, fonts, target_row_h, row_pad_y, body_lh, src_lh, sig_lh):
    img = Image.new("RGB", (W, H), BG)

    y = draw_title(img, title_text, date_text, fonts)
    y = draw_table_header(img, y, fonts)

    for idx, news, src, sig in items:
        y = draw_row(img, y, target_row_h, idx, news, src, sig, fonts, row_pad_y, body_lh, src_lh, sig_lh)

    draw_pagination(img, page_num, fonts)
    return img


def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    TITLE = "富人信息差"
    DATE  = "2026年8月4日"

    # 统一字号：以 page1(4条·最紧)为基准,page2 同字号
    fonts, _, row_pad_y, body_lh, src_lh, sig_lh = scale_fonts(NEWS, base_body_pt=36)

    for pg, items, out in [(1, NEWS, OUT_1), (2, NEWS_P2, OUT_2)]:
        n = len(items)
        avail = H - TITLE_H - HEADER_H - HEADER_GAP - PAGE_H - (n - 1) * ROW_GAP
        target_row_h = avail / n

        img = render_page(pg, items, TITLE, DATE, fonts, target_row_h, row_pad_y, body_lh, src_lh, sig_lh)
        img.save(out, "PNG", optimize=True)
        print(f"✓ page{pg}_v2: {out}  (宋体·行高{int(target_row_h)}px·{n}条·字号统一)")


if __name__ == "__main__":
    main()
