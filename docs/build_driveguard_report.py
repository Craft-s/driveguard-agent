from pathlib import Path
from math import cos, pi, sin

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from pypdf import PdfReader


ROOT = Path(r"C:\Users\西山\Documents\ChatGPT\ican")
OUT_DIR = ROOT / "output" / "pdf"
TMP_DIR = ROOT / "tmp" / "pdfs"
OUTPUT = OUT_DIR / "DriveGuard_Agent_项目说明书.pdf"

W, H = A4
M = 42

INK = HexColor("#0A0D0B")
PAPER = HexColor("#F3F1EA")
PAPER_2 = HexColor("#E8E6DE")
WHITE = HexColor("#FFFFFF")
MUTED = HexColor("#646B63")
LINE = HexColor("#C7CAC2")
ACID = HexColor("#D8FF45")
ICE = HexColor("#8FDCFF")
SIGNAL = HexColor("#FF5C4D")
VIOLET = HexColor("#A994FF")
GREEN = HexColor("#48C78E")


def register_fonts():
    pdfmetrics.registerFont(TTFont("YaHei", r"C:\Windows\Fonts\msyh.ttc", subfontIndex=0))
    pdfmetrics.registerFont(TTFont("YaHeiB", r"C:\Windows\Fonts\msyhbd.ttc", subfontIndex=0))
    pdfmetrics.registerFont(TTFont("YaHeiL", r"C:\Windows\Fonts\msyhl.ttc", subfontIndex=0))


def rounded(c, x, y, w, h, fill, radius=8, stroke=None, sw=0.8):
    c.setLineWidth(sw)
    if stroke:
        c.setStrokeColor(stroke)
    else:
        c.setStrokeColor(fill)
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1 if stroke else 0)


def wrap_lines(text, font, size, max_width):
    lines = []
    for paragraph in str(text).split("\n"):
        if paragraph == "":
            lines.append("")
            continue
        line = ""
        for ch in paragraph:
            candidate = line + ch
            if line and pdfmetrics.stringWidth(candidate, font, size) > max_width:
                lines.append(line.rstrip())
                line = ch.lstrip() if ch == " " else ch
            else:
                line = candidate
        if line:
            lines.append(line.rstrip())
    return lines


def draw_text(c, text, x, y, width, size=10, leading=None, font="YaHei", color=INK, max_lines=None):
    leading = leading or size * 1.58
    lines = wrap_lines(text, font, size, width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        tail = lines[-1]
        while tail and pdfmetrics.stringWidth(tail + "...", font, size) > width:
            tail = tail[:-1]
        lines[-1] = tail + "..."
    c.setFont(font, size)
    c.setFillColor(color)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_bullets(c, items, x, y, width, size=9.4, leading=14.8, color=INK, accent=ACID, gap=7):
    for item in items:
        c.setFillColor(accent)
        c.circle(x + 3, y + 4, 2.2, fill=1, stroke=0)
        lines = wrap_lines(item, "YaHei", size, width - 18)
        c.setFillColor(color)
        c.setFont("YaHei", size)
        for line in lines:
            c.drawString(x + 14, y, line)
            y -= leading
        y -= gap
    return y


def page_base(c, number, section, title, subtitle=None, dark=False):
    c.setFillColor(INK if dark else PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    if dark:
        return
    c.setFillColor(INK)
    c.rect(0, H - 7, W, 7, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(MUTED)
    c.drawString(M, H - 38, f"{number:02d}  /  {section.upper()}")
    title_size = 23
    while title_size > 17 and pdfmetrics.stringWidth(title, "YaHeiB", title_size) > W - 2 * M:
        title_size -= 0.5
    c.setFont("YaHeiB", title_size)
    c.setFillColor(INK)
    c.drawString(M, H - 74, title)
    if subtitle:
        c.setFont("YaHei", 8.6)
        c.setFillColor(MUTED)
        c.drawString(M, H - 94, subtitle)
    c.setStrokeColor(LINE)
    c.setLineWidth(0.7)
    c.line(M, H - 108, W - M, H - 108)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(MUTED)
    c.drawString(M, 24, "DRIVEGUARD AGENT  /  PROJECT DOCUMENTATION")
    c.drawRightString(W - M, 24, f"{number:02d}")


def section_tag(c, text, x, y, color=INK, fill=ACID):
    width = pdfmetrics.stringWidth(text, "YaHeiB", 7.6) + 18
    rounded(c, x, y - 3, width, 18, fill, radius=4)
    c.setFillColor(color)
    c.setFont("YaHeiB", 7.6)
    c.drawString(x + 9, y + 2, text)
    return width


def stat_card(c, x, y, w, h, number, label, note, color):
    rounded(c, x, y, w, h, WHITE, radius=10, stroke=LINE)
    c.setFillColor(color)
    c.rect(x, y + h - 6, w, 6, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(x + 15, y + h - 38, number)
    c.setFont("YaHeiB", 10)
    c.drawString(x + 15, y + h - 57, label)
    draw_text(c, note, x + 15, y + h - 76, w - 30, 7.8, 11.5, color=MUTED, max_lines=3)


def two_col_text(
    c,
    left_title,
    left_items,
    right_title,
    right_items,
    y_top=H - 136,
    bottom=82,
    body_size=9.2,
    body_leading=14.2,
    body_gap=8,
):
    gap = 18
    col = (W - M * 2 - gap) / 2
    for x, title, items, accent in [
        (M, left_title, left_items, ACID),
        (M + col + gap, right_title, right_items, ICE),
    ]:
        rounded(c, x, bottom, col, y_top - bottom, WHITE, radius=10, stroke=LINE)
        section_tag(c, title, x + 16, y_top - 26, fill=accent)
        draw_bullets(c, items, x + 16, y_top - 58, col - 32, size=body_size, leading=body_leading, gap=body_gap, accent=accent)


def flow_box(c, x, y, w, h, title, subtitle, fill, text_color=INK):
    rounded(c, x, y, w, h, fill, radius=8)
    c.setFillColor(text_color)
    c.setFont("YaHeiB", 9.5)
    c.drawCentredString(x + w / 2, y + h - 20, title)
    c.setFont("YaHei", 6.8)
    c.drawCentredString(x + w / 2, y + 10, subtitle)


def arrow(c, x1, y1, x2, y2, color=MUTED):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.2)
    c.line(x1, y1, x2, y2)
    angle = 0 if x2 >= x1 else pi
    if abs(y2 - y1) > abs(x2 - x1):
        angle = pi / 2 if y2 > y1 else -pi / 2
    s = 5
    pts = [
        (x2, y2),
        (x2 - s * cos(angle - .55), y2 - s * sin(angle - .55)),
        (x2 - s * cos(angle + .55), y2 - s * sin(angle + .55)),
    ]
    path = c.beginPath()
    path.moveTo(*pts[0])
    path.lineTo(*pts[1])
    path.lineTo(*pts[2])
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def draw_cover(c):
    page_base(c, 1, "Cover", "", dark=True)
    c.setFillColor(ACID)
    c.rect(0, H - 12, W, 12, fill=1, stroke=0)
    for i in range(9):
        c.setStrokeColor(HexColor("#202620"))
        c.setLineWidth(0.6)
        c.circle(W * .74, H * .56, 32 + i * 18, fill=0, stroke=1)
    for i in range(26):
        a = i * (2 * pi / 26)
        r = 68 + (i % 5) * 17
        x = W * .74 + cos(a) * r
        y = H * .56 + sin(a) * r * .66
        c.setFillColor([ACID, ICE, SIGNAL, VIOLET][i % 4])
        c.circle(x, y, 2.2 if i % 3 else 3.4, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(ACID)
    c.drawString(M, H - 72, "VISION PERCEPTION  /  MULTI-AGENT DECISION  /  ACTIVE INTERVENTION")
    c.setFont("Helvetica-Bold", 45)
    c.setFillColor(WHITE)
    c.drawString(M, H - 160, "DRIVEGUARD")
    c.drawString(M, H - 208, "AGENT")
    c.setFont("YaHeiB", 24)
    c.setFillColor(WHITE)
    c.drawString(M, H - 266, "基于视觉感知与多智能体决策的")
    c.drawString(M, H - 300, "驾驶安全主动干预系统")
    c.setStrokeColor(HexColor("#3B423B"))
    c.line(M, H - 336, W - M, H - 336)
    draw_text(
        c,
        "项目说明书 | 覆盖背景、需求、AI技术方案、功能说明、使用流程、应用前景与商业模式",
        M,
        H - 370,
        W * .62,
        size=10.5,
        leading=17,
        color=HexColor("#B8BEB6"),
    )
    rounded(c, M, 70, W - 2 * M, 86, HexColor("#121612"), radius=8, stroke=HexColor("#313731"))
    c.setFont("YaHeiB", 9)
    c.setFillColor(ACID)
    c.drawString(M + 18, 130, "作品定位")
    c.setFont("YaHei", 10)
    c.setFillColor(WHITE)
    c.drawString(M + 18, 107, "从单帧目标检测升级为具备时序理解、风险推理、主动预警和驾驶报告能力的 AI Agent 产品。")
    c.setFont("Helvetica", 8)
    c.setFillColor(HexColor("#737B72"))
    c.drawString(M + 18, 84, "VERSION 1.1  /  SEPTEMBER 2026  /  THREE-MODEL FUSION PROTOTYPE")


def draw_toc(c):
    page_base(c, 2, "Overview", "目录与阅读地图", "本说明书共18页，重点内容可按模块快速定位。")
    entries = [
        ("01", "项目背景与机会", "03-04", ACID),
        ("02", "痛点与需求分析", "05-07", ICE),
        ("03", "技术架构与AI方案", "08-11", VIOLET),
        ("04", "功能与使用说明", "12-14", SIGNAL),
        ("05", "工程、验证与边界", "15-16", GREEN),
        ("06", "前景、商业模式与路线", "17", ACID),
        ("07", "总结与参考资料", "18", ICE),
    ]
    y = H - 148
    for no, title, pages, color in entries:
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(M, y, no)
        c.setFillColor(INK)
        c.setFont("YaHeiB", 13)
        c.drawString(M + 44, y - 2, title)
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(W - M, y, pages)
        c.setStrokeColor(LINE)
        c.line(M + 44, y - 14, W - M, y - 14)
        y -= 68
    rounded(c, M, 76, W - 2 * M, 74, INK, radius=8)
    c.setFillColor(ACID)
    c.setFont("YaHeiB", 9.5)
    c.drawString(M + 18, 125, "核心结论")
    c.setFillColor(WHITE)
    c.setFont("YaHei", 9.5)
    c.drawString(M + 18, 101, "作品的价值不在于“识别到一个标签”，而在于把连续行为转化为可解释风险，并立即完成闭环干预。")


def draw_background(c):
    page_base(c, 3, "Background", "项目背景：驾驶风险需要从“事后统计”走向“事中干预”")
    stat_card(c, M, H - 260, 154, 118, "4x", "手机使用事故风险", "WHO指出，驾驶时使用手机会显著增加事故风险，并影响制动反应、车道保持与跟车距离。[1]", SIGNAL)
    stat_card(c, M + 170, H - 260, 154, 118, "3,208", "分心驾驶死亡人数", "NHTSA公布的2024年数据：美国涉及分心驾驶的道路事故造成3,208人死亡。[2]", ICE)
    stat_card(c, M + 340, H - 260, 154, 118, "DDAW", "监管与行业方向", "欧盟法规要求相关车型配置驾驶员困倦与注意力警告系统，并通过HMI向驾驶员发出提醒。[3]", ACID)
    c.setFont("YaHeiB", 14)
    c.setFillColor(INK)
    c.drawString(M, H - 306, "为什么选择车内视觉感知")
    body = (
        "危险驾驶往往不是单一瞬间，而是一个逐渐累积的过程：眨眼频率升高、闭眼持续时间增加、低头查看物品、视线长期离开道路、接打电话或未系安全带。"
        "传统车辆告警通常依赖单一传感器或固定规则，难以理解这些行为之间的时间关系。车内摄像头能够以低成本提供连续观察窗口，再结合边缘AI与时序规则，将行为信号转化为可解释的风险结论。"
    )
    draw_text(c, body, M, H - 332, W - 2 * M, 10.4, 17.8, color=MUTED)
    rounded(c, M, 135, W - 2 * M, 225, WHITE, radius=10, stroke=LINE)
    section_tag(c, "项目机会", M + 16, 328, fill=ACID)
    draw_bullets(c, [
        "浏览器端视觉推理降低了部署门槛：普通笔记本或车载计算单元即可运行原型，不依赖持续上传视频。",
        "主动干预比单纯记录更有价值：系统在风险发生过程中发出提示音、语音提醒，并保留事件轨迹。",
        "可解释报告使安全管理从“凭感觉”变成“有证据”：事件次数、风险时段、组合行为与建议均可回溯。",
        "模块化Agent链路便于后续连接车队平台、智能座舱或LLM复盘能力，同时保留安全规则的确定性。",
    ], M + 16, 300, W - 2 * M - 32, size=9.8, leading=15.5, gap=7)


def draw_problem(c):
    page_base(c, 4, "Pain Points", "当前方案的典型痛点", "从传统检测网页、人工管理和工程落地三个层面分析。")
    cards = [
        ("01", "单帧识别缺乏上下文", "模型只能回答“这一帧是什么”，不能判断行为是否持续、是否反复、是否与其他异常共同发生。", ACID),
        ("02", "误报与漏报影响信任", "光照、眼镜、摄像头角度、短暂眨眼和自然侧视都会造成波动；没有个人基线与防抖时，告警容易失真。", ICE),
        ("03", "告警方式缺少闭环", "很多系统只显示红框或置信度，没有提示音、语音建议、解除机制与后续驾驶报告。", SIGNAL),
        ("04", "隐私与算力成本矛盾", "云端分析需要上传视频，带来网络延迟、带宽费用和隐私风险；本地设备算力又有限。", VIOLET),
        ("05", "管理者缺少可解释证据", "车队或驾校真正需要的是时段、频次、严重程度和改进建议，而不是一串模型日志。", GREEN),
        ("06", "工程环境复杂", "摄像头权限、硬件开关、虚拟设备、浏览器兼容和模型加载失败都会影响实际使用。", ACID),
    ]
    cols = 2
    gap = 16
    cw = (W - M * 2 - gap) / 2
    ch = 162
    y_top = H - 136
    for i, (no, title, text, color) in enumerate(cards):
        col = i % cols
        row = i // cols
        x = M + col * (cw + gap)
        y = y_top - (row + 1) * ch - row * 12
        rounded(c, x, y, cw, ch, WHITE, radius=9, stroke=LINE)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + 16, y + ch - 27, no)
        c.setFillColor(INK)
        c.setFont("YaHeiB", 12)
        c.drawString(x + 50, y + ch - 28, title)
        draw_text(c, text, x + 16, y + ch - 58, cw - 32, 9, 14.8, color=MUTED, max_lines=5)


def draw_users(c):
    page_base(c, 5, "Users", "目标用户群体与关键场景")
    users = [
        ("个人驾驶员", "新手、长途驾驶者、网约车司机", ["实时发现疲劳与分心", "获得即时、清晰的干预", "驾驶结束后复盘习惯"], ACID),
        ("车队与运营管理者", "物流、客运、工程车辆", ["统一观察风险事件", "识别高风险时段与司机", "形成培训和管理依据"], ICE),
        ("驾校与安全培训机构", "教练、学员、实验课程", ["直观展示不安全行为", "量化训练过程", "用于AI与交通安全教学"], VIOLET),
        ("整车与后装集成方", "DMS方案商、智能座舱团队", ["验证视觉与HMI交互", "评估端侧部署路径", "扩展车辆信号融合"], SIGNAL),
    ]
    gap = 14
    cw = (W - 2 * M - gap) / 2
    ch = 246
    for i, (name, profile, needs, color) in enumerate(users):
        x = M + (i % 2) * (cw + gap)
        y = H - 136 - (i // 2 + 1) * ch - (i // 2) * 14
        rounded(c, x, y, cw, ch, WHITE, radius=10, stroke=LINE)
        c.setFillColor(color)
        c.circle(x + 31, y + ch - 34, 15, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(x + 31, y + ch - 38, str(i + 1).zfill(2))
        c.setFont("YaHeiB", 13)
        c.drawString(x + 56, y + ch - 31, name)
        c.setFont("YaHei", 8.2)
        c.setFillColor(MUTED)
        c.drawString(x + 56, y + ch - 49, profile)
        c.setFillColor(LINE)
        c.rect(x + 16, y + ch - 76, cw - 32, 1, fill=1, stroke=0)
        section_tag(c, "核心诉求", x + 16, y + ch - 104, fill=color)
        draw_bullets(c, needs, x + 16, y + ch - 132, cw - 32, size=9, leading=14, gap=7, accent=color)


def draw_requirements(c):
    page_base(c, 6, "Requirements", "需求分析：从识别能力到干预闭环")
    two_col_text(c, "功能需求 Functional", [
        "摄像头接入：申请权限、枚举设备、处理无设备、虚拟摄像头和启动失败等状态。",
        "五类安全行为：闭眼、低头或视线偏移、手机使用、抽烟、未系安全带。",
        "行为时序：对连续帧进行防抖、持续时间判断和事件计数，避免单帧即报警。",
        "风险决策：根据行为类型、持续时间和组合情况生成1至3级风险。",
        "主动干预：提示音、中文语音、界面高亮与风险说明协同工作。",
        "驾驶报告：展示安全评分、事件次数、风险结论和自然语言解释。",
    ], "非功能需求 Non-functional", [
        "实时性：人脸分析保持高频，目标检测按设备能力间隔执行，不阻塞界面。",
        "隐私性：视频默认只在浏览器本地处理，不上传原始画面。",
        "可解释性：展示行为名称、指标状态、风险等级与触发原因，不只显示置信度。",
        "鲁棒性：采用个人基线、持续阈值和多信号交叉验证，减少自然动作误报。",
        "兼容性：优先支持最新版Edge和Chrome，并提供摄像头故障诊断。",
        "可扩展性：感知、时序、风险、干预与报告模块解耦，便于接入更多传感器。",
    ], bottom=250, body_size=10.8, body_leading=17.8, body_gap=10)
    rounded(c, M, 78, W - 2 * M, 136, INK, radius=10)
    c.setFillColor(ACID)
    c.setFont("YaHeiB", 10)
    c.drawString(M + 18, 181, "需求结论")
    c.setFillColor(WHITE)
    c.setFont("YaHeiB", 14)
    c.drawString(M + 18, 150, "系统必须同时做到：看得见、判得准、说得清、能干预。")
    draw_text(c, "识别准确率只是基础，真正可用的驾驶安全产品还需要稳定的时序判断、可解释的风险结论、低打扰的告警方式，以及对摄像头和浏览器异常的完整处理。", M + 18, 120, W - 2 * M - 36, 9.2, 14.5, color=HexColor("#B8BEB6"))


def draw_scope(c):
    page_base(c, 7, "Scope", "目标、验收标准与作品边界")
    rounded(c, M, H - 274, W - 2 * M, 136, INK, radius=10)
    c.setFillColor(ACID)
    c.setFont("YaHeiB", 10)
    c.drawString(M + 18, H - 168, "总体目标")
    c.setFillColor(WHITE)
    c.setFont("YaHeiB", 16)
    c.drawString(M + 18, H - 198, "将连续驾驶行为转化为可解释、可干预、可复盘的风险事件。")
    draw_text(c, "作品强调端侧实时运行与闭环体验，而非仅展示YOLO检测框。", M + 18, H - 226, W - 2 * M - 36, 9.5, 15, color=HexColor("#B8BEB6"))
    c.setFont("YaHeiB", 13)
    c.setFillColor(INK)
    c.drawString(M, H - 312, "可验收的完成标准")
    draw_bullets(c, [
        "用户能启动摄像头并完成4秒个人姿态校准；异常状态有明确诊断信息。",
        "闭眼持续约0.55秒、低头或视线偏移持续约0.7秒后形成事件，短暂动作不计入。",
        "手机与抽烟需要连续目标确认；安全带通过多帧状态进行判断。",
        "异常首次成立时出现视觉高亮和双音提示，高风险时可继续触发中文语音干预。",
        "用户可打开报告查看事件数量、安全评分与AI解释，并可询问“为什么报警”。",
    ], M, H - 340, W - 2 * M, size=10.1, leading=16, gap=7)
    rounded(c, M, 170, W - 2 * M, 164, WHITE, radius=9, stroke=LINE)
    section_tag(c, "边界声明", M + 16, 302, fill=SIGNAL)
    draw_text(c, "当前版本是教育与产品原型，使用公开模型和浏览器端推理，尚未完成车规级数据闭环、夜间红外适配、极端姿态测试、功能安全认证或量产合规验证。因此不能替代驾驶员判断，也不能作为事故责任认定工具。作品当前验证的是可运行的技术链路与交互闭环，量产应用仍需专用硬件、规模化数据与合规测试。", M + 16, 274, W - 2 * M - 32, 9.8, 15.8, color=MUTED)


def draw_architecture(c):
    page_base(c, 8, "Architecture", "总体技术架构", "摄像头输入经过感知、时序、风险与Agent协同，形成主动干预闭环。")
    x0 = M
    y = H - 230
    boxes = [
        ("Camera", "MediaDevices", ACID),
        ("Perception", "YOLO + Face + Phone", ICE),
        ("Temporal", "Debounce + Streak", VIOLET),
        ("Risk", "Level 1-3", SIGNAL),
        ("Agent", "Reason + Action", ACID),
        ("Output", "Tone + Voice + Report", GREEN),
    ]
    bw = 75
    gap = 10
    for i, (title, sub, color) in enumerate(boxes):
        x = x0 + i * (bw + gap)
        flow_box(c, x, y, bw, 78, title, sub, color)
        if i < len(boxes) - 1:
            arrow(c, x + bw + 2, y + 39, x + bw + gap - 2, y + 39)
    rounded(c, M, H - 460, W - 2 * M, 172, WHITE, radius=10, stroke=LINE)
    section_tag(c, "五个逻辑Agent", M + 16, H - 320, fill=INK, color=WHITE)
    agents = [
        ("Perception Agent", "提取目标、眼部与姿态信号"),
        ("Temporal Agent", "确认持续时间与连续帧"),
        ("Risk Agent", "组合行为并计算风险等级"),
        ("Intervention Agent", "选择提示音、语音和界面反馈"),
        ("Report Agent", "沉淀统计与自然语言解释"),
    ]
    yy = H - 355
    for i, (name, desc) in enumerate(agents):
        c.setFillColor([ACID, ICE, VIOLET, SIGNAL, GREEN][i])
        c.circle(M + 25, yy + 3, 4, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9.1)
        c.drawString(M + 38, yy, name)
        c.setFont("YaHei", 9.1)
        c.setFillColor(MUTED)
        c.drawString(M + 164, yy, desc)
        yy -= 22
    panel_y = 160
    rounded(c, M, panel_y, W - 2 * M, 138, INK, radius=9)
    c.setFillColor(ACID)
    c.setFont("YaHeiB", 10)
    c.drawString(M + 16, panel_y + 106, "Agent的核心价值")
    draw_text(c, "系统不把一次模型输出直接等同于危险，而是把多源信号放入时间窗口，判断其是否持续、是否组合、是否需要升级风险，并选择合适的干预动作。这就是作品由“检测页面”向“主动安全Agent”升级的关键。", M + 16, panel_y + 76, W - 2 * M - 32, 9.8, 15.8, color=WHITE)


def draw_ai_perception(c):
    page_base(c, 9, "AI Core", "AI感知层：三模型协同与冲突裁决")
    gap = 12
    cw = (W - 2 * M - gap * 2) / 3
    rounded(c, M, H - 430, cw, 292, WHITE, radius=10, stroke=LINE)
    rounded(c, M + cw + gap, H - 430, cw, 292, WHITE, radius=10, stroke=LINE)
    rounded(c, M + (cw + gap) * 2, H - 430, cw, 292, WHITE, radius=10, stroke=LINE)
    section_tag(c, "YOLO11n Object Detection", M + 16, H - 168, fill=ICE)
    draw_text(c, "driver-monitor.onnx", M + 16, H - 200, cw - 32, 8.8, 13, font="Helvetica-Bold")
    draw_bullets(c, [
        "640×640 letterbox输入，由ONNX Runtime Web + WASM执行。",
        "识别疲劳、分心、用手机、安全带与抽烟等驾驶语义。",
        "IoU 0.45 NMS；抽烟最终确认阈值为0.28。",
        "手机与抽烟均需连续两次推理，抑制单帧波动。",
    ], M + 16, H - 226, cw - 32, size=7.8, leading=12.1, gap=6, accent=ICE)
    section_tag(c, "MediaPipe Face Landmarker", M + cw + gap + 16, H - 168, fill=VIOLET)
    draw_text(c, "眼部、虹膜、姿态与面部跟踪", M + cw + gap + 16, H - 200, cw - 32, 8.7, 13, font="YaHeiB")
    draw_bullets(c, [
        "在归一化视频帧上计算EAR、俯仰/偏航、视线与低头几何量。",
        "4秒个人基线用于适配脸型、镜头角度和坐姿差异。",
        "GPU优先；推理异常或启动持续无脸时自动切换CPU。",
        "闭眼时暂停虹膜偏移判定，减少眼睑遮挡误报。",
    ], M + cw + gap + 16, H - 226, cw - 32, size=7.8, leading=12.1, gap=6, accent=VIOLET)
    third_x = M + (cw + gap) * 2
    section_tag(c, "EfficientDet-Lite0", third_x + 16, H - 168, fill=SIGNAL)
    draw_text(c, "独立手机目标检测器（CPU）", third_x + 16, H - 200, cw - 32, 8.7, 13, font="YaHeiB")
    draw_bullets(c, [
        "MediaPipe Object Detector加载COCO手机类别。",
        "0.20候选阈值；结合手机与人脸的空间位置验证使用场景。",
        "为PhoneUse动作模型提供独立物体证据。",
        "检测到真实手机时优先判手机，并抑制香烟误报。",
    ], third_x + 16, H - 226, cw - 32, size=7.8, leading=12.1, gap=6, accent=SIGNAL)
    panel_y = 178
    rounded(c, M, panel_y, W - 2 * M, 155, INK, radius=9)
    c.setFillColor(ACID)
    c.setFont("YaHeiB", 10)
    c.drawString(M + 16, panel_y + 122, "融合策略")
    draw_text(c, "YOLO负责驾驶动作语义，Face Landmarker负责精细生理与姿态特征，EfficientDet-Lite0提供独立手机物体证据。冲突裁决不再要求香烟分数压过相似的手机动作分数：只在独立检测器确实看到手机时抑制抽烟；否则Smoking达到0.28并连续两次出现即可形成事件。", M + 16, panel_y + 92, W - 2 * M - 32, 9.5, 15.2, color=WHITE)


def draw_temporal(c):
    page_base(c, 10, "AI Core", "时序分析与个体化校准", "把不稳定的逐帧信号转换为可靠事件。")
    y = H - 345
    stages = [
        ("01", "4秒校准", "正视前方，采集EAR、头姿、视线和面部几何中位数基线", ACID),
        ("02", "多频率测量", "人脸约80ms；手机目标约650ms；YOLO动作约850ms一次", ICE),
        ("03", "持续确认", "闭眼约0.55秒；低头与视线偏移约0.7秒；目标需连续帧", VIOLET),
        ("04", "事件上升沿", "仅在安全状态转为异常状态时计数并播放提示音", SIGNAL),
    ]
    gap = 12
    cw = (W - 2 * M - gap * 3) / 4
    for i, (no, title, text, color) in enumerate(stages):
        x = M + i * (cw + gap)
        rounded(c, x, y, cw, 166, WHITE, radius=9, stroke=LINE)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(x + 14, y + 128, no)
        c.setFillColor(INK)
        c.setFont("YaHeiB", 10.5)
        c.drawString(x + 14, y + 101, title)
        draw_text(c, text, x + 14, y + 76, cw - 28, 8, 12.5, color=MUTED, max_lines=5)
    c.setFont("YaHeiB", 13)
    c.setFillColor(INK)
    c.drawString(M, H - 432, "关键判定逻辑")
    rows = [
        ("闭眼", "EAR低于个人动态阈值，或Drowsy语义目标成立", "≥0.55 s"),
        ("低头", "俯仰角与鼻眼下巴几何量共同变化，并排除明显侧转", "≥0.70 s"),
        ("视线偏移", "虹膜相对眼角持续偏移，且眼睛保持睁开", "≥0.70 s"),
        ("手机 / 抽烟", "动作语义与独立手机物体证据进行冲突裁决", "连续2次"),
        ("未系安全带", "面部可见，且连续推理未确认Seatbelt目标", "连续6次"),
    ]
    table_x = M
    table_w = W - 2 * M
    behavior_x = table_x + 12
    condition_x = table_x + 108
    duration_x = table_x + table_w - 86
    condition_w = duration_x - condition_x - 18
    y0 = H - 466
    c.setFillColor(PAPER_2)
    c.roundRect(table_x, y0 - 13, table_w, 27, 4, fill=1, stroke=0)
    for x, t in [(behavior_x, "行为"), (condition_x, "融合条件"), (duration_x, "确认阈值")]:
        c.setFillColor(INK)
        c.setFont("YaHeiB", 8.5)
        c.drawString(x, y0 - 4, t)
    row_h = 43
    row_top = y0 - 26
    for i, (behavior, condition, duration) in enumerate(rows):
        top = row_top - i * row_h
        if i % 2 == 1:
            c.setFillColor(HexColor("#ECEAE3"))
            c.rect(table_x, top - row_h + 2, table_w, row_h - 2, fill=1, stroke=0)
        c.setStrokeColor(LINE)
        c.line(table_x, top - row_h + 2, table_x + table_w, top - row_h + 2)
        c.setFillColor(INK)
        c.setFont("YaHeiB", 8.4)
        c.drawString(behavior_x, top - 24, behavior)
        draw_text(c, condition, condition_x, top - 18, condition_w, 8.0, 11.2, color=MUTED, max_lines=2)
        c.setFont("YaHeiB", 8.2)
        c.setFillColor(INK)
        c.drawString(duration_x, top - 24, duration)
    c.setFont("YaHei", 7.5)
    c.setFillColor(MUTED)
    c.drawString(M, 118, "注：时间与连续次数是当前原型的事件确认参数，可在真实道路数据验证后重新标定。")


def draw_risk_agent(c):
    page_base(c, 11, "AI Core", "风险决策与主动干预Agent")
    rounded(c, M, H - 290, W - 2 * M, 152, WHITE, radius=10, stroke=LINE)
    c.setFont("YaHeiB", 12)
    c.setFillColor(INK)
    c.drawString(M + 16, H - 174, "当前原型的风险权重")
    weights = [("闭眼", 45, ACID), ("手机", 38, SIGNAL), ("未系安全带", 30, ICE), ("注意力偏移", 22, VIOLET), ("抽烟", 18, GREEN)]
    x = M + 16
    for label, value, color in weights:
        w = (W - 2 * M - 48) * value / 153
        c.setFillColor(color)
        c.rect(x, H - 242, w, 24, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("YaHeiB", 7.5)
        c.drawCentredString(x + w / 2, H - 235, f"{label} {value}")
        x += w
    c.setFont("YaHei", 8.4)
    c.setFillColor(MUTED)
    c.drawString(M + 16, H - 266, "组合得分 <20 为一级监测；20-54 为二级注意；≥55 为三级高风险。权重用于原型演示，可由真实数据重新标定。")
    left = M
    right = M + 264
    rounded(c, left, 105, 244, 380, INK, radius=10)
    c.setFillColor(ACID)
    c.setFont("YaHeiB", 10)
    c.drawString(left + 16, 455, "Agent推理示例")
    sequence = [("闭眼", "0.7s", ACID), ("低头", "1.1s", ICE), ("闭眼", "1.2s", ACID), ("闭眼", "1.6s", SIGNAL)]
    yy = 420
    for i, (label, duration, color) in enumerate(sequence):
        c.setFillColor(color)
        c.circle(left + 26, yy + 4, 5, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("YaHeiB", 10)
        c.drawString(left + 44, yy, label)
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor("#A8B0A7"))
        c.drawRightString(left + 220, yy, duration)
        if i < len(sequence) - 1:
            c.setStrokeColor(HexColor("#3D443D"))
            c.line(left + 26, yy - 9, left + 26, yy - 24)
        yy -= 58
    c.setStrokeColor(HexColor("#3D443D"))
    c.line(left + 16, 180, left + 228, 180)
    draw_text(c, "最近30秒异常频率上升，闭眼持续时间逐渐增加，并出现低头行为。疲劳风险由一级提升至三级。", left + 16, 155, 212, 9, 14.5, color=WHITE)
    rounded(c, right, 105, W - M - right, 380, WHITE, radius=10, stroke=LINE)
    section_tag(c, "干预策略", right + 16, 455, fill=SIGNAL)
    draw_bullets(c, [
        "一级：维持监测，界面显示稳定状态。",
        "二级：行为卡片高亮，播放双音提示，展示具体原因。",
        "三级：高风险视觉状态 + 中文语音，建议安全停车休息。",
        "提示音由Web Audio实时生成，不依赖外部文件；启动按钮同时解锁浏览器音频。",
        "语音使用SpeechSynthesis，并设置30秒冷却，避免频繁打扰。",
        "用户可点击“重播警告”播放当前语音，或点击“标记已解决”确认已处理。",
    ], right + 16, 422, W - M - right - 32, size=8.8, leading=13.8, gap=7, accent=SIGNAL)


def draw_functions_1(c):
    page_base(c, 12, "Functions", "作品功能说明 I：实时监测与告警")
    functions = [
        ("摄像头启动与诊断", "自动尝试默认、前置及枚举设备；区分权限拒绝、无实体摄像头、虚拟摄像头离线和硬件不可用。", ICE),
        ("闭眼/疲劳识别", "根据个人EAR基线识别持续闭眼，并可融合YOLO的Drowsy语义结果。", ACID),
        ("低头与视线偏移", "分别分析pitch、yaw、面部几何和虹膜位置；低头、侧转、左右视线拥有不同解释。", VIOLET),
        ("手机与抽烟识别", "YOLO动作语义配合独立cell phone目标证据；连续帧streak确认事件并处理类别冲突。", SIGNAL),
        ("安全带状态", "连续确认Seatbelt目标；面部存在而多帧无安全带时生成异常事件。", GREEN),
        ("实时可视化", "展示检测框、Face Track、行为状态、风险等级、模型延迟和30秒事件时间轴。", ICE),
    ]
    y = H - 148
    for i, (title, desc, color) in enumerate(functions):
        x = M if i % 2 == 0 else M + 264
        yy = y - (i // 2) * 160
        rounded(c, x, yy - 127, 248, 128, WHITE, radius=9, stroke=LINE)
        c.setFillColor(color)
        c.rect(x, yy - 127, 7, 128, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 18, yy - 27, f"0{i + 1}")
        c.setFont("YaHeiB", 11)
        c.drawString(x + 50, yy - 28, title)
        draw_text(c, desc, x + 18, yy - 58, 212, 9.2, 14.8, color=MUTED, max_lines=5)
    rounded(c, M, 82, W - 2 * M, 112, INK, radius=9)
    c.setFillColor(ACID)
    c.setFont("YaHeiB", 9.5)
    c.drawString(M + 18, 160, "实时闭环")
    c.setFillColor(WHITE)
    c.setFont("YaHeiB", 13)
    c.drawString(M + 18, 132, "实时识别  ·  持续确认  ·  风险升级  ·  主动干预  ·  驾驶报告")
    draw_text(c, "六项功能共享同一事件状态，不是彼此孤立的检测组件。", M + 18, 106, W - 2 * M - 36, 9, 14, color=HexColor("#B8BEB6"))


def draw_functions_2(c):
    page_base(c, 13, "Functions", "作品功能说明 II：解释、报告与交互")
    two_col_text(c, "AI解释与自然语言助手", [
        "Agent reasoning区域根据当前最高优先级风险生成标题、原因、指标变化和建议。",
        "低头会说明姿态与几何偏移；视线偏移会说明虹膜相对个人正视基线的变化。",
        "用户可询问“我刚才为什么一直报警”，系统依据本次会话事件统计生成结构化解释。",
        "当前助手属于状态驱动的自然语言解释，不依赖云端大模型，保证结果可控且可追溯。",
        "后续可接入LLM，对结构化事件做更丰富的复盘，但不得让LLM替代感知与安全判定。",
    ], "驾驶报告与安全评分", [
        "记录闭眼、注意力偏移、手机、抽烟和未系安全带的事件次数。",
        "按照异常类型扣分形成0至100的会话安全评分。",
        "报告强调“满足持续阈值的真实事件”，不把每一帧识别当成一次异常。",
        "30秒事件窗口驱动时间轴，帮助用户理解行为发生顺序。",
        "可扩展高风险时段、前后半程对比、驾驶时长和趋势分析。",
    ], bottom=320, body_size=10.3, body_leading=16.8, body_gap=10)
    rounded(c, M, 85, W - 2 * M, 185, INK, radius=9)
    c.setFillColor(ACID)
    c.setFont("YaHeiB", 9.5)
    c.drawString(M + 18, 235, "AI功能的核心作用")
    c.setFillColor(WHITE)
    c.setFont("YaHeiB", 13.5)
    c.drawString(M + 18, 202, "感知负责发现事实，Agent负责解释风险并决定行动。")
    draw_text(c, "自然语言能力建立在结构化事件之上：模型输出、持续时间、组合行为和风险等级均可追溯；即使后续接入LLM，也不让生成式模型替代安全判定。", M + 18, 169, W - 2 * M - 36, 9.5, 15.2, color=HexColor("#B8BEB6"))


def draw_usage(c):
    page_base(c, 14, "User Guide", "完整使用说明与操作流程")
    steps = [
        ("01", "打开系统", "使用最新版Edge或Chrome进入DriveGuard Agent。", ACID),
        ("02", "启动摄像头", "点击“启动车内摄像头”，在浏览器提示中允许摄像头。", ICE),
        ("03", "完成校准", "保持正视前方约4秒，等待CALIBRATING切换为FORWARD。", VIOLET),
        ("04", "开始驾驶监测", "系统持续分析闭眼、低头、视线、手机、抽烟和安全带。", SIGNAL),
        ("05", "处理告警", "听到提示音后查看原因；高风险语音建议停车时应优先保证安全。", GREEN),
        ("06", "查看报告", "点击报告入口，查看评分、事件计数和AI解释。", ACID),
    ]
    y = H - 150
    for i, (no, title, desc, color) in enumerate(steps):
        x = M + (i % 2) * 264
        yy = y - (i // 2) * 170
        rounded(c, x, yy - 132, 248, 134, WHITE, radius=9, stroke=LINE)
        c.setFillColor(color)
        c.circle(x + 29, yy - 29, 16, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(x + 29, yy - 32, no)
        c.setFont("YaHeiB", 11.5)
        c.drawString(x + 56, yy - 25, title)
        draw_text(c, desc, x + 56, yy - 49, 174, 8.5, 13.4, color=MUTED, max_lines=4)
    rounded(c, M, 72, W - 2 * M, 72, INK, radius=8)
    c.setFillColor(ACID)
    c.setFont("YaHeiB", 9)
    c.drawString(M + 16, 118, "安全交互原则")
    c.setFillColor(WHITE)
    c.setFont("YaHei", 8.8)
    c.drawString(M + 16, 93, "驾驶中不要操作报告或输入框。所有页面交互应在车辆停稳后完成；告警只提供辅助，不替代驾驶员判断。")


def draw_interaction(c):
    page_base(c, 15, "Interaction", "交互指南、状态反馈与异常处理")
    rows = [
        ("CALIBRATING", "正在建立个人正视基线", "正视前方，避免频繁眨眼或转头", VIOLET),
        ("FORWARD", "姿态与视线稳定", "无需操作，保持正常驾驶", GREEN),
        ("LOOKING DOWN", "持续低头成立", "抬头看路；若需要操作设备请安全停车", SIGNAL),
        ("GAZE AWAY", "虹膜持续偏离道路方向", "恢复前方视线，减少车内物品干扰", ICE),
        ("HEAD TURN", "头部明显侧转", "确认道路情况并恢复正向姿态", VIOLET),
        ("NO CAMERA DEVICE", "浏览器未发现实体摄像头", "检查物理遮挡、键盘热键、驱动或USB连接", SIGNAL),
    ]
    y0 = H - 150
    for i, (state, meaning, action, color) in enumerate(rows):
        y = y0 - i * 84
        rounded(c, M, y - 57, W - 2 * M, 62, WHITE, radius=7, stroke=LINE)
        c.setFillColor(color)
        c.rect(M, y - 57, 6, 62, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(M + 18, y - 20, state)
        c.setFont("YaHeiB", 8.5)
        c.drawString(M + 144, y - 20, meaning)
        c.setFont("YaHei", 8.2)
        c.setFillColor(MUTED)
        c.drawString(M + 300, y - 20, action)
    rounded(c, M, 76, W - 2 * M, 92, INK, radius=9)
    c.setFillColor(ACID)
    c.setFont("YaHeiB", 9)
    c.drawString(M + 16, 140, "提示音说明")
    draw_text(c, "闭眼、手机和未系安全带使用更急促的三段音；低头、视线偏移和抽烟使用双音提示。声音在点击启动按钮时由浏览器解锁，若无声请检查标签页及系统音量。", M + 16, 114, W - 2 * M - 32, 8.8, 13.8, color=WHITE)


def draw_tools(c):
    page_base(c, 16, "Engineering", "开发工具、工程实现与验证")
    tools = [
        ("Frontend", "HTML5 / CSS3 / JavaScript ES Modules", "单页实时监测界面、Canvas叠加和响应式布局"),
        ("Vision Runtime", "ONNX Runtime Web 1.23.2", "在浏览器使用WebAssembly执行ONNX模型推理[5]"),
        ("Face AI", "MediaPipe Tasks Vision 1.0.1", "面部关键点、虹膜点与变换矩阵"),
        ("Object AI", "EfficientDet-Lite0 INT8", "MediaPipe CPU推理与COCO cell phone独立物体证据[8]"),
        ("Browser APIs", "MediaDevices / Web Audio / Web Speech", "摄像头、提示音和中文语音[6]"),
        ("Model", "YOLO11n-derived ONNX", "公开Driver Monitoring System模型与CC BY 4.0数据来源[7]"),
        ("Delivery", "Git + OpenAI Sites", "版本化发布静态站点，模型与页面统一分发"),
    ]
    y = H - 150
    for i, (kind, tech, desc) in enumerate(tools):
        yy = y - i * 68
        c.setFillColor(PAPER_2 if i % 2 == 0 else WHITE)
        c.roundRect(M, yy - 52, W - 2 * M, 58, 6, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8.7)
        c.drawString(M + 14, yy - 19, kind.upper())
        tech_x = M + 118
        tech_w = 178
        desc_x = M + 304
        desc_w = W - M - 14 - desc_x
        tech_y = yy - (14 if len(wrap_lines(tech, "Helvetica-Bold", 8.8, tech_w)) > 1 else 20)
        desc_y = yy - (14 if len(wrap_lines(desc, "YaHei", 8.2, desc_w)) > 1 else 20)
        draw_text(c, tech, tech_x, tech_y, tech_w, 8.8, 11, font="Helvetica-Bold", color=INK, max_lines=2)
        draw_text(c, desc, desc_x, desc_y, desc_w, 8.2, 11, font="YaHei", color=MUTED, max_lines=2)
    rounded(c, M, 78, W - 2 * M, 104, INK, radius=9)
    c.setFillColor(ACID)
    c.setFont("YaHeiB", 9.5)
    c.drawString(M + 16, 150, "验证策略")
    draw_text(c, "当前工程验证包括脚本语法、三模型加载、摄像头多路径启动、GPU到CPU自动回退、姿态角数学验证、连续阈值、手机与香烟冲突回归和界面响应式检查。量产前仍需建立覆盖光照、肤色、眼镜、口罩、夜间、颠簸及不同摄像头位置的数据集。", M + 16, 124, W - 2 * M - 32, 8.6, 13.4, color=WHITE)


def draw_privacy(c):
    page_base(c, 17, "Outlook", "应用前景、商业模式与发展路线")
    left_w = 246
    rounded(c, M, H - 472, left_w, 334, WHITE, radius=10, stroke=LINE)
    rounded(c, M + left_w + 16, H - 472, W - 2 * M - left_w - 16, 334, WHITE, radius=10, stroke=LINE)
    section_tag(c, "应用前景", M + 16, H - 168, fill=ACID)
    draw_bullets(c, [
        "个人安全助手：在笔记本、平板或后装车机上提供轻量监测。",
        "商用车队：结合驾驶时长、GPS与车辆CAN信号形成风险运营平台。",
        "驾校与高校：用于驾驶行为训练、计算机视觉和AI Agent课程展示。",
        "智能座舱验证：作为DMS算法和HMI策略的快速原型。",
        "保险与安全服务：在用户授权和合规前提下提供风险改善计划。",
    ], M + 16, H - 200, left_w - 32, size=8.7, leading=13.4, gap=7, accent=ACID)
    section_tag(c, "商业模式", M + left_w + 32, H - 168, fill=ICE)
    draw_bullets(c, [
        "B2C订阅：基础监测免费，高级报告、历史趋势和多设备同步付费。",
        "B2B SaaS：按车辆或司机数量向车队提供管理后台、风险报表与API。",
        "Edge License：向座舱或后装方案商授权端侧模型与SDK。",
        "硬件套装：摄像头、边缘计算盒与软件服务一体化销售。",
        "项目定制：面向驾校、实验室和交通安全单位提供私有化部署。",
    ], M + left_w + 32, H - 200, W - 2 * M - left_w - 48, size=8.7, leading=13.4, gap=7, accent=ICE)
    c.setFont("YaHeiB", 13)
    c.setFillColor(INK)
    c.drawString(M, H - 518, "三阶段发展路线")
    phases = [
        ("Phase 1", "原型验证", "完善标定、阈值配置、事件回放与数据导出", ACID),
        ("Phase 2", "场景产品化", "红外摄像头、车速联动、车队后台和隐私策略", ICE),
        ("Phase 3", "车规化探索", "多传感器融合、功能安全、法规测试与量产适配", SIGNAL),
    ]
    gap = 12
    cw = (W - 2 * M - 2 * gap) / 3
    for i, (phase, name, desc, color) in enumerate(phases):
        x = M + i * (cw + gap)
        rounded(c, x, 92, cw, 172, INK, radius=8)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(x + 14, 235, phase.upper())
        c.setFillColor(WHITE)
        c.setFont("YaHeiB", 11)
        c.drawString(x + 14, 207, name)
        draw_text(c, desc, x + 14, 179, cw - 28, 8.3, 13, color=HexColor("#B8BEB6"), max_lines=5)


def draw_conclusion(c):
    page_base(c, 18, "Conclusion", "总结与参考资料")
    rounded(c, M, H - 278, W - 2 * M, 140, INK, radius=10)
    c.setFillColor(ACID)
    c.setFont("YaHeiB", 10)
    c.drawString(M + 18, H - 172, "项目总结")
    draw_text(c, "DriveGuard Agent通过YOLO驾驶动作检测、MediaPipe Face Landmarker、EfficientDet-Lite0手机目标检测、本地时序分析、风险决策与主动干预，将摄像头画面转换为连续驾驶安全事件。AI核心不仅识别标签，还通过多源证据裁决类别冲突，理解行为是否持续、是否组合、是否需要升级风险。", M + 18, H - 201, W - 2 * M - 36, 9.7, 15.5, color=WHITE)
    c.setFont("YaHeiB", 12)
    c.setFillColor(INK)
    c.drawString(M, H - 316, "参考资料")
    refs = [
        ("[1] WHO - Road traffic injuries", "https://www.who.int/news-room/fact-sheets/detail/road-traffic-injuries/"),
        ("[2] NHTSA - Distracted Driving", "https://www.nhtsa.gov/risky-driving/distracted-driving"),
        ("[3] EU 2021/1341 - Driver drowsiness and attention warning", "https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32021R1341"),
        ("[4] MediaPipe FaceGeometry specification", "https://github.com/google-ai-edge/mediapipe/blob/master/mediapipe/modules/face_geometry/protos/face_geometry.proto"),
        ("[5] ONNX Runtime Web documentation", "https://onnxruntime.ai/docs/tutorials/web/"),
        ("[6] MDN - MediaDevices.getUserMedia()", "https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia"),
        ("[7] AlbatrossC Driver Monitoring System", "https://github.com/AlbatrossC/Driver-Monitoring-System"),
        ("[8] MediaPipe Object Detector guide", "https://ai.google.dev/edge/mediapipe/solutions/vision/object_detector/web_js"),
    ]
    y = H - 344
    for label, url in refs:
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8.2)
        c.drawString(M + 4, y, label)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 6.8)
        c.drawString(M + 4, y - 13, url)
        c.linkURL(url, (M, y - 16, W - M, y + 6), relative=0)
        y -= 43
    rounded(c, M, 72, W - 2 * M, 68, PAPER_2, radius=8)
    c.setFillColor(INK)
    c.setFont("YaHeiB", 8.8)
    c.drawString(M + 16, 116, "真实性说明")
    c.setFont("YaHei", 7.8)
    c.setFillColor(MUTED)
    c.drawString(M + 16, 92, "本文只描述当前原型已实现或明确规划的能力。作品尚未通过车规级认证，不应作为量产安全系统或事故责任依据。")


def build_pdf():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    register_fonts()
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    c.setTitle("DriveGuard Agent 项目说明书")
    c.setAuthor("DriveGuard Agent Project")
    pages = [
        draw_cover,
        draw_toc,
        draw_background,
        draw_problem,
        draw_users,
        draw_requirements,
        draw_scope,
        draw_architecture,
        draw_ai_perception,
        draw_temporal,
        draw_risk_agent,
        draw_functions_1,
        draw_functions_2,
        draw_usage,
        draw_interaction,
        draw_tools,
        draw_privacy,
        draw_conclusion,
    ]
    for index, draw_page in enumerate(pages):
        draw_page(c)
        if index != len(pages) - 1:
            c.showPage()
    c.save()
    reader = PdfReader(str(OUTPUT))
    if len(reader.pages) > 20:
        raise RuntimeError(f"PDF exceeds page limit: {len(reader.pages)}")
    print(f"Created {OUTPUT} with {len(reader.pages)} pages")


if __name__ == "__main__":
    build_pdf()

