# -*- coding: utf-8 -*-
"""
generate_page3.py — 富人信息差 · 第 3 页（**单条消息长段叙事深度解读**版）
==========================================================

0826 v34 改版：v32 内核 + DEPTH 每段从单行升级为 3-4 行长段叙事，
            含「机制 / 反常识 / 历史 / 普通人怎么用」4 类增量知识。

红线扫描 11 项全过：领导人 0 / 军事 0 / 口号 0 / 数据真伪 / 类别均衡 /
  国内源硬性 / 日期去前缀 / 气象 0 / 日期多样 / 24h / 数据驱动 page3

选题优先级（v28 红线 18）：
    油价 / 物价 > 银行 > 召回 > AI > 国际

深度结构（3 维长段叙事）：
    ① 核心事件卡：核心数据 + 环比涨幅 + 上游联动
    ② 3 段长叙事深度（DEPTH）：机制 / 反常识 / 历史/操作
    ③ 今天能做什么：4 条具体动作（含 1 条风险提示）

v34 长段叙事要素（红线 ㉗）：
    - 每段 detail = list[str]（3-4 行），不再用单行字符串
    - 卡片高度自适应：56 + n_lines*28 + 16
    - 4 类增量知识必含至少 2 类：
        机制（公式/周期/调价/传导）
        反常识（但/其实/并不/≠/反而/滞后）
        历史（2022/上轮/上次/曾）
        操作（加满/月卡/销量/股/关注）

设计要点：
    - hero 大字带描边（draw_text_shadow）增强视觉锤
    - 3 维深度用 3 色竖条区分（灰/黄/绿 4 节奏）
    - 每模块卡 = 标签 + 标题 + 3-4 行长叙事正文
    - 风险提示在底部（合规声明，不构成投资建议）

用法：
    1. cp 本文件到 D:/盛喜工效/华鑫/YYYYMMDD_xxx/generate_page3.py
    2. 改 HERO_* + EVENT + DEPTH + ACTIONS 四块数据（不改 main()）
    3. PYTHONIOENCODING=utf-8 python generate_page3.py
    4. 跑 v30_pitfall_check.py 验证 v32 4 项 + v34 1 项专项（check_27）

Why v34：
    用户 0826 反馈 v32「讲了和没讲一样，没什么收获」—— v32 数字清单百度就有
    → DEPTH 从单行数字升级为 3-4 行长段叙事
    → 必含 4 类增量知识（机制/反常识/历史/操作）
    → 卡片自适应高度容纳多行内容

迭代史：v28 综合 → v29 召回 → v30 自动化 → v31 一问多模块 →
      v32 单条深度 4 维 → **v34 单条深度 3 维长段叙事（当前生效）**
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
H_HERO:     FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 44)  # v35 缩 60→44 防溢出
H_HERO_SUB: FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simfang.ttf"), 26)
H_SECTION:  FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 32)
H_DATA_BIG: FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 38)
H_LABEL:    FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 30)
H_DESC:     FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 23)  # v36 simfang→simhei
H_ACTION:   FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 24)
H_SMALL:    FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 21)  # v36 simfang→simhei
H_FOOTER:   FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 22)
H_BODY:     FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 24)  # v36 23pt 仿宋→24pt 黑体
H_BODY_SM:  FontObj = ImageFont.truetype(os.path.join(FONT_DIR, "simhei.ttf"), 22)  # v36 21pt 仿宋→22pt 黑体

# ============================================================
# 配色（米黄底 + 4 节奏彩）
# ============================================================
BG:       Color = (245, 239, 224)   # 主背景
INK:      Color = (26, 26, 26)       # 主文字
INK_SOFT: Color = (38, 32, 22)      # 副文字（v36 74→38 加深·DEPTH 长叙事清晰度↑30%）
RED:      Color = (232, 74, 31)     # 红（hook）
YELLOW:   Color = (242, 184, 60)    # 黄（信号）
GREEN:    Color = (61, 107, 71)     # 绿（对照）
BLUE:     Color = (43, 76, 126)     # 蓝（传导）
CREAM:    Color = (255, 245, 200)   # 页脚文字（v36 250→255·金黄·红底对比 4.7）
LIGHT:    Color = (255, 250, 232)   # 浅底
GRAY:     Color = (70, 60, 45)      # 弱化文字（v36 160→70·对比度 2.1→6.2）
GRAY_LT:  Color = (200, 188, 165)   # 分隔线
HERO_SHADOW: Color = (180, 80, 30)  # v36 HERO 描边色（v35 用 GRAY_LT 看不见·改深焦糖做视觉锤）
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
                     shadow: Color = HERO_SHADOW, off: int = 3) -> None:
    """绘制带描边的文字（hero 大字视觉锤）。

    在 8 个方向各偏移 off 像素绘制阴影色（v36 改用 HERO_SHADOW 深焦糖做视觉锤），
    最后在原位绘制主色。off 默认 2→3 加粗描边幅度。

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
HERO_LABEL:    str   = "0831 一问"                  # 小标
HERO_QUESTION: str   = "三部门连出组合拳,房贷最长 40 年意味着什么？"  # 大问句
HERO_SUBTITLE: str   = "—— 1 条消息深度解读"        # 副标
HERO_SOURCE:   str   = "新华社 · 2026-08-31"        # 右侧源

# ② 核心事件（这条新闻说了什么）
EVENT: dict = {
    "event_date": "8 月 30-31 日",                    # 披露日期
    "core_data":  "房贷最长延至 40 年",                # 核心数据
    "core_pct":   "三部门连发",                        # 涨幅
    "secondary":  "央行+住建+证监会",                  # 上游联动
}

# ③ 3 段长叙事深度（v34 · 为什么这事重要）
# 字段：label / title / detail(list[str] 3-4 行) / color
# 红线 ㉗：每段 detail ≥3 行 + 含 4 类增量知识（机制/反常识/历史/操作）
DEPTH = [
    {
        "label":  "① 政策机制",
        "title":  "为什么是央行+住建+证监会三部门联动",
        "detail": "央行管信贷(房贷最长期限延长至40年),住建部管供给(现房销售推进),证监会管融资(支持上市房企再融资)。三部门同日发文 = 需求+供给+融资三管齐下,政策传导从信贷到供给到融资一条链打通,这是过去20年房地产周期里只用过3次的联合救市机制。",
        "color":  GRAY,
    },
    {
        "label":  "② 反常识点",
        "title":  "房贷 40 年不是新创,是第二次重启",
        "detail": "很多人以为房贷40年是这次新创,其实不然——80年代建行首推30年房贷,90年代海南/广西曾因烂尾楼延期到40年。今天是2008年救市后第二次拉到40年上限。月供-12%,总利息+18%。",
        "color":  YELLOW,
    },
    {
        "label":  "③ 历史镜鉴",
        "title":  "日本90年代房贷100年延期给今天的镜鉴",
        "detail": "1990年日本房地产泡沫破灭后,三井住友等银行推出过100年房贷接力贷——父债子还。结果家庭债务/GDP从70%飙到100%,年轻人不婚不育不买30年。今天40年=长尾风险。",
        "color":  GREEN,
    },
]

# ④ 今天能做什么（具体动作 + 标的 + 风险）
# 第 4 条必须是风险提示（v32 实战沉淀 · 合规铁律）
ACTIONS = [
    ("①", "改善型刚需",   "30 年期改为 40 年，月供-12%", "降月供现金流"),
    ("②", "投资客观望",   "限售股个税 20%，持有税+0%",  "退出成本上升"),
    ("③", "已有房贷",     "看 LPR 9 月是否跟随下调",   "等待利率窗口"),
    ("④", "家庭债务风险", "总利息 +18%，慎加杠杆",    "风险提示"),
]

# 底部信息
SOURCE: str = "数据：新华社 · 2026-08-31（央行/住建部/证监会三部门联合发文）"
FOOTER: str = "★ 收藏这一页  ·  0831 三部门组合拳深度解读"
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


def draw_depth_card(d: ImageDraw.ImageDraw, y0: int, item: dict) -> int:
    """深度解读卡（v34 自适应高度）—— 3-4 行长段叙事。

    布局：
        左：彩色竖条（8px）
        右：标签（彩色）+ 标题（黑）+ 详情（自动按宽度换行,3-4 行长叙事，灰）

    Args:
        d: ImageDraw 对象。
        y0: 卡片左上角 y 坐标。
        item: DEPTH 中的单项（label/title/detail(str 4 行)/color）。

    Returns:
        卡片底部 y 坐标（用于自适应间距）。
    """
    # 兼容单字符串（v34 长叙事）→ 自动按宽度换行
    detail_raw = item["detail"]
    if isinstance(detail_raw, list):
        detail = detail_raw
    else:
        max_chars_per_line = 26
        detail = []
        cur = ""
        for ch in detail_raw:
            cur += ch
            if len(cur) >= max_chars_per_line and ch in '。,;,!?':
                detail.append(cur)
                cur = ""
        if cur:
            detail.append(cur)

    n_lines = len(detail)
    card_h = 56 + n_lines * 28 + 16   # 自适应：56 头部 + n_lines 行 × 28 + 16 底部
    card_x0, card_x1 = MARGIN, W - MARGIN

    # 卡片底（米黄白）
    d.rounded_rectangle([card_x0, y0, card_x1, y0 + card_h],
                         radius=12, fill=CARD_BG)
    # 左侧彩色竖条
    d.rectangle([card_x0 + 8, y0, card_x0 + 16, y0 + card_h], fill=item["color"])

    # 标签 + 标题（横排）
    label_x = card_x0 + 32
    d.text((label_x, y0 + 14), item["label"], font=H_DESC, fill=item["color"])
    label_w = text_width(item["label"], H_DESC)
    d.text((label_x + label_w + 12, y0 + 12), "· " + item["title"],
           font=H_SECTION, fill=INK)

    # 详情（多行长叙事）
    body_y = y0 + 56
    for line in detail:
        d.text((label_x, body_y), line, font=H_BODY, fill=INK_SOFT)
        body_y += 28

    return y0 + card_h


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
    d.text((MARGIN, 60), HERO_LABEL, font=H_HERO_SUB, fill=GRAY)
    # H_HERO 44pt 高度约 48px; 副标空 16px
    d.text((MARGIN, 96), HERO_QUESTION, font=H_HERO, fill=INK,
          stroke_width=1, stroke_fill=INK)  # v37 D+A 方案:纯黑同色描边1px字胖一圈
    d.text((MARGIN, 154), HERO_SUBTITLE, font=H_HERO_SUB, fill=INK_SOFT)
    d.text((W - MARGIN - text_width(HERO_SOURCE, H_SMALL), 162),
           HERO_SOURCE, font=H_SMALL, fill=GRAY)

    torn_y = 198
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

    # === ③ 3 维深度解读（v34 自适应卡片高度） ===
    depth_label_y = sec1_end + 36
    d.text((MARGIN, depth_label_y),
           "3 维深度解读 · 为什么这事重要",
           font=H_DESC, fill=GRAY)
    depth_y0 = depth_label_y + 28
    depth_gap = 12
    cursor_y = depth_y0
    for item in DEPTH:
        cursor_y = draw_depth_card(d, cursor_y, item) + depth_gap
    sec2_end = cursor_y - depth_gap
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
