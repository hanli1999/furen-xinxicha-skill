# generate.py — 小红书图文笔记生成器 v6（富人信息差版式）
# 画布 1080x1440（小红书 3:4 竖图）· 紧凑参数（page1 装 4 条不溢出）
# 用法：PYTHONIOENCODING=utf-8 python generate.py

from PIL import Image, ImageDraw, ImageFont
import os

# ============ 路径（按需修改） ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = r"C:\Windows\Fonts"  # macOS/Linux 改对应系统字体路径
OUT_1 = os.path.join(BASE_DIR, "page1.png")
OUT_2 = os.path.join(BASE_DIR, "page2.png")

# 字体（标题仿宋·正文宋体）
FONT_TITLE   = ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), 72)
FONT_HEI_REG = ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), 26)
FONT_HEI_SIG = ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), 26)
FONT_HEI_SML = ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), 20)
FONT_HEI_TBL = ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), 30)
FONT_HEI_NUM = ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), 30)
FONT_HEI_PAG = ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), 26)

# 配色
BG               = (251, 246, 228)  # #FBF6E4 米黄背景
TABLE_HEADER_BG  = (240, 232, 201)  # #F0E8C9 浅黄表头底
NEWS_CARD_BG     = (255, 255, 255)  # 新闻事实卡片白底
SIGNAL_BG        = (245, 239, 216)  # #F5EFD8 信号解读米黄底
TEXT_DARK        = (26, 26, 26)     # #1A1A1A 主文字
TEXT_SOURCE      = (170, 160, 140)  # 来源灰
ORANGE           = (240, 138, 36)   # #F08A24 序号橙 / 标题线
PAGINATION_GRAY  = (180, 170, 150)

# 画布
W, H = 1080, 1440

# 紧凑参数 v2
TITLE_STROKE    = 2
NEWS_LINE_H     = 38
SRC_LINE_H      = 24
SIG_LINE_H      = 36
CARD_PAD        = 20
ROW_GAP         = 12
SIG_RIGHT_MARGIN= 60
SIG_LEFT_MIN    = 660
SIG_PAD_X       = 22


def draw_title_with_spacing(d, text, font, y, letter_spacing=6, stroke=TITLE_STROKE):
    char_widths = [font.getbbox(ch)[2] - font.getbbox(ch)[0] for ch in text]
    total_w = sum(char_widths) + letter_spacing * (len(text) - 1)
    x = (W - total_w) / 2
    for i, ch in enumerate(text):
        d.text((x, y), ch, font=font, fill=TEXT_DARK, stroke_width=stroke, stroke_fill=TEXT_DARK)
        x += char_widths[i] + letter_spacing


def draw_title(img, title_text, date_text):
    d = ImageDraw.Draw(img)
    y1 = 70
    draw_title_with_spacing(d, title_text, FONT_TITLE, y1, letter_spacing=6)
    y2 = y1 + 90
    draw_title_with_spacing(d, date_text, FONT_TITLE, y2, letter_spacing=6)
    line_y = y2 + 95
    d.rectangle([90, line_y, W - 90, line_y + 4], fill=ORANGE)
    return line_y + 32


def draw_table_header(img, y_start):
    d = ImageDraw.Draw(img)
    h = 80
    d.rounded_rectangle([60, y_start, W - 60, y_start + h], radius=14, fill=TABLE_HEADER_BG)
    text_y = y_start + 22
    d.text((62,  text_y), "序号",     font=FONT_HEI_TBL, fill=TEXT_DARK)
    d.text((159, text_y), "新闻事实", font=FONT_HEI_TBL, fill=TEXT_DARK)
    d.text((742, text_y), "信号解读", font=FONT_HEI_TBL, fill=TEXT_DARK)
    return y_start + h + 22


def wrap_text(text, font, max_width):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            if cur: lines.append(cur); cur = ""
            else:  lines.append("")
            continue
        test = cur + ch
        bbox = font.getbbox(test)
        if bbox[2] - bbox[0] <= max_width:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = ch
    if cur: lines.append(cur)
    return lines


def draw_signal_card(d, y0, y1, text):
    CARD_W = 300
    sig_x1 = W - SIG_RIGHT_MARGIN
    sig_x0 = max(sig_x1 - CARD_W, SIG_LEFT_MIN)
    d.rounded_rectangle([sig_x0, y0, sig_x1, y1], radius=20, fill=SIGNAL_BG)
    line = text or ""
    bbox = d.textbbox((0, 0), line, font=FONT_HEI_SIG)
    text_h = bbox[3] - bbox[1]
    text_x = sig_x0 + SIG_PAD_X
    text_y = y0 + (y1 - y0 - text_h) / 2 - bbox[1]
    d.text((text_x, text_y), line, font=FONT_HEI_SIG, fill=TEXT_DARK)


def draw_row(img, y_start, idx, news_text, source_text, signal_text):
    d = ImageDraw.Draw(img)
    news_lines = wrap_text(news_text, FONT_HEI_REG, 460)
    src_lines  = wrap_text("— " + source_text, FONT_HEI_SML, 460)
    news_h = len(news_lines) * NEWS_LINE_H + len(src_lines) * SRC_LINE_H + 12 + CARD_PAD * 2
    sig_h  = SIG_LINE_H + CARD_PAD * 2
    row_h  = max(news_h, sig_h)

    circle_r, circle_x, circle_y = 28, 90, y_start + row_h // 2
    d.ellipse([circle_x - circle_r, circle_y - circle_r, circle_x + circle_r, circle_y + circle_r], fill=ORANGE)
    num = str(idx)
    nb = d.textbbox((0, 0), num, font=FONT_HEI_NUM)
    nw, nh = nb[2] - nb[0], nb[3] - nb[1]
    d.text((circle_x - nw // 2, circle_y - nh // 2 - 6), num, font=FONT_HEI_NUM, fill=(255, 255, 255))

    news_x0, news_y0 = 135, y_start
    news_x1, news_y1 = 700, y_start + row_h
    d.rounded_rectangle([news_x0, news_y0, news_x1, news_y1], radius=20, fill=NEWS_CARD_BG)
    text_y = news_y0 + CARD_PAD
    for line in news_lines:
        d.text((news_x0 + CARD_PAD, text_y), line, font=FONT_HEI_REG, fill=TEXT_DARK)
        text_y += NEWS_LINE_H
    text_y += 12
    for line in src_lines:
        d.text((news_x0 + CARD_PAD, text_y), line, font=FONT_HEI_SML, fill=TEXT_SOURCE)
        text_y += SRC_LINE_H

    draw_signal_card(d, y_start, y_start + row_h, signal_text)
    return y_start + row_h + ROW_GAP


def draw_pagination(img, page, total=3):
    d = ImageDraw.Draw(img)
    txt = f"{page} / {total}"
    bbox = d.textbbox((0, 0), txt, font=FONT_HEI_PAG)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((W - 60 - w, H - 70), txt, font=FONT_HEI_PAG, fill=PAGINATION_GRAY)


# ============ 0804 今日 7 条 ============
# 句式：① 转折  ② 判断  ③ 直陈  ④ 场景  ⑤ 趋势  ⑥ 结论  ⑦ 预测
NEWS = [
    # ① 国际 · 美伊霍尔木兹 — 转折（美方主张→伊朗打脸）
    (1, "美方称霍尔木兹海峡可能 8 月 4 日重开,伊朗正式拒绝,重申海峡不会恢复到冲突前状态。",
     "央视新闻 2026-08-04",
     "说过要开也开不了"),
    # ② 国际 · ISM 制造业 — 判断（衰退担忧 + 降息概率）
    (2, "美国 7 月 ISM 制造业 PMI 报 48.5,连续四个月低于 50 荣枯线,CME 工具 9 月降息概率升至 65%。",
     "路透社/ISM 2026-08-04",
     "衰退预期压降息"),
    # ③ 科技 · 阿里 Qwen3.8 — 直陈
    (3, "阿里 Qwen3.8 大模型正式发布,2.4 万亿参数,编程与办公能力跻身全球第一梯队。",
     "36氪 2026-08-04",
     "国产大模型又赶一档"),
    # ④ 国际 · 美日联手干预汇市 — 场景（15 年来首次）
    (4, "美日联手干预汇市支撑日元为 15 年来首次,美方称或进一步动作,日元短线回到 162 关口。",
     "日经新闻/华尔街日报 2026-08-04",
     "汇市干预不常有"),
]

NEWS_P2 = [
    # ⑤ 欧洲 · 天然气 — 趋势（北溪管道维护 + TTF 突破 45 欧元）
    (5, "欧洲天然气因北溪管道维护消息单日涨 3%,TTF 基准首破 45 欧元/兆瓦时,工业气价同步走高。",
     "欧洲时报/ICE 2026-08-04",
     "气价就是欧洲命门"),
    # ⑥ 民生 · 公积金 60 城松动 — 结论（提取+额度+二套认定三件套）
    (6, "国内超 60 城调整公积金,提取范围扩大、贷款额度上调、二套房认定同步松绑。",
     "证券时报/住建部 2026-08-04",
     "政策松绑就在落地"),
    # ⑦ 科技 · AI 拟人化新政 — 预测（出海合规第一关）
    (7, "《人工智能拟人化互动服务管理办法》今日施行,机械陪伴类等需先过伦理安全关。",
     "网信办/财新 2026-08-04",
     "AI 出海先过合规关"),
]


def render_page(page_num, items, title_text, date_text):
    img = Image.new("RGB", (W, H), BG)
    y = draw_title(img, title_text, date_text)
    y = draw_table_header(img, y)
    for item in items:
        idx, news, source, signal = item
        y = draw_row(img, y, idx, news, source, signal)
    draw_pagination(img, page_num)
    return img


def main():
    os.makedirs(BASE_DIR, exist_ok=True)
    TITLE = "富人信息差"
    DATE  = "2026年8月4日"
    img1 = render_page(1, NEWS, TITLE, DATE)
    img1.save(OUT_1, "PNG", optimize=True); print(f"✓ page1: {OUT_1}")
    img2 = render_page(2, NEWS_P2, TITLE, DATE)
    img2.save(OUT_2, "PNG", optimize=True); print(f"✓ page2: {OUT_2}")


if __name__ == "__main__":
    main()