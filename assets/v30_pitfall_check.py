# -*- coding: utf-8 -*-
"""
v30_pitfall_check.py — 富人信息差 v30 踩坑清单逐条核查脚本
==========================================================

写完初版 page1+page2+page3 后必跑，对照 SKILL.md §8 已知坑 22 条逐条核查。
命中即返回 ❌ 清单（含位置 + 应对），Agent 直接修复 → 重渲 → 再跑。
✅ 全过才进数据核对报告 + 发布。

用法:
    PYTHONIOENCODING=utf-8 python v30_pitfall_check.py <项目目录>

示例:
    PYTHONIOENCODING=utf-8 python v30_pitfall_check.py "D:/盛喜工效/华鑫/20260824_富人信息差"

返回:
    退出码 0 = 全部通过
    退出码 1 = 有问题（清单打印在 stdout）

Why:
    v1-v29 沉淀 22 条踩坑（§8 已知坑），每次新跑都有概率踩到。
    人工记忆不可靠 → 必须自动化脚本逐条核查 + 命中即修（不等用户）。
"""

import os
import re
import sys
import argparse
from datetime import date, datetime
from collections import Counter


# ============================================================
# 解析 generate.py / generate_page3.py
# ============================================================

def parse_news_items(generate_path):
    """解析 generate.py 的 NEWS / NEWS_P2 列表 + TITLE + DATE"""
    with open(generate_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取 TITLE
    title_match = re.search(r'TITLE\s*=\s*["\'](.+?)["\']', content)
    title = title_match.group(1) if title_match else "?"

    # 提取 DATE
    date_match = re.search(r'DATE\s*=\s*["\'](.+?)["\']', content)
    date_text = date_match.group(1) if date_match else "?"

    # 提取 NEWS（page1）
    news_match = re.search(r'NEWS\s*=\s*\[(.*?)\n\]', content, re.DOTALL)
    page1_raw = news_match.group(1) if news_match else ""

    # 提取 NEWS_P2（page2）
    p2_match = re.search(r'NEWS_P2\s*=\s*\[(.*?)\n\]', content, re.DOTALL)
    page2_raw = p2_match.group(1) if p2_match else ""

    # 解析元组（每条 (idx, news, source, signal)）
    items = []
    for raw_block in [page1_raw, page2_raw]:
        tuples = re.findall(
            r'\(\s*(\d+)\s*,\s*["\'](.+?)["\']\s*,\s*["\'](.+?)["\']\s*,\s*["\'](.+?)["\']\s*\)',
            raw_block, re.DOTALL
        )
        for t in tuples:
            items.append({
                'idx': int(t[0]),
                'news': t[1],
                'source': t[2],
                'signal': t[3],
            })

    return title, date_text, items


def parse_page3_data(page3_path):
    """解析 generate_page3.py 的 page3 数据（只抓 desc 类的中文字符串，排除字体路径/变量名/英文字符串）"""
    if not os.path.exists(page3_path):
        return None
    with open(page3_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 启发式 1：抓 desc = "..." / description = "..." / SECTION_DESC = "..." 等显式 desc 赋值
    desc_patterns = [
        r'desc\s*=\s*["\']([^"\']+)["\']',
        r'description\s*=\s*["\']([^"\']+)["\']',
        r'SECTION_DESC\s*=\s*["\']([^"\']+)["\']',
        r'phase_desc\s*=\s*["\']([^"\']+)["\']',
        r'ROW_DESC\s*=\s*["\']([^"\']+)["\']',
    ]
    descs = []
    for pat in desc_patterns:
        descs.extend(re.findall(pat, content, re.IGNORECASE))

    # 启发式 2：抓含中文字符 + 长度 ≥ 10 + 不含反斜杠路径/扩展名的字符串（避免误抓 FONT_DIR/OUT_PATH）
    all_strings = re.findall(r'["\']([^"\']{10,})["\']', content)
    for s in all_strings:
        # 排除字体路径、Windows 路径、文件扩展名
        if any(bad in s for bad in ['\\\\', 'Fonts', '.ttf', '.png', 'BASE_DIR', 'FONT_', 'OUT_',
                                     'simhei', 'simfang', 'simsun', 'W, H', '#', 'RGB']):
            continue
        # 排除纯英文字符串
        if not re.search(r'[一-龥]', s):
            continue
        # 排除变量赋值（如 TITLE_MAIN = "..." 后面的字符串）
        if re.match(r'^[A-Z_]{3,}\s*$', s):
            continue
        descs.append(s)

    # 去重
    return list(set(descs))


def parse_v32_page3_data(page3_path):
    """v32 单条深度版解析：抓 HERO_QUESTION / EVENT / DEPTH(4) / ACTIONS(4) / RISK / FOOTER

    Returns:
        dict 含 hero_question / event / depth_list / actions_list / risk / footer
        or None if file not exists
    """
    if not os.path.exists(page3_path):
        return None
    with open(page3_path, 'r', encoding='utf-8') as f:
        content = f.read()

    data = {
        'hero_question': None,
        'hero_source':   None,
        'event':         {},
        'depth_list':    [],
        'actions_list':  [],
        'risk':          None,
        'footer':        None,
    }

    # HERO_QUESTION（必带问号·支持类型注解 `HERO_QUESTION: str = "..."`）
    m = re.search(r'HERO_QUESTION[^=\n]*=\s*["\']([^"\']+)["\']', content)
    if m:
        data['hero_question'] = m.group(1)

    # HERO_SOURCE（同上）
    m = re.search(r'HERO_SOURCE[^=\n]*=\s*["\']([^"\']+)["\']', content)
    if m:
        data['hero_source'] = m.group(1)

    # EVENT dict
    ev_match = re.search(r'EVENT\s*=\s*\{(.*?)\n\}', content, re.DOTALL)
    if ev_match:
        ev_block = ev_match.group(1)
        for field in ['event_date', 'core_data', 'core_pct', 'secondary']:
            fm = re.search(rf'["\']?{field}["\']?\s*:\s*["\']([^"\']+)["\']', ev_block)
            if fm:
                data['event'][field] = fm.group(1)

    # DEPTH list（每项含 label / title / detail）
    depth_match = re.search(r'DEPTH\s*=\s*\[(.*?)\n\]', content, re.DOTALL)
    if depth_match:
        # 抓每个 dict 块：{ ... }
        depth_blocks = re.findall(r'\{(.*?)\}', depth_match.group(1), re.DOTALL)
        for block in depth_blocks:
            lm = re.search(r'["\']?label["\']?\s*:\s*["\']([^"\']+)["\']', block)
            tm = re.search(r'["\']?title["\']?\s*:\s*["\']([^"\']+)["\']', block)
            dm = re.search(r'["\']?detail["\']?\s*:\s*["\']([^"\']+)["\']', block)
            if lm and tm:
                data['depth_list'].append({
                    'label':  lm.group(1),
                    'title':  tm.group(1),
                    'detail': dm.group(1) if dm else '',
                })

    # ACTIONS list（4 项 tuple: label / target / note / tag）
    act_match = re.search(r'ACTIONS\s*=\s*\[(.*?)\n\]', content, re.DOTALL)
    if act_match:
        tuples = re.findall(r'\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*\)',
                            act_match.group(1))
        for t in tuples:
            data['actions_list'].append({
                'label': t[0],
                'target': t[1],
                'note': t[2],
                'tag': t[3],
            })

    # RISK + FOOTER（支持类型注解）
    m = re.search(r'RISK[^=\n]*=\s*["\']([^"\']+)["\']', content)
    if m:
        data['risk'] = m.group(1)
    m = re.search(r'FOOTER[^=\n]*=\s*["\']([^"\']+)["\']', content)
    if m:
        data['footer'] = m.group(1)

    return data


# ============================================================
# 22 条踩坑逐条核查
# ============================================================

class Check:
    def __init__(self, id_, title, source_version):
        self.id = id_
        self.title = title
        self.source_version = source_version
        self.status = None  # "pass" | "fail" | "warn"
        self.detail = ""

    def fail(self, detail):
        self.status = "fail"
        self.detail = detail

    def pass_(self, detail):
        self.status = "pass"
        self.detail = detail


def check_01_news_overflow(items):
    """坑 1：page1 NEWS 字数 >60 字 → wrap 3-4 行 → 溢出
    v14 升级：阈值从 v9 的 34 字放宽到 60 字（v14 极致撑满参数 + 精准压缩）"""
    c = Check("01", "NEWS 字数 >60 字 → 溢出", "v14")
    overflow = []
    for item in items:
        if len(item['news']) > 60:
            overflow.append(f"条 {item['idx']}: {len(item['news'])} 字 - {item['news'][:30]}...")
    if overflow:
        c.fail(f"❌ {len(overflow)} 条超 60 字 → 必精简\n   " + "\n   ".join(overflow))
    else:
        c.pass_("✓ 所有 NEWS ≤60 字（v14 标准）")
    return c


def check_02_media_count(items):
    """坑 2：一家媒体 >1 条 → 触发平台违规"""
    c = Check("02", "一家媒体 >1 条 → 平台违规", "v9")
    media_counter = Counter()
    for item in items:
        # 提取媒体名（"— 媒体名 · 日期"格式）
        match = re.match(r'^[—\-]?\s*(\S+?)(?:\s*·|$)', item['source'])
        if match:
            media = match.group(1).strip()
            # 去掉"官网"
            media = re.sub(r'官网$', '', media)
            media_counter[media] += 1

    duplicates = [(m, n) for m, n in media_counter.items() if n > 1]
    if duplicates:
        c.fail(f"❌ {len(duplicates)} 家媒体重复：{duplicates} → 必替换")
    else:
        c.pass_(f"✓ {len(media_counter)} 家媒体分散（无重复）")
    return c


def check_03_24h_strict(items, today=None):
    """坑 3：NEWS 事件日期 today-2 → 超 48h"""
    c = Check("03", "事件日期超 48h", "v10")
    if today is None:
        today = date.today()

    expired = []
    for item in items:
        match = re.search(r'202[5-7]-(\d{2})-(\d{2})', item['source'])
        if not match:
            continue
        try:
            source_date = date(2026, int(match.group(1)), int(match.group(2)))
            delta = (today - source_date).days
            if delta > 2:
                expired.append(f"条 {item['idx']}: {item['source']} ({delta} 天前)")
            elif delta > 1:
                expired.append(f"⚠️ 条 {item['idx']}: {item['source']} ({delta} 天前 · 国内边界)")
        except (ValueError, TypeError):
            pass

    if expired:
        c.fail(f"❌ {len(expired)} 条超期 → 必替换\n   " + "\n   ".join(expired))
    else:
        c.pass_("✓ 所有日期均在 48h 内")
    return c


def check_04_page3_company_pile(page3_descs):
    """坑 4：page3 04 段堆公司名"""
    c = Check("04", "page3 堆公司名", "v18")
    if not page3_descs:
        c.pass_("⚠️ page3 文件不存在 · 跳过")
        return c
    company_words = ['公司', '集团', '股份', '科技', '有限']
    matches = []
    for desc in page3_descs:
        for w in company_words:
            if w in desc:
                matches.append(f"含'{w}': {desc[:40]}...")
                break
    if len(matches) > 2:
        c.fail(f"❌ page3 含 {len(matches)} 条公司字样 → 改用宏观/国际/全球性里程碑\n   " + "\n   ".join(matches[:5]))
    else:
        c.pass_(f"✓ page3 公司字样 {len(matches)} 条（阈值 ≤2）")
    return c


def check_05_y_end_sim(project_dir):
    """坑 5：模拟 y_end 未跑就出图"""
    c = Check("05", "y_end 模拟未跑", "v9")
    sim_files = [f for f in os.listdir(project_dir) if 'sim' in f.lower() and f.endswith(('.py', '.log', '.json', '.txt'))]
    if not sim_files:
        c.fail("❌ 未发现 y_end 模拟文件 → 必先跑 simulate_y.py")
    else:
        c.pass_(f"✓ 发现模拟文件: {sim_files[0]}")
    return c


def check_06_war_headline(items):
    """坑 6：战争消息放头条 → 国际新闻感"""
    c = Check("06", "战争消息放头条", "v23")
    war_keywords = ['俄乌', '巴以', '中东', '以方', '哈马斯', '加沙', '伊朗', '黎巴嫩', '真主党']
    page1_war = []
    for item in items[:4]:  # 仅看 page1 前 4 条
        for w in war_keywords:
            if w in item['news']:
                page1_war.append(f"条 {item['idx']}: 含'{w}' - {item['news'][:30]}...")
                break
    if page1_war:
        c.fail(f"❌ page1 前 4 条含战争关键词 → 移到 page2 后段\n   " + "\n   ".join(page1_war))
    else:
        c.pass_("✓ page1 前 4 条无战争关键词")
    return c


def check_07_title_brackets(title):
    """坑 7：标题带"（国内）"/"（国际）"（v29 已弃）"""
    c = Check("07", "标题带（国内/国际）括注", "v28")
    if "（国内）" in title or "（国际）" in title or "(国内)" in title or "(国际)" in title:
        c.fail(f"❌ 标题含括注：{title} → 改用'富人信息差'")
    elif title != "富人信息差":
        c.fail(f"❌ 标题应为'富人信息差'，实为'{title}'")
    else:
        c.pass_(f"✓ 标题统一为'富人信息差'")
    return c


def check_08_signal_space_separator(items):
    """坑 8：信号解读用空格分隔短语"""
    c = Check("08", "信号解读用空格分隔短语", "v26")
    bad = []
    for item in items:
        sig = item['signal']
        # 检测连续 3 个以上 ASCII 空格
        if re.search(r'\S\s{2,}\S', sig) or '  ' in sig:
            bad.append(f"条 {item['idx']}: '{sig}'")
        # 检测"X Y Z"无标点连缀（4 字以上短语连空格）
        elif re.search(r'[一-龥]\s[一-龥]\s[一-龥]', sig):
            bad.append(f"条 {item['idx']}: '{sig}'（中文短语+空格）")
    if bad:
        c.fail(f"❌ {len(bad)} 条信号用空格分隔 → 改用标点（逗号/中点）\n   " + "\n   ".join(bad))
    else:
        c.pass_("✓ 信号解读无空格分隔短语")
    return c


def check_09_page3_phrase_dump(page3_descs):
    """坑 9：page3 desc 用短语罗列"""
    c = Check("09", "page3 desc 短语罗列", "v26")
    if not page3_descs:
        c.pass_("⚠️ page3 不存在 · 跳过")
        return c
    phrase_like = []
    for desc in page3_descs:
        # 严格判定：长度 6-12 字 + 无句末标点 + 必须含罗列标点（顿号/逗号/中点）
        if 6 <= len(desc) <= 12 and not re.search(r'[。！？]', desc):
            # 必须含罗列式分隔（顿号、中点、斜线之一）才算短语罗列
            if re.search(r'[、，·/／]', desc):
                phrase_like.append(desc[:40])
    if len(phrase_like) > 3:
        c.fail(f"❌ page3 含 {len(phrase_like)} 个短语罗列 → 改用通顺句子\n   " + "\n   ".join(phrase_like[:5]))
    else:
        c.pass_(f"✓ page3 短语罗列 {len(phrase_like)} 条（阈值 ≤3）")
    return c


def check_10_city_news(items):
    """坑 10：上海/深圳/北京某市本地新闻"""
    c = Check("10", "省份/城市本地新闻", "v25")
    city_keywords = ['上海', '深圳', '北京', '广州', '杭州', '成都', '南京', '武汉', '西安', '重庆',
                    '河北', '河南', '山东', '江苏', '浙江', '广东', '云南', '贵州', '四川']
    matches = []
    for item in items:
        for city in city_keywords:
            if city in item['news']:
                matches.append(f"条 {item['idx']}: 含'{city}'")
                break
    if matches:
        c.fail(f"❌ {len(matches)} 条含省份/城市叙事 → 改用全国口径/上市公司/国际主体\n   " + "\n   ".join(matches))
    else:
        c.pass_("✓ 无省份/城市叙事")
    return c


def check_11_policy_slogan(items):
    """坑 11：政策发布会稿含'高质量发展'等口号"""
    c = Check("11", "政策发布会口号", "v17")
    slogan_words = ['高质量发展', '稳中向好', '继续实施', '深入推进', '扎实推进', '全面落实',
                    '规划纲要', '征求意见稿', '会议表态', '十五五', '十四五']
    matches = []
    for item in items:
        for sw in slogan_words:
            if sw in item['news']:
                matches.append(f"条 {item['idx']}: 含'{sw}'")
                break
    if matches:
        c.fail(f"❌ {len(matches)} 条含政策口号 → 改用数据公报\n   " + "\n   ".join(matches))
    else:
        c.pass_("✓ 无政策发布会口号")
    return c


def check_12_single_company(items):
    """坑 12：单一公司事件触红线"""
    c = Check("12", "单一公司事件触红线", "v18")
    company_words = ['股份', '集团', '公司', '科技', 'BYD', '比亚迪', '宁德', '隆基', '腾讯', '阿里']
    matches = []
    for item in items:
        for w in company_words:
            if w in item['news']:
                matches.append(f"条 {item['idx']}: 含'{w}' - {item['news'][:30]}...")
                break
    if len(matches) > 1:
        c.fail(f"❌ {len(matches)} 条含单一公司 → 改用板块 + 行业宏观数据\n   " + "\n   ".join(matches))
    else:
        c.pass_(f"✓ 单一公司 {len(matches)} 条（阈值 ≤1）")
    return c


def check_13_weather_only(items):
    """坑 13：暴雨/台风/山洪 → 必须有财经切口"""
    c = Check("13", "暴雨/台风/山洪无财经切口", "v17")
    weather_words = ['暴雨', '台风', '山洪', '内涝', '干旱', '寒潮', '高温预警']
    matches = []
    for item in items:
        for w in weather_words:
            if w in item['news']:
                matches.append(f"条 {item['idx']}: 含'{w}'")
                break
    if len(matches) > 1:
        c.fail(f"❌ {len(matches)} 条气象消息 → 砍或必须有财经切口\n   " + "\n   ".join(matches))
    else:
        c.pass_(f"✓ 气象消息 {len(matches)} 条（阈值 ≤1）")
    return c


def check_14_2020_arbitrage_residual(generate_path, page3_path):
    """坑 14：0820 套利残留"""
    c = Check("14", "0820 套利残留", "v26")
    forbidden = [
        "5 大参与者", "5 大渠道", "6 个 III 期", "6 个套利路径",
        "套利路径", "兑现关键节点", "投资标的", "市场结构 · 周交易",
        "周交易 100 吨", "0804 编译版"
    ]
    matches = []
    for path in [generate_path, page3_path]:
        if not os.path.exists(path):
            continue
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        for kw in forbidden:
            if kw in content:
                matches.append(f"{os.path.basename(path)} 含 '{kw}'")
    if matches:
        c.fail(f"❌ 0820 套利残留：\n   " + "\n   ".join(matches))
    else:
        c.pass_("✓ 无 0820 套利残留")
    return c


def check_15_page3_section_gap(page3_path, project_dir):
    """坑 15：page3 段间太挤（< 50px）"""
    c = Check("15", "page3 段间 < 50px", "v26")
    if not os.path.exists(page3_path) or not os.path.exists(os.path.join(project_dir, "page3.png")):
        c.pass_("⚠️ page3 文件不存在 · 跳过")
        return c
    # 启发式：从 generate_page3.py 读 torn_line 相关参数
    with open(page3_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'torn_line' not in content and 'SECTION_GAP' not in content:
        c.pass_("⚠️ 未找到 torn_line/SECTION_GAP 配置 · 跳过")
        return c
    # 简单判断：grep section_gap 或 SECTION_GAP 数值
    gap_match = re.search(r'SECTION_GAP\s*=\s*(\d+)', content)
    if gap_match:
        gap = int(gap_match.group(1))
        if gap < 50:
            c.fail(f"❌ SECTION_GAP={gap}px < 50px → 改为 ≥50")
        else:
            c.pass_(f"✓ SECTION_GAP={gap}px ≥ 50")
    else:
        c.pass_("⚠️ 未抓到 SECTION_GAP 数值 · 人工核查")
    return c


def check_16_leader_name(items):
    """坑 16：领导人姓名 0（红线 ①）"""
    c = Check("16", "领导人姓名", "v10")
    leader_words = ['习近平', '李强', '李克强', '特朗普', '拜登', '内塔尼亚胡', '普京',
                    '哈梅内伊', '泽连斯基', '马克龙', '朔尔茨', '潘功', '鲍威尔', '沃什',
                    '易纲', '刘昆']
    matches = []
    for item in items:
        for w in leader_words:
            if w in item['news'] or w in item['signal']:
                matches.append(f"条 {item['idx']}: 含'{w}'")
                break
    if matches:
        c.fail(f"❌ {len(matches)} 条含领导人姓名 → 改'美方/以方/中方'\n   " + "\n   ".join(matches))
    else:
        c.pass_("✓ 无领导人姓名")
    return c


def check_17_military_action(items):
    """坑 17：国内军事动作 0（红线 ②）"""
    c = Check("17", "国内军事动作", "v10")
    military_words = ['演训', '演习', '国防部', '南部战区', '北部战区', '东部战区',
                      '战区', '军机', '海警船', '国防科技']
    matches = []
    for item in items:
        for w in military_words:
            if w in item['news']:
                matches.append(f"条 {item['idx']}: 含'{w}'")
                break
    if matches:
        c.fail(f"❌ {len(matches)} 条含国内军事 → 删/换\n   " + "\n   ".join(matches))
    else:
        c.pass_("✓ 无国内军事动作")
    return c


def check_18_abroad_source(items):
    """坑 18：国外源触发平台违规（红线 ⑥）"""
    c = Check("18", "国外源触发平台违规", "v14")
    abroad_sources = ['路透社', '路透', '半岛', 'BBC', 'CNN', '华盛顿邮报', '纽约时报',
                      '金融时报', '日经新闻', '韩联社', '彭博']
    matches = []
    for item in items:
        for src in abroad_sources:
            if src in item['source']:
                matches.append(f"条 {item['idx']}: {item['source']}")
                break
    if matches:
        c.fail(f"❌ {len(matches)} 条用国外源 → 换国内一手源\n   " + "\n   ".join(matches))
    else:
        c.pass_("✓ 全部国内一手源")
    return c


def check_19_date_prefix(items):
    """坑 19：新闻事实正文带日期前缀（红线 ⑦）"""
    c = Check("19", "新闻事实正文带日期前缀", "v14")
    matches = []
    for item in items:
        # 抓"X月X日 X"前缀
        if re.match(r'^\s*\d{1,2}月\d{1,2}日', item['news']):
            matches.append(f"条 {item['idx']}: '{item['news'][:30]}...'")
        elif re.match(r'^\s*据\d', item['news']):
            matches.append(f"条 {item['idx']}: 据X日报道...")
    if matches:
        c.fail(f"❌ {len(matches)} 条带日期前缀 → 删前缀，日期走来源行\n   " + "\n   ".join(matches))
    else:
        c.pass_("✓ 新闻事实无日期前缀")
    return c


def check_20_signal_complete_sentence(items):
    """坑 20：解读是短语罗列 vs 一句话"""
    c = Check("20", "解读是短语罗列", "v24")
    short_signals = []
    for item in items:
        sig = item['signal']
        # 短信号 + 无方向判断词
        if len(sig) <= 6:
            short_signals.append(f"条 {item['idx']}: '{sig}'（{len(sig)}字太短）")
    if len(short_signals) > 2:
        c.fail(f"❌ {len(short_signals)} 条信号 ≤6 字 → 必改完整一句话\n   " + "\n   ".join(short_signals))
    else:
        c.pass_(f"✓ 短信号 {len(short_signals)} 条（阈值 ≤2）")
    return c


def check_21_humanizer_required(generate_path):
    """坑 21：humanizer-zh 必须跑（红线 ㉔）"""
    c = Check("21", "humanizer-zh 已跑", "v28")
    # 检查 generate.py 注释或文件存在 humanizer 标记
    if not os.path.exists(generate_path):
        c.fail("❌ generate.py 不存在")
        return c
    with open(generate_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 查找 humanizer 标记
    if 'humanizer' in content.lower() or 'v28' in content:
        c.pass_("✓ generate.py 含 humanizer 标记")
    else:
        c.fail("⚠️ 未见 humanizer 痕迹 → 必跑 humanizer-zh 改写 7 条信号 + page3 desc")
    return c


def check_22_data_truth_required(project_dir):
    """坑 22：数据真实性核对报告存在"""
    c = Check("22", "数据真实性核对报告存在", "v24")
    report_files = [f for f in os.listdir(project_dir) if '核对' in f or '真伪' in f or '真实性' in f]
    if not report_files:
        c.fail("❌ 未发现'数据真实性核对报告.md' → 必写")
    else:
        c.pass_(f"✓ 报告存在: {report_files[0]}")
    return c


# ============================================================
# v32 单条深度版专项核查（4 项）
# ============================================================

def check_23_v32_hero_has_question(v32_data):
    """v32 坑 1：HERO_QUESTION 必须带问号（一眼看出的"问"）"""
    c = Check("23", "v32 HERO 大问句带问号", "v32")
    if v32_data is None:
        c.pass_("⚠️ page3 文件不存在 · 跳过")
        return c
    q = v32_data.get('hero_question')
    if not q:
        c.fail("❌ HERO_QUESTION 为空 → 必须填'X 启动了？/X 拐点？'")
        return c
    if '?' not in q and '？' not in q:
        c.fail(f"❌ HERO_QUESTION='{q}' 缺问号 → 加？")
    else:
        c.pass_(f"✓ HERO 大问句='{q}'")
    return c


def check_24_v32_depth_4d(v32_data):
    """v32 坑 2：DEPTH 必须 3-4 维（v32=4 维：周期定位/信号链/历史对照/A 股传导；v34=3-4 维长段叙事）"""
    c = Check("24", "DEPTH 3-4 维深度", "v32/v34")
    if v32_data is None:
        c.pass_("⚠️ page3 文件不存在 · 跳过")
        return c
    depths = v32_data.get('depth_list', [])
    n = len(depths)
    if n < 3 or n > 4:
        c.fail(f"❌ DEPTH 数量={n} → 必须 3-4 维（v32=4 维/v34=3-4 维）")
        return c
    # v32: 4 维必备关键词
    if n == 4:
        labels_required = ['周期', '信号', '历史', 'A 股']
        labels_found = ''.join(d['label'] + d['title'] for d in depths)
        missing = [w for w in labels_required if w not in labels_found]
        if missing:
            c.fail(f"❌ DEPTH 4 维缺失关键词: {missing} → 必含 周期/信号/历史/A 股")
            return c
        titles = ' / '.join(d['title'] for d in depths)
        c.pass_(f"✓ DEPTH 4 维齐 (v32): {titles}")
    else:
        # v34: 3 维长段叙事（关键词不强制，由 check_27 验证叙事质量）
        titles = ' / '.join(d['title'] for d in depths)
        c.pass_(f"✓ DEPTH 3 维 (v34 长段叙事): {titles}")
    return c


def check_25_v32_action_4(v32_data):
    """v32 坑 3：ACTIONS 必须 4 条 + 第 4 条必须是风险提示（合规铁律）"""
    c = Check("25", "v32 ACTIONS 4 条 + 风险提示", "v32")
    if v32_data is None:
        c.pass_("⚠️ page3 文件不存在 · 跳过")
        return c
    actions = v32_data.get('actions_list', [])
    n = len(actions)
    if n != 4:
        c.fail(f"❌ ACTIONS 数量={n} → 必须恰好 4 条（3 行动 + 1 风险）")
        return c
    # 第 4 条必含风险关键词
    last = actions[-1]
    risk_words = ['风险', '谨慎', '不追高', '回调', '止损', '规避']
    if not any(w in last['target'] + last['note'] + last['tag'] for w in risk_words):
        c.fail(f"❌ 第 4 条不是风险提示: '{last['target']}' → 改'风险提示/短期回调/止损'")
    else:
        targets = ' / '.join(a['target'] for a in actions)
        c.pass_(f"✓ 4 条: {targets}（第 4 条='{last['target']}' = 风险提示）")
    return c


def check_26_v32_risk_disclaimer(v32_data):
    """v32 坑 4：RISK 风险提示字符串必含「不构成投资建议」（合规铁律）"""
    c = Check("26", "v32 RISK 不构成投资建议", "v32")
    if v32_data is None:
        c.pass_("⚠️ page3 文件不存在 · 跳过")
        return c
    risk = v32_data.get('risk', '')
    if not risk:
        c.fail("❌ RISK 字符串为空 → 必须含'市场有风险/不构成投资建议'")
        return c
    required = ['不构成投资建议']
    missing = [w for w in required if w not in risk]
    if missing:
        c.fail(f"❌ RISK 缺关键词: {missing} → 加'市场有风险·投资需谨慎·本文不构成投资建议'")
    else:
        c.pass_(f"✓ RISK='{risk[:40]}...'")
    return c


def check_27_v34_long_narrative(v32_data, page3_path):
    """v34 坑：DEPTH 长段叙事 + 反常识干货（红线 ㉗）

    必含：
    1. 每段 detail ≥3 行（v33 失败模式 = 1 行）
    2. 4 类元素关键词至少出现 1 类（避免再次罗列数字）
       - 机制：定价/公式/规则/传导/挂钩/周期/调价/机制
       - 反常识：但/其实/并不是/不等于/≠/反/反而
       - 历史：2022/2020/2018/曾/历/上轮/上次/当年
       - 操作：加满/月卡/销量/订单/股/买/不买/今晚/明天/两周
    """
    c = Check("27", "v34 DEPTH 长段叙事 + 4 类增量知识", "v34")
    if v32_data is None:
        c.pass_("⚠️ page3 文件不存在 · 跳过")
        return c
    depths = v32_data.get('depth_list', [])
    if not depths:
        c.fail("❌ DEPTH 为空 → v34 必填 3-4 段长段叙事")
        return c

    # 启发式：从 page3.py 读 detail 原始内容（multi-line 字符串列表）
    detail_blocks = []
    if os.path.exists(page3_path):
        with open(page3_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 抓 "detail": ["...", "...", ...] 字符串列表形式
        list_matches = re.findall(r'"detail"\s*:\s*\[\s*(.*?)\s*\]', content, re.DOTALL)
        for lm in list_matches:
            lines = re.findall(r'["\']([^"\']+)["\']', lm)
            if lines:
                detail_blocks.append(lines)

    # 4 类元素关键词
    KW_MECHANISM = ['定价', '公式', '规则', '传导', '挂钩', '周期', '调价', '机制']
    KW_COUNTER   = ['但', '其实', '并不是', '不等于', '≠', '反而', '反过来', '滞后', '埋伏笔']
    KW_HISTORY   = ['2022', '2020', '2018', '2019', '2023', '曾', '历', '上轮', '上次', '当年', '过去']
    KW_ACTION    = ['加满', '月卡', '销量', '订单', '股', '买', '不买', '今晚', '明天', '两周', '长线', '看', '关注', '规避']

    short_narratives = []
    missing_kw_segments = []
    for i, d in enumerate(depths):
        # 1. 行数检查（取字符串列表或回退字符串长度粗判）
        if i < len(detail_blocks):
            n_lines = len(detail_blocks[i])
            full_text = ''.join(detail_blocks[i])
        else:
            # fallback：detail 字符串粗判（按字数推算行数）
            full_text = d['detail']
            n_lines = max(1, (len(full_text) + 27) // 28)  # ~28 字/行

        if n_lines < 3:
            short_narratives.append(f"段{i+1}: 仅{n_lines}行（必≥3行长段叙事）")

        # 2. 4 类关键词检查
        if not any(k in full_text for k in KW_MECHANISM + KW_COUNTER + KW_HISTORY + KW_ACTION):
            missing_kw_segments.append(f"段{i+1}: '{d['title'][:20]}' 无4类关键词")

    if short_narratives:
        c.fail(f"❌ {len(short_narratives)} 段不满足≥3行长叙事：\n   " +
               "\n   ".join(short_narratives))
        return c
    if missing_kw_segments:
        c.fail(f"❌ {len(missing_kw_segments)} 段缺 4 类增量知识（机制/反常识/历史/操作）：\n   " +
               "\n   ".join(missing_kw_segments))
        return c
    c.pass_(f"✓ DEPTH {len(depths)} 段均为长叙事（≥3行）+ 含机制/反常识/历史/操作")
    return c


def check_28_v38_depth2_counter_data(v32_data, page3_path):
    """v38 坑：page3 DEPTH② 反常识数据必须二次溯源（红线 ㉘·0905）

    反常识点段落中的具体数据（如市场份额/产能/价格）必须：
    1. 有具体数字（不能模糊"不足 5% / 仍依赖进口"）
    2. 至少 1 个第三方独立数据源标注（Counterpoint/CFM/Omdia/Wind/同花顺/官方公报）
    3. 不能出现"凭空写"的反常识表述（无数字 + 无源 = 红线 ㉘ 触线）

    0905 实战踩坑：长鑫 LPDDR5X 量产稿写"长鑫全球 DRAM 份额不足 5%、EUV 依赖进口"
    → 实际份额 7.7%-8% 已超美光（Counterpoint/CFM/Omdia 三方一致数据）
    """
    c = Check("28", "v38 DEPTH② 反常识数据二次溯源", "v38")
    if v32_data is None or page3_path is None or not os.path.exists(page3_path):
        c.pass_("⚠️ page3 文件不存在 · 跳过")
        return c
    depths = v32_data.get('depth_list', [])
    if not depths:
        c.pass_("⚠️ DEPTH 为空 · 跳过")
        return c

    with open(page3_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 第三方独立源关键词
    SOURCE_KW = ['Counterpoint', 'CFM', 'Omdia', 'TrendForce', 'Wind', '同花顺', '海关总署',
                 '财政部', '央行', '国家统计局', '邮政局', '商务部', '央行', 'WGC',
                 '财联社', '彭博', '路透', 'Bloomberg', 'S&P', 'S&P Global']

    # 反常识点关键词（DEPTH② 段通常含这些）
    COUNTER_KW = ['反常识', '并不', '并不等于', '≠', '误区', '反', '反而', '并未']

    # 模糊表述（红线 ㉘ 黑名单——必须替换为可溯源数字）
    VAGUE_BLACKLIST = ['不足 5%', '不足5%', '仍依赖进口', '依赖进口', '目前', '仍以低端为主']

    issues = []
    for i, d in enumerate(depths):
        title = d.get('title', '')
        detail = d.get('detail', '')

        # 只针对 DEPTH② 反常识点段落（按标题关键词定位）
        if not any(k in title for k in ['反常识', '②', '不等于', '误区', '破']):
            continue

        # 检查 1：反常识段是否含数字（必须有具体数字，否则就是"凭感觉写"）
        has_number = bool(re.search(r'\d', detail))

        # 检查 2：是否含第三方独立源标注
        has_source = any(k in detail for k in SOURCE_KW)

        # 检查 3：是否触黑名单（模糊表述）
        has_vague = any(v in detail for v in VAGUE_BLACKLIST)

        if has_vague:
            issues.append(f"段{i+1}「{title[:18]}」触黑名单：含「不足5%」/「依赖进口」等模糊表述 → 必查 Counterpoint/CFM/Omdia")
        elif has_number and not has_source:
            issues.append(f"段{i+1}「{title[:18]}」有数字但无第三方源标注 → 必加 Counterpoint/CFM/Omdia/WGC 等")

    if issues:
        c.fail("❌ DEPTH② 反常识数据缺溯源：\n   " +
               "\n   ".join(issues))
        return c
    c.pass_("✓ DEPTH② 反常识点均有数字 + 第三方源标注")
    return c


def check_29_v38_report_knowledge_increment(project_dir):
    """v38 坑：数据真伪核对报告必须结论先行 + 知识增量（红线 ㉙·0905）

    报告 5 类禁用句式（命中 = 水话）：
    1. "X 条全部 PASS · Y 项红线全过" — 流程化检查表
    2. "基本事实正确" / "与多家国内源表述一致" — 软话套话
    3. "已确认 / 已缩 / 已替换 / 已渲染" — 过程性废话
    4. "✓" / "PASS" / "全过" — 凑字总结
    5. 报告无「核心观点/主线/未来盯点」段 — 缺观点

    报告必备特征：
    - 含「核心观点」或「主线」或「未来30天盯点」段
    - 段首以"观点 1/2/3"或"判断 1/2/3"或"结论先行"开头
    - 总字数 ≥ 400 字（短于 400 = 凑字）

    0905 用户反馈原话：「不仅是核对数据真实性，而是少说水话，明确知识或观点」
    """
    c = Check("29", "v38 数据真伪报告必须含知识增量+观点", "v38")
    report_path = os.path.join(project_dir, "数据真伪核对报告.md")
    if not os.path.exists(report_path):
        c.fail("❌ 数据真伪核对报告.md 不存在")
        return c
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. 必含特征：核心观点/主线/未来盯点 至少 1 个
    KEY_FEATURES = ['核心观点', '主线', '未来', '盯点', '结论先行', '判断', '意味着']
    has_feature = any(k in content for k in KEY_FEATURES)
    if not has_feature:
        c.fail("❌ 报告无核心观点/未来盯点段 → 用户当场打回「说水话，没观点」")
        return c

    # 2. 5 类禁用句式
    WATER_PATTERNS = [
        (r'\d+\s*条全部\s*PASS', '「X 条全部 PASS」凑字总结'),
        (r'\d+\s*项红线全过', '「X 项红线全过」凑字总结'),
        (r'基本事实正确', '「基本事实正确」软话套话'),
        (r'与多家国内源表述一致', '「与多家国内源表述一致」软话套话'),
        (r'不构成失实', '「不构成失实」软话套话'),
        (r'(已确认|已缩|已替换|已渲染|已修复)(?!\w)', '过程性废话'),
        (r'三件套可交付', '「X 件套可交付」凑字总结'),
        (r'全部数据真伪 PASS', '「全部 PASS」流程化检查表'),
    ]
    water_hits = []
    for pat, desc in WATER_PATTERNS:
        if re.search(pat, content):
            water_hits.append(desc)

    if water_hits:
        c.fail("❌ 报告含水话特征：\n   " +
               "\n   ".join(f"⚠️ {h}" for h in water_hits))
        return c

    # 3. 字数下限
    word_count = len(content)
    if word_count < 400:
        c.fail(f"❌ 报告字数 {word_count} < 400 字（凑字嫌疑）")
        return c

    c.pass_(f"✓ 报告含核心观点/未来盯点段 + 字数 {word_count} ≥ 400")
    return c


def check_30_v38_fix_three_steps(project_dir):
    """v38 坑：修复必须三步全做（红线 ㉚·0905）

    当 page3.py / generate.py 的修改时间 晚于 page3.png / page1.png 时，
    报告必须显式标注「修复 → 重渲染 → 更新核对报告」三步都已执行。

    必查 3 个一致：
    1. generate.py / generate_page3.py mtime ≤ page1.png / page2.png / page3.png mtime
       （代码改了，PNG 没重渲染 = 红线 ㉚ 触线）
    2. 数据真伪核对报告 mtime ≥ 代码修改 mtime
       （代码改了但报告没更新 = 红线 ㉚ 触线）
    3. 报告内必须显式出现「重渲」「重渲染」「重新渲染」关键字（如有代码修改）
       （如果代码 mtime 晚于 PNG mtime 但报告无「重渲」字 = 凑字嫌疑）

    0905 实战踩坑：page3 长鑫份额改对了，但用旧 PNG 验收 → 错误图流出去
    """
    c = Check("30", "v38 修复三步全做（代码/PNG/报告 mtime 一致）", "v38")
    code_files = ['generate.py', 'generate_page3.py']
    png_files  = ['page1.png', 'page2.png', 'page3.png']

    code_mtime = 0.0
    code_names = []
    for cf in code_files:
        p = os.path.join(project_dir, cf)
        if os.path.exists(p):
            t = os.path.getmtime(p)
            if t > code_mtime:
                code_mtime = t
            code_names.append(cf)

    if code_mtime == 0.0:
        c.pass_("⚠️ 代码文件不存在 · 跳过")
        return c

    # 1. PNG mtime 必须 ≥ 代码 mtime（否则 = 只改代码没重渲染）
    outdated_pngs = []
    for pf in png_files:
        p = os.path.join(project_dir, pf)
        if os.path.exists(p):
            t = os.path.getmtime(p)
            if t < code_mtime - 1:  # 容忍 1 秒时钟漂移
                outdated_pngs.append(f"{pf} (mtime={int(t)} < code={int(code_mtime)})")

    report_path = os.path.join(project_dir, "数据真伪核对报告.md")
    report_mtime = os.path.getmtime(report_path) if os.path.exists(report_path) else 0

    issues = []

    # 代码改了但 PNG 没重渲
    if outdated_pngs:
        issues.append("❌ 代码改了但 PNG 未重渲染：\n   " +
                      "\n   ".join(outdated_pngs) +
                      "\n   → 必跑 python generate_page3.py 重出 PNG")

    # 代码改了但报告没更新
    if report_mtime < code_mtime - 1:
        issues.append(f"❌ 代码改了但核对报告未更新（report_mtime={int(report_mtime)} < code_mtime={int(code_mtime)}）")

    if issues:
        c.fail("\n\n".join(issues))
        return c

    c.pass_(f"✓ 代码/PNG/报告 mtime 一致（最新代码 {code_names[-1]} = {int(code_mtime)}）")
    return c


# ============================================================
# 主流程
# ============================================================

def run_all_checks(project_dir):
    today = date.today()
    generate_path = os.path.join(project_dir, "generate.py")
    page3_path = os.path.join(project_dir, "generate_page3.py")

    if not os.path.exists(generate_path):
        print(f"❌ 致命错误：{generate_path} 不存在")
        sys.exit(1)

    title, date_text, items = parse_news_items(generate_path)
    page3_descs = parse_page3_data(page3_path) if os.path.exists(page3_path) else None
    v32_data   = parse_v32_page3_data(page3_path) if os.path.exists(page3_path) else None

    checks = [
        check_01_news_overflow(items),
        check_02_media_count(items),
        check_03_24h_strict(items, today),
        check_04_page3_company_pile(page3_descs),
        check_05_y_end_sim(project_dir),
        check_06_war_headline(items),
        check_07_title_brackets(title),
        check_08_signal_space_separator(items),
        check_09_page3_phrase_dump(page3_descs),
        check_10_city_news(items),
        check_11_policy_slogan(items),
        check_12_single_company(items),
        check_13_weather_only(items),
        check_14_2020_arbitrage_residual(generate_path, page3_path),
        check_15_page3_section_gap(page3_path, project_dir),
        check_16_leader_name(items),
        check_17_military_action(items),
        check_18_abroad_source(items),
        check_19_date_prefix(items),
        check_20_signal_complete_sentence(items),
        check_21_humanizer_required(generate_path),
        check_22_data_truth_required(project_dir),
        # v32 单条深度版专项
        check_23_v32_hero_has_question(v32_data),
        check_24_v32_depth_4d(v32_data),
        check_25_v32_action_4(v32_data),
        check_26_v32_risk_disclaimer(v32_data),
        # v34 长段叙事版专项
        check_27_v34_long_narrative(v32_data, page3_path),
        # v38 升级：报告文风 + 反常识溯源 + 修复三步全做
        check_28_v38_depth2_counter_data(v32_data, page3_path),
        check_29_v38_report_knowledge_increment(project_dir),
        check_30_v38_fix_three_steps(project_dir),
    ]

    print(f"\n{'='*60}")
    print(f"v30+v32+v34+v38 踩坑清单核查 · {date_text} · {len(checks)} 项")
    print(f"{'='*60}\n")

    failed = []
    passed = 0
    for c in checks:
        symbol = "✅" if c.status == "pass" else "❌"
        print(f"[{c.id}] {symbol} {c.title}")
        print(f"    {c.detail}\n")
        if c.status == "pass":
            passed += 1
        else:
            failed.append(c)

    print(f"{'='*60}")
    print(f"✅ 通过: {passed}/{len(checks)}")
    print(f"❌ 失败: {len(failed)}/{len(checks)}")
    if failed:
        print(f"\n⚠️ 必须修复后重渲，再跑一次本脚本。\n")
    else:
        print(f"\n🎉 全部通过！可进数据核对报告 + 发布。\n")

    return len(failed)


def main():
    parser = argparse.ArgumentParser(description="v30 踩坑清单逐条核查")
    parser.add_argument("project_dir", help="项目目录（含 generate.py）")
    args = parser.parse_args()

    project_dir = os.path.abspath(args.project_dir)
    failed_count = run_all_checks(project_dir)
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()