# generate.py — 小红书图文笔记生成器 v2.5.0（华鑫富人信息差版式）·0916 实战沉淀版
# 画布 1080x1440（小红书 3:4 竖图）· 紧凑参数 v2（page1 装 4 条不溢出）
# v2.5.0（0916 实战）：5 元组 NEWS（加 term_note 注解）+ v20.2 多行完整渲染版
# 用法：PYTHONIOENCODING=utf-8 /d/.venvs/ai-audio/Scripts/python.exe generate.py

from PIL import Image, ImageDraw, ImageFont
import os

BASE_DIR = r"D:\盛喜工效\华鑫\20260804_富人信息差"
FONT_DIR  = r"C:\Windows\Fonts"
OUT_1 = os.path.join(BASE_DIR, "page1.png")
OUT_2 = os.path.join(BASE_DIR, "page2.png")

# 字体（标题仿宋·正文宋体·信号卡黑体）
FONT_TITLE       = ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), 72)
FONT_HEI_REG     = ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), 26)
FONT_HEI_SIG     = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 26)   # v39 黑体·禁 stroke
FONT_HEI_SML     = ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), 20)
FONT_HEI_TBL     = ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), 30)
FONT_HEI_TBL_BOLD= ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 30)   # v39 表头信号解读列加粗
FONT_HEI_NUM     = ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), 30)
FONT_HEI_PAG     = ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), 26)
# v40 术语注解字体
FONT_HEI_TERM    = ImageFont.truetype(os.path.join(FONT_DIR, "simsun.ttc"), 22)
TERM_LINE_H      = 30  # 注解行距

# 配色
BG                = (251, 246, 228)  # #FBF6E4 米黄背景
TABLE_HEADER_BG   = (240, 232, 201)  # #F0E8C9 浅黄表头底
NEWS_CARD_BG      = (255, 255, 255)  # 新闻事实卡片白底
SIGNAL_BG         = (245, 239, 216)  # #F5EFD8 信号解读米黄底
TEXT_DARK         = (26, 26, 26)     # #1A1A1A 主文字
TEXT_SOURCE       = (170, 160, 140)  # 来源灰
ORANGE            = (240, 138, 36)   # #F08A24 序号橙 / 标题线
PAGINATION_GRAY   = (180, 170, 150)
# v40 注解配色
TERM_TEXT         = (170, 70, 15)    # 深橙红
TERM_STROKE       = (255, 240, 215)  # 浅杏描边
TERM_BG           = (252, 240, 218)  # 浅杏底色块
TERM_BAR          = (220, 120, 40)   # 左侧橙色色条

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
# v40 注解块参数
NOTE_BLOCK_H    = 60    # 单行最小高度；多行自动扩展（v20.2）


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
    d.text((62,  text_y), "序号",     font=FONT_HEI_TBL,      fill=TEXT_DARK)
    d.text((159, text_y), "新闻事实", font=FONT_HEI_TBL,      fill=TEXT_DARK)
    # v39 信号解读列加粗·黑体 30pt
    d.text((742, text_y), "信号解读", font=FONT_HEI_TBL_BOLD, fill=TEXT_DARK)
    return y_start + h + 22


def wrap_text(text, font, max_width):
    """按字符逐字测试换行。

    Args:
        text: 待换行文本。
        font: PIL 字体对象。
        max_width: 最大像素宽度。

    Returns:
        list[str]: 切好的多行。
    """
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            if cur: lines.append(cur); cur = ""
            else:   lines.append("")
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
    """绘制信号卡：宽度 300 固定 + 左对齐垂直居中（v10 规范）。

    Args:
        d: ImageDraw 对象。
        y0/y1: 卡片上下边界。
        text: 信号解读文本（≤10 字 · 单行）。
    """
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


def draw_row(img, y_start, idx, news_text, source_text, signal_text, note_text=""):
    """绘制单条新闻 row：序号圆 + 新闻卡（含 term_note 注解块）+ 信号卡。

    v40 注解块：浅杏底色 + 橙条 + 深橙红字（22pt simsun + 1px 浅杏描边）。
    v20.2 多行完整渲染：保留 wrap_text 切好的多行逐行绘制，不 "".join 截断。

    Args:
        img: PIL Image。
        y_start: 当前 row 起点 y。
        idx: 序号（数字）。
        news_text: 新闻事实（≤60 字）。
        source_text: 来源（"媒体名 · YYYY-MM-DD"）。
        signal_text: 信号解读（≤10 字 · 单行）。
        note_text: 术语注解（≤25 字 · "X=通俗解释" 格式，可选）。

    Returns:
        int: 下一 row 起点 y。
    """
    d = ImageDraw.Draw(img)
    news_lines = wrap_text(news_text, FONT_HEI_REG, 460)
    src_lines  = wrap_text("— " + source_text, FONT_HEI_SML, 460)
    note_lines = wrap_text(note_text, FONT_HEI_TERM, 460) if note_text else []

    # v20.2 动态 NOTE_BLOCK_H：单行 NOTE_BLOCK_H，多行按实际行数扩展
    NOTE_LINE_H_DYN = 28
    note_pad_y = 10
    dynamic_note_h = max(NOTE_BLOCK_H, len(note_lines) * NOTE_LINE_H_DYN + note_pad_y * 2) if note_lines else 0

    base_h = len(news_lines) * NEWS_LINE_H + len(src_lines) * SRC_LINE_H + CARD_PAD * 2
    note_gap = 10 if note_lines else 0
    news_h = base_h + note_gap + dynamic_note_h + (14 if note_lines else 0)
    sig_h  = SIG_LINE_H + CARD_PAD * 2
    row_h  = max(news_h, sig_h)

    # 序号圆
    circle_r, circle_x, circle_y = 28, 90, y_start + row_h // 2
    d.ellipse([circle_x - circle_r, circle_y - circle_r, circle_x + circle_r, circle_y + circle_r], fill=ORANGE)
    num = str(idx)
    nb = d.textbbox((0, 0), num, font=FONT_HEI_NUM)
    nw, nh = nb[2] - nb[0], nb[3] - nb[1]
    d.text((circle_x - nw // 2, circle_y - nh // 2 - 6), num, font=FONT_HEI_NUM, fill=(255, 255, 255))

    # 新闻卡
    news_x0, news_y0 = 135, y_start
    news_x1, news_y1 = 700, y_start + row_h
    d.rounded_rectangle([news_x0, news_y0, news_x1, news_y1], radius=20, fill=NEWS_CARD_BG)
    text_y = news_y0 + CARD_PAD
    for line in news_lines:
        d.text((news_x0 + CARD_PAD, text_y), line, font=FONT_HEI_REG, fill=TEXT_DARK)
        text_y += NEWS_LINE_H

    # v40/v20.2 注解块（浅杏底 + 橙条 + 深橙红字 · 多行完整渲染版）
    if note_lines:
        text_y += note_gap
        note_x0 = news_x0 + CARD_PAD
        note_x1 = news_x1 - CARD_PAD
        note_y0 = text_y
        note_y1 = note_y0 + dynamic_note_h
        d.rectangle([note_x0, note_y0, note_x1, note_y1], fill=TERM_BG)
        d.rectangle([note_x0, note_y0, note_x0 + 4, note_y1], fill=TERM_BAR)
        # v20.2 多行渲染：保留 wrap_text 切好的多行，逐行绘制（不再 "".join 截断）
        note_text_y = note_y0 + note_pad_y
        for line in note_lines:
            d.text((note_x0 + 14, note_text_y), line, font=FONT_HEI_TERM, fill=TERM_TEXT,
                   stroke_width=1, stroke_fill=TERM_STROKE)
            note_text_y += NOTE_LINE_H_DYN
        text_y = note_y1 + 14

    # 来源行
    for line in src_lines:
        d.text((news_x0 + CARD_PAD, text_y), line, font=FONT_HEI_SML, fill=TEXT_SOURCE)
        text_y += SRC_LINE_H

    draw_signal_card(d, y_start, y_start + row_h, signal_text)
    return y_start + row_h + ROW_GAP


def draw_pagination(img, page, total=2):
    d = ImageDraw.Draw(img)
    txt = f"{page} / {total}"
    bbox = d.textbbox((0, 0), txt, font=FONT_HEI_PAG)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((W - 60 - w, H - 70), txt, font=FONT_HEI_PAG, fill=PAGINATION_GRAY)


# ============ 0804 今日 7 条（5 元组示例 · v40 注解版） ============
# 5 元组格式: (idx, news事实, term_note注解, source来源, signal信号)
# 句式：① 转折  ② 判断  ③ 直陈  ④ 场景  ⑤ 趋势  ⑥ 结论  ⑦ 预测
NEWS = [
    # ① 国际 · 美伊霍尔木兹 — 转折（美方主张→伊朗打脸）
    (1, "美方称霍尔木兹海峡可能 8 月 4 日重开,伊朗正式拒绝,重申海峡不会恢复到冲突前状态。",
     "霍尔木兹=全球石油海运咽喉,日均通行 2000 万桶。",
     "央视新闻 2026-08-04",
     "说过要开也开不了"),
    # ② 国际 · ISM 制造业 — 判断（衰退担忧 + 降息概率）
    (2, "美国 7 月 ISM 制造业 PMI 报 48.5,连续四个月低于 50 荣枯线,CME 工具 9 月降息概率升至 65%。",
     "PMI=采购经理指数,50 是荣枯分水岭,低于 50=制造业收缩。",
     "路透社/ISM 2026-08-04",
     "衰退预期压降息"),
    # ③ 科技 · 阿里 Qwen3.8 — 直陈
    (3, "阿里 Qwen3.8 大模型正式发布,2.4 万亿参数,编程与办公能力跻身全球第一梯队。",
     "大模型=能写代码能对话的 AI,万亿参数=脑子容量单位。",
     "36氪 2026-08-04",
     "国产大模型又赶一档"),
    # ④ 国际 · 美日联手干预汇市 — 场景（15 年来首次）
    (4, "美日联手干预汇市支撑日元为 15 年来首次,美方称或进一步动作,日元短线回到 162 关口。",
     "汇市干预=央行卖美元买日元,人为压低日元贬值速度。",
     "日经新闻/华尔街日报 2026-08-04",
     "汇市干预不常有"),
]

NEWS_P2 = [
    # ⑤ 欧洲 · 天然气 — 趋势（北溪管道维护 + TTF 突破 45 欧元）
    (5, "欧洲天然气因北溪管道维护消息单日涨 3%,TTF 基准首破 45 欧元/兆瓦时,工业气价同步走高。",
     "TTF=欧洲天然气基准价,兆瓦时=工业用电计量单位。",
     "欧洲时报/ICE 2026-08-04",
     "气价就是欧洲命门"),
    # ⑥ 民生 · 公积金 60 城松动 — 结论（提取+额度+二套认定三件套）
    (6, "国内超 60 城调整公积金,提取范围扩大、贷款额度上调、二套房认定同步松绑。",
     "公积金=单位+个人共同缴存的买房低息贷款池。",
     "证券时报/住建部 2026-08-04",
     "政策松绑就在落地"),
    # ⑦ 科技 · AI 拟人化新政 — 预测（出海合规第一关）
    (7, "《人工智能拟人化互动服务管理办法》今日施行,机械陪伴类等需先过伦理安全关。",
     "拟人化 AI=像人一样跟你说话的聊天机器人,管理办法=合规红线。",
     "网信办/财新 2026-08-04",
     "AI 出海先过合规关"),
]


def _unpack(item):
    """兼容 4 元组/5 元组 NEWS（v40 向后兼容）。

    Args:
        item: tuple (4 元组或 5 元组)。

    Returns:
        tuple: (idx, news, source, signal, note)
    """
    if len(item) == 5:
        idx, news, note, source, signal = item
        return idx, news, source, signal, note
    else:
        idx, news, source, signal = item
        return idx, news, source, signal, ""


def render_page(page_num, items, title_text, date_text):
    img = Image.new("RGB", (W, H), BG)
    y = draw_title(img, title_text, date_text)
    y = draw_table_header(img, y)
    for item in items:
        idx, news, source, signal, note = _unpack(item)
        y = draw_row(img, y, idx, news, source, signal, note)
    draw_pagination(img, page_num)
    return img


# ============================================================
# v34+ · 手绘贴纸合成（doodle-anim 抓的 PNG 贴到图文上）
# ============================================================
def paste_sticker(base_img, sticker_path, position="bottom_right",
                  size=(180, 180), margin=40):
    """把 doodle-anim 抓的贴纸合成到图文的空白角落。

    Args:
        base_img: PIL.Image 对象（page1/page2/page3 的 Image 对象）
        sticker_path: 贴纸 PNG 绝对路径
        position: top_left / top_right / bottom_left / bottom_right
        size: 缩放后大小（page1 角标默认 180x180；page3 装饰 220x80 横长条）
        margin: 距边缘像素

    Returns:
        合成后的 PIL.Image

    原理：doodle-anim 的 Canvas 背景是米色 (#efe9d8 等)，PIL 把这些近白
    米色像素的 alpha 设为 0 → 透明 → 用 paste() 带 mask 参数合成到 base 上
    """
    sticker = Image.open(sticker_path).convert("RGBA")
    sticker = sticker.resize(size, Image.LANCZOS)

    # 米色背景 → 透明
    pixels = sticker.load()
    w, h = sticker.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            # doodle-anim 几个 template 背景色阈值
            # mannay: #e7dfd1 (231,223,209)
            # friends: #f4efe4 (244,239,228)
            # faces: #efe9d8 (239,233,216)
            # doodle: #e8e2d2 (232,226,210)
            if r > 225 and g > 215 and b > 195 and abs(r-g) < 30 and abs(g-b) < 30:
                pixels[x, y] = (r, g, b, 0)

    # 计算位置
    bw, bh = base_img.size
    sw, sh = sticker.size
    if position == "bottom_right":
        x, y = bw - sw - margin, bh - sh - margin
    elif position == "bottom_left":
        x, y = margin, bh - sh - margin
    elif position == "top_right":
        x, y = bw - sw - margin, margin
    else:  # top_left
        x, y = margin, margin

    # 边界检查：不超出画布
    x = max(0, min(x, bw - sw))
    y = max(0, min(y, bh - sh))

    base_img.paste(sticker, (x, y), sticker)
    return base_img


def render_page_with_sticker(page_num, items, title_text, date_text,
                             sticker_path=None, sticker_position="bottom_right",
                             sticker_size=(180, 180)):
    """v34+ 包装：渲染页面 + 可选贴纸（向后兼容 render_page）。"""
    img = render_page(page_num, items, title_text, date_text)
    if sticker_path and os.path.exists(sticker_path):
        try:
            img = paste_sticker(img, sticker_path, sticker_position, sticker_size)
        except Exception as e:
            print(f"⚠️ 贴纸合成失败: {e}（不影响主图）")
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
