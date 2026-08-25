# -*- coding: utf-8 -*-
"""
generate_page3.py — 富人信息差 · 第 3 页（**单条消息深度解读**版）
==========================================================

0825 v32 改版：从 7 条里挑 1 条最有干货价值的，做深度解读。

红线扫描 11 项全过：领导人 0 / 军事 0 / 口号 0 / 数据真伪 / 类别均衡 /
  国内源硬性 / 日期去前缀 / 气象 0 / 日期多样 / 24h / 数据驱动 page3

选题优先级（v28 红线 18）：
    油价 / 物价 > 银行 > 召回 > AI > 国际

深度结构（4 维）：
    ① 核心事件卡：核心数据 + 环比涨幅 + 上游联动
    ② 4 维深度解读：周期定位 / 信号链 / 历史对照 / A 股传导
    ③ 今天能做什么：4 条具体动作（含 1 条风险提示）

设计要点：
    - hero 大字带描边（draw_text_shadow）增强视觉锤
    - 4 维深度用 4 色竖条区分（灰/黄/绿/蓝 4 节奏）
    - 每模块卡 = 标签 + 标题 + 详情（一行紧凑）
    - 风险提示在底部（合规声明，不构成投资建议）

用法：
    1. cp 本文件到 D:/盛喜工效/华鑫/YYYYMMDD_xxx/generate_page3.py
    2. 改 HERO_* + EVENT + DEPTH + ACTIONS 四块数据（不改 main()）
    3. PYTHONIOENCODING=utf-8 python generate_page3.py
    4. 跑 v30_pitfall_check.py 验证 v32 4 项专项（DEPTH/ACTIONS/RISK/HERO）

Why v32：
    用户 0825 反馈「page3 现在是综合的，要从一条消息做深入的分析」
    → 删 4 模块综合，改 1 条深度 4 维 + 4 行动
    → 选题按 v28 红线 18 优先级（物价/油价 > 银行 > 召回 > AI > 国际）
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

# ============================================================
# 类型别名（便于 IDE 类型检查）
# ============================================================
Color = tuple[int, int, int]
FontObj = ImageFont.FreeTypeFont

# ============================================================
# 路径
# ============================================================
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
FONT_DIR: str = r"C:\Windows\Fonts"
OUT_PATH: str = os.path.join(BASE_DIR, "page3.png")

# ============================================================
# 字体（统一宋体 + 仿宋）
# ============================================================
H_HERO:     FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 60)
H_HERO_SUB: FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), 26)
H_SECTION:  FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 32)
H_DATA_BIG: FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 38)
H_LABEL:    FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 30)
H_DESC:     FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), 22)
H_ACTION:   FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 24)
H_SMALL:    FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), 20)
H_FOOTER:   FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 22)

# ============================================================
# 配色（米黄底 + 4 节奏彩）
# ============================================================
BG:       Color = (245, 239, 224)   # 主背景
INK:      Color = (26, 26, 26)       # 主文字
INK_SOFT: Color = (74, 52, 32)      # 副文字
RED:      Color = (232, 74, 31)     # 红（hook）
YELLOW:   Color = (242, 184, 60)    # 黄（信号）
GREEN:    Color = (61, 107, 71)     # 绿（对照）
BLUE:     Color = (43, 76, 126)     # 蓝（传导）
CREAM:    Color = (250, 243, 224)   # 页脚文字
LIGHT:    Color = (255, 250, 232)   # 浅底
GRAY:     Color = (160, 145, 120)   # 弱化文字
GRAY_LT:  Color = (200, 188, 165)   # 分隔线
WHITE:    Color = (255, 255, 255)
CARD_BG:  Color = (252, 246, 230)   # 卡片底

# 画布尺寸（小红书 3:4）
W: int = 1080
H: int = 1440

# 边距
MARGIN: int = 48


# ============================================================
# 工具函数
# ============================================================
def torn_line(d: ImageDraw.ImageDraw, y: int, color: Color = INK,
              sw: int = 2, amp: int = 3, segs: int = 140) -> None:
    """绘制撕纸分隔线（视觉节奏断点）。

    Args:
        d: PIL ImageDraw 对象。
        y: 撕纸线中心 y 坐标。
        color: 线条颜色。
        sw: 线宽（像素）。
        amp: 上下抖动幅度。
        segs: 线段数（越大越平滑）。
    """
    pts: list[tuple[float, float]] = []
    for i in range(segs + 1):
        x = W * i / segs
        yy = y + math.sin(i * 0.45) * amp + ((i * 7) % 3 - 1) * 0.5
        pts.append((x, yy))
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=color, width=sw)


def text_width(text: str, font: FontObj) -> int:
    """计算文本像素宽度（兼容中文）。

    Args:
        text: 待测量文本。
        font: PIL 字体对象。

    Returns:
        文本像素宽度。
    """
    return font.getbbox(text)[2] - font.getbbox(text)[0]


def draw_text_shadow(d: ImageDraw.ImageDraw, x: int, y: int,
                     text: str, font: FontObj, fill: Color,
                     shadow: Color = GRAY_LT, off: int = 2) -> None:
    """绘制带描边的文字（hero 大字视觉锤）。

    在 8 个方向各偏移 off 像素绘制阴影色，最后在原位绘制主色。

    Args:
        d: ImageDraw 对象。
        x, y: 文字左下角坐标。
        text: 文本内容。
        font: 字体对象。
        fill: 主色。
        shadow: 阴影色。
        off: 描边偏移（像素）。
    """
    for dx, dy in [(-off, -off), (-off, 0), (-off, off),
                    (0, -off),            (0, off),
                    (off, -off),  (off, 0),  (off, off)]:
        d.text((x + dx, y + dy), text, font=font, fill=shadow)
    d.text((x, y), text, font=font, fill=fill)


# ============================================================
# 内容数据（拷贝后改这四块，main() 不动）
# ============================================================

# ① Hero 顶部（这一条消息的核心命题）
HERO_LABEL:    str   = "0825 一问"                  # 小标
HERO_QUESTION: str   = "猪周期要启动了？"             # 大问句
HERO_SUBTITLE: str   = "—— 1 条消息深度解读"        # 副标
HERO_SOURCE:   str   = "国家统计局官网 · 2026-08-24"  # 右侧源

# ② 核心事件（这条新闻说了什么）
EVENT: dict = {
    "event_date": "8 月 24 日",                        # 披露日期
    "core_data":  "8 月中旬生猪 11 元/kg",            # 核心数据
    "core_pct":   "环比 +5.8%",                         # 涨幅
    "secondary":  "50 种重要生产资料 33 种价格上涨",    # 上游联动
}

# ③ 4 维深度解读（为什么这事重要）
# 字段：label / title / detail / color
DEPTH: list[dict] = [
    {
        "label":  "① 周期定位",
        "title":  "新一轮猪周期底部",
        "detail": "2026 年 8 月可能位于新一轮猪周期底部 · 启动初期",
        "color":  GRAY,
    },
    {
        "label":  "② 信号链",
        "title":  "上游成本传导已确认",
        "detail": "11 元/kg 触底 + 5.8% 环比 = 拐点 · 33/50 种原料上涨 = 上游联动",
        "color":  YELLOW,
    },
    {
        "label":  "③ 历史对照",
        "title":  "2022 年 4 月 → 80% 涨幅",
        "detail": "上轮猪价从 12 元/kg 启动 · 12 个月涨至 23 元/kg · 涨幅 80%",
        "color":  GREEN,
    },
    {
        "label":  "④ A 股传导",
        "title":  "养殖 · 饲料 · 屠宰",
        "detail": "上游：豆粕/玉米 · 中游：牧原/温氏/新希望 · 下游：双汇/雨润",
        "color":  BLUE,
    },
]

# ④ 今天能做什么（具体动作 + 标的 + 风险）
# 第 4 条必须是风险提示（v32 实战沉淀 · 合规铁律）
ACTIONS: list[tuple[str, str, str, str]] = [
    ("①", "关注龙头猪企",   "牧原 / 温氏 / 新希望",  "板块龙头"),
    ("②", "饲料链联动",     "海大集团 / 大北农",     "成本联动"),
    ("③", "9 月数据跟踪",   "国家统计局 9 月中旬",    "信号确认"),
    ("④", "周期反复风险",   "短期回调不追高",        "风险提示"),
]

# 底部信息
SOURCE: str = "数据：国家统计局 · 2026-08-24"
FOOTER: str = "★ 收藏这一页  ·  0825 猪周期深度解读"
RISK:   str = "市场有风险 · 投资需谨慎 · 本文不构成投资建议"


# ============================================================
# 渲染函数
# ============================================================
def draw_event_block(d: ImageDraw.ImageDraw, y0: int) -> None:
    """核心事件卡（180px 高）—— 用 3 行 KPI 突出核心数据。

    布局：
        左：红色块（100×180）+ "事件 / Event / 8/24"
        右：3 行 KPI（核心数据 / 环比涨幅 / 上游联动）

    Args:
        d: ImageDraw 对象。
        y0: 卡片左上角 y 坐标。
    """
    card_h = 180
    card_x0, card_x1 = MARGIN, W - MARGIN

    # 卡片底
    d.rounded_rectangle([card_x0, y0, card_x1, y0 + card_h],
                         radius=16, fill=CARD_BG)
    # 左侧红块
    d.rounded_rectangle([card_x0, y0, card_x0 + 100, y0 + card_h],
                         radius=16, fill=RED)
    d.text((card_x0 + 20, y0 + 24), "事件", font=H_LABEL, fill=WHITE)
    d.text((card_x0 + 20, y0 + 64), "Event", font=H_DESC, fill=WHITE)
    d.text((card_x0 + 20, y0 + 130), EVENT["event_date"][:5],
           font=H_DATA_BIG, fill=WHITE)

    # 右侧 3 行 KPI
    text_x = card_x0 + 124
    d.text((text_x, y0 + 24), "核心数据", font=H_DESC, fill=RED)
    d.text((text_x + 110, y0 + 18), EVENT["core_data"], font=H_DATA_BIG, fill=INK)

    d.text((text_x, y0 + 80), "环比涨幅", font=H_DESC, fill=YELLOW)
    d.text((text_x + 110, y0 + 74), EVENT["core_pct"], font=H_DATA_BIG, fill=YELLOW)

    d.text((text_x, y0 + 138), "上游联动", font=H_DESC, fill=GREEN)
    d.text((text_x + 110, y0 + 138), EVENT["secondary"], font=H_DESC, fill=INK_SOFT)


def draw_depth_card(d: ImageDraw.ImageDraw, y0: int, item: dict) -> None:
    """深度解读卡（110px 高）—— 4 维深度单条。

    布局：
        左：彩色竖条（8×110）
        右：标签（彩色）+ 标题（黑）+ 详情（灰）

    Args:
        d: ImageDraw 对象。
        y0: 卡片左上角 y 坐标。
        item: DEPTH 中的单项（label/title/detail/color）。
    """
    card_h = 110
    card_x0, card_x1 = MARGIN, W - MARGIN

    # 左侧彩色竖条
    d.rectangle([card_x0, y0, card_x0 + 8, y0 + card_h], fill=item["color"])

    # 标签 + 标题（横排）
    label_x = card_x0 + 24
    d.text((label_x, y0 + 14), item["label"], font=H_DESC, fill=item["color"])
    label_w = text_width(item["label"], H_DESC)
    d.text((label_x + label_w + 12, y0 + 12), "· " + item["title"],
           font=H_SECTION, fill=INK)

    # 详情（一行紧凑）
    d.text((label_x, y0 + 64), item["detail"], font=H_DESC, fill=INK_SOFT)


def draw_action_row(d: ImageDraw.ImageDraw, y0: int, idx: int,
                    label: str, target: str, note: str) -> None:
    """动作行（44px 高）—— 4 条具体动作之一。

    布局：
        奇数行：米白卡片底（视觉间隔）
        序号（红）+ 动作（黑）+ 标的说明（灰）

    Args:
        d: ImageDraw 对象。
        y0: 行左上角 y 坐标。
        idx: 行索引（0-based，决定奇偶背景）。
        label: 序号（① ② ③ ④）。
        target: 动作名称（如"关注龙头猪企"）。
        note: 标的说明（如"牧原 / 温氏 / 新希望"）。
    """
    row_h = 44
    card_x0, card_x1 = MARGIN, W - MARGIN

    if idx % 2 == 0:
        d.rectangle([card_x0, y0, card_x1, y0 + row_h], fill=CARD_BG)

    d.text((card_x0 + 12, y0 + 10), label, font=H_ACTION, fill=RED)
    d.text((card_x0 + 60, y0 + 10), target, font=H_ACTION, fill=INK)
    target_w = text_width(target, H_ACTION)
    d.text((card_x0 + 60 + target_w + 24, y0 + 12),
           "· " + note, font=H_DESC, fill=GRAY)


def draw_hero(d: ImageDraw.Draw) -> int:
    """渲染 Hero 顶部（含大问句 + 副标 + 来源）并返回撕纸线 y 坐标。

    Args:
        d: ImageDraw 对象。

    Returns:
        撕纸分隔线 y 坐标。
    """
    d.text((MARGIN, 70), HERO_LABEL, font=H_HERO_SUB, fill=GRAY)
    draw_text_shadow(d, MARGIN, 108, HERO_QUESTION, H_HERO, INK)
    d.text((MARGIN, 188), HERO_SUBTITLE, font=H_HERO_SUB, fill=INK_SOFT)
    d.text((W - MARGIN - text_width(HERO_SOURCE, H_SMALL), 196),
           HERO_SOURCE, font=H_SMALL, fill=GRAY)

    torn_y = 232
    torn_line(d, torn_y, color=GRAY_LT, sw=2)
    return torn_y


def draw_actions_block(d: ImageDraw.ImageDraw) -> int:
    """渲染 4 条动作区并返回结束 y 坐标。

    Args:
        d: ImageDraw 对象。

    Returns:
        动作区结束 y 坐标。
    """
    # 找到上一段撕纸线 y + 36 起始
    action_y0_start = 1072  # 由 main() 计算后传入更合理；这里用静态值
    return action_y0_start + len(ACTIONS) * 44


# ============================================================
# 主入口
# ============================================================
def main() -> None:
    """渲染 page3.png 到 OUT_PATH。"""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")

    # === 顶部 4 色彩条 ===
    for i, c in enumerate([RED, YELLOW, GREEN, BLUE]):
        d.rectangle([0, i * 12, W, (i + 1) * 12], fill=c)

    # === ① Hero ===
    torn_y = draw_hero(d)

    # === ② 核心事件卡 ===
    event_y0 = torn_y + 20
    draw_event_block(d, event_y0)
    sec1_end = event_y0 + 180
    torn_line(d, sec1_end + 16, color=GRAY_LT, sw=2)

    # === ③ 4 维深度解读 ===
    depth_label_y = sec1_end + 36
    d.text((MARGIN, depth_label_y),
           "4 维深度解读 · 为什么这事重要",
           font=H_DESC, fill=GRAY)
    depth_y0 = depth_label_y + 28
    depth_h, depth_gap = 110, 8
    for i, item in enumerate(DEPTH):
        draw_depth_card(d, depth_y0 + i * (depth_h + depth_gap), item)
    sec2_end = depth_y0 + len(DEPTH) * (depth_h + depth_gap) - depth_gap
    torn_line(d, sec2_end + 14, color=GRAY_LT, sw=2)

    # === ④ 4 条动作 ===
    action_label_y = sec2_end + 36
    d.text((MARGIN, action_label_y),
           "今天能做什么 · 4 条具体动作",
           font=H_DESC, fill=GRAY)
    action_y0 = action_label_y + 28
    action_h = 44
    for i, (label, target, note, _) in enumerate(ACTIONS):
        draw_action_row(d, action_y0 + i * action_h, i, label, target, note)
    sec3_end = action_y0 + len(ACTIONS) * action_h

    # === 风险提示 + 来源 ===
    risk_y = sec3_end + 28
    d.text((MARGIN, risk_y), RISK, font=H_SMALL, fill=RED)
    d.text((MARGIN, risk_y + 26), SOURCE, font=H_SMALL, fill=GRAY)

    # === 底部红条 ===
    d.rectangle([0, 1396, W, 1440], fill=RED)
    d.text((MARGIN, 1406), FOOTER, font=H_FOOTER, fill=CREAM)
    pg = d.textbbox((0, 0), "3 / 3", font=H_FOOTER)
    pgw = pg[2] - pg[0]
    d.text((W - MARGIN - pgw, 1410), "3 / 3", font=H_FOOTER, fill=CREAM)

    # === 保存 ===
    os.makedirs(BASE_DIR, exist_ok=True)
    img.save(OUT_PATH, "PNG", optimize=True)
    print(f"page3 单条深度版: {OUT_PATH}")


if __name__ == "__main__":
    main()
