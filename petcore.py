# -*- coding: utf-8 -*-
r"""
终端宠物核心库
================
负责：心情定义、动画帧、状态文件读写、终端渲染辅助。

状态文件默认位于 ~/.terminal-pet/state.json（Windows: %USERPROFILE%\.terminal-pet\state.json），
可用环境变量 PET_STATE_DIR 覆盖（例如让每个项目各养一只）。
由 pet-run（编译包装器）写入，由 pet.py（宠物窗口）读取，
从而实现「宠物随编译结果变脸」。
"""

import json
import os
import sys
import time

# Windows 下启用 ANSI 转义，并统一 stdout/stderr 编码为 UTF-8
if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    os.system("")

# ------------------------------------------------------------------ 路径
STATE_DIR = os.environ.get("PET_STATE_DIR") or os.path.join(os.path.expanduser("~"), ".terminal-pet")
STATE_FILE = os.path.join(STATE_DIR, "state.json")
CONFIG_FILE = os.path.join(STATE_DIR, "config.json")

# ------------------------------------------------------------------ 颜色（truecolor，Windows Terminal 完全支持）
C = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "dim":    "\033[2m",
    "cyan":   "\033[38;2;120;205;255m",
    "pink":   "\033[38;2;255;150;190m",
    "yellow": "\033[38;2;255;215;110m",
    "orange": "\033[38;2;255;165;85m",
    "blue":   "\033[38;2;150;175;255m",
    "gray":   "\033[38;2;145;145;158m",
    "green":  "\033[38;2;145;215;150m",
    "red":    "\033[38;2;255;125;125m",
    "white":  "\033[38;2;235;235;245m",
}

# ------------------------------------------------------------------ 动画帧
def _deco(color, ch):
    """给装饰字符单独上色（放在行尾，不影响主体）。"""
    return color + ch + C["reset"]

# 每帧 3~5 行，主体（耳朵/脸/下巴）缩进保持一致，避免画面抖动
IDLE = (
    ("  /\\_/\\ ", " ( o.o )" + _deco(C["gray"], "~"), "  > ^ < "),
    ("  /\\_/\\ ", " ( o.o )" + _deco(C["gray"], "⌒"), "  > ^ < "),
    ("  /\\_/\\ ", " ( -.- )" + _deco(C["gray"], "~"), "  > ^ < "),   # 眨眼
)

BUILD = tuple(
    ("  /\\_/\\ " + _deco(C["cyan"], "'"),
     " ( o.o )" + _deco(C["orange"], g),
     "  > ^ < ")
    for g in ("◴", "◷", "◶", "◵")   # 齿轮旋转
)

SUCCESS = (
    (" ", "  /\\_/\\ " + _deco(C["yellow"], "♪"),
     " ( ^.^ )" + _deco(C["pink"], "♥"), "  > ^ < "),
    ("  /\\_/\\ " + _deco(C["pink"], "♥"), " ( >ω< )", "  > ^ < "),   # 高兴得跳起
    (" ", "  /\\_/\\ " + _deco(C["pink"], "♥"),
     " ( ^.^ )" + _deco(C["yellow"], "♪"), "  > ^ < "),
)

FAIL = (
    ("  /\\_/\\ ", " ( ;_; )", "  > ^ < ",
     "  " + _deco(C["blue"], ";") + "   " + _deco(C["blue"], ";")),
    (_deco(C["gray"], "☁") + "    ", "  /\\_/\\ ", " ( ;_; )", "  > ^ < ",
     "   " + _deco(C["blue"], ";") + " ;  "),
    ("  /\\_/\\ ", " ( ;_; )", "  > ^ < ",
     " " + _deco(C["blue"], ";") + "     " + _deco(C["blue"], ";")),
)

SLEEP = (
    ("  " + _deco(C["dim"] + C["white"], "z"), "  /\\_/\\ ", " ( -ω- )", "  > ^ < "),
    ("    " + _deco(C["dim"] + C["white"], "Z"), "  /\\_/\\ ", " ( -ω- )", "  > ^ < "),
)

MOODS = {
    "idle":     {"frames": IDLE,    "label": "等待构建", "color": C["cyan"],   "icon": "🐾"},
    "building": {"frames": BUILD,   "label": "构建中…",   "color": C["orange"], "icon": "⚙"},
    "success":  {"frames": SUCCESS, "label": "构建成功",   "color": C["yellow"], "icon": "🎉"},
    "fail":     {"frames": FAIL,    "label": "构建失败",   "color": C["blue"],   "icon": "💔"},
    "sleep":    {"frames": SLEEP,   "label": "睡觉中…",   "color": C["gray"],   "icon": "💤"},
}

CAT_ROWS = 5      # 猫咪区域行数（含云朵/泪滴等额外行）
TOTAL_ROWS = 8    # 整个面板行数 = 标题 1 + 猫咪 5 + 状态 2

# ------------------------------------------------------------------ 心情规则（秒）
SUCCESS_SHOW_SEC = 12    # 成功后开心 12 秒
FAIL_SHOW_SEC = 25       # 失败后难过 25 秒
BUILD_MAX_SEC = 3600     # 「构建中」超过 1 小时视为卡死，回到待机
SLEEP_AFTER_SEC = 300    # 空闲 5 分钟后开始打盹

# ------------------------------------------------------------------ 配置
DEFAULT_NAME = "小喵"

def load_config():
    cfg = dict(name=DEFAULT_NAME)
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("name"), str):
            cfg["name"] = data["name"]
    except Exception:
        pass
    return cfg

# ------------------------------------------------------------------ 状态文件
def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_state(state):
    """写状态文件；失败时只告警，绝不中断编译流程。"""
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        os.replace(tmp, STATE_FILE)  # 原子替换，避免宠物读到写了一半的文件
        return True
    except Exception as e:
        print("[终端宠物] 状态文件写入失败（%s），不影响编译本身。" % e, file=sys.stderr)
        return False

# ------------------------------------------------------------------ 心情推导
def decide_mood(state, now=None):
    now = now if now is not None else time.time()
    mood = state.get("mood", "idle")
    if mood not in MOODS:
        mood = "idle"
    since = state.get("mood_since_ts") or 0
    if mood == "success":
        return "idle" if since and now - since > SUCCESS_SHOW_SEC else "success"
    if mood == "fail":
        return "idle" if since and now - since > FAIL_SHOW_SEC else "fail"
    if mood == "building":
        if since and now - since > BUILD_MAX_SEC:
            return "idle"
        return "building"
    # idle：长时间没动静就去睡觉
    last = state.get("mood_since_ts") or state.get("updated_ts") or now
    if now - last > SLEEP_AFTER_SEC:
        return "sleep"
    return "idle"

# ------------------------------------------------------------------ 帧选择
def pick_frame(mood, tick):
    n = len(MOODS[mood]["frames"])
    if mood == "idle":
        if tick % 24 == 0:                      # 约每 3 秒眨一次眼
            return 2
        return 0 if (tick // 6) % 2 == 0 else 1 # 尾巴左右摆
    if mood == "sleep":
        return (tick // 5) % n
    return tick % n

# ------------------------------------------------------------------ 渲染
def frame_lines(mood, index):
    lines = list(MOODS[mood]["frames"][index % len(MOODS[mood]["frames"])])
    while len(lines) < CAT_ROWS:
        lines.append("")
    return lines[:CAT_ROWS]

def info_line(state):
    if not state:
        return "运行 pet-run <你的编译命令> 来开始吧！"
    parts = []
    if state.get("command"):
        parts.append("命令: " + state["command"])
    if state.get("duration_sec") is not None:
        parts.append("用时: %.1fs" % state["duration_sec"])
    if state.get("exit_code") is not None:
        parts.append("退出码: %s" % state["exit_code"])
    return "  ·  ".join(parts) if parts else "（还没有构建记录）"

def render_rows(mood, index, state, name, header=None):
    m = MOODS.get(mood) or MOODS["idle"]
    rows = []
    hdr = header if header is not None else "终端宠物 · %s    [Ctrl+C 退出]" % name
    rows.append(C["bold"] + C["white"] + hdr + C["reset"])
    for ln in frame_lines(mood, index):
        rows.append(m["color"] + ln + C["reset"])
    rows.append(m["color"] + m["icon"] + " " + m["label"] + C["reset"])
    rows.append(C["gray"] + info_line(state) + C["reset"])
    return rows

def draw_rows(rows):
    """从当前位置向下重绘面板（每行先清行），光标停在面板底部。"""
    for r in rows:
        sys.stdout.write("\033[2K" + r + "\n")
    sys.stdout.flush()

def animate_inline(mood, state, ticks=10, delay=0.15, header="终端宠物 · 构建完成"):
    """在命令输出下方原地播放一小段心情动画（供 pet-run 调用）。"""
    name = load_config()["name"]
    frames = MOODS.get(mood, MOODS["idle"])["frames"]

    def draw(i):
        draw_rows(render_rows(mood, i % len(frames), state, name, header))

    draw(0)
    for i in range(1, ticks):
        time.sleep(delay)
        sys.stdout.write("\033[%dA" % TOTAL_ROWS)   # 回到面板顶部
        draw(i)
