# -*- coding: utf-8 -*-
r"""
编译包装器
==========
用宠物感知的方式运行你的编译命令：

    pet-run cargo build                # 安装后，任意目录可用
    python pet-run.py -- cargo build   # 未安装时

流程：
  1) 运行前把心情写为「构建中」；
  2) 原样运行命令（输出直接透传到终端）；
  3) 根据退出码把心情写为「成功/失败」，并在终端下方播放一段反应动画。

退出码与原命令保持一致，可直接用于脚本判断。
"""

import subprocess
import sys
import time

import petcore as pc

VERSION = "1.1"


def _usage():
    print(__doc__)
    print("用法: pet-run <你的编译命令> [参数...]")
    print("      python pet-run.py -- <你的编译命令> [参数...]")
    print("示例: pet-run cargo build")
    print("      pet-run npm run build")
    print("提示: 分隔符 -- 可省略；写成 --cargo 也能被自动识别为 cargo。")


def main():
    args = sys.argv[1:]
    # 去掉可选的分隔符 "--"
    if args and args[0] == "--":
        args = args[1:]
    # 帮助 / 版本
    if args and args[0] in ("-h", "--help", "help"):
        _usage()
        return 0
    if args and args[0] in ("-v", "-V", "--version"):
        print("终端宠物 TerminalPet pet-run %s" % VERSION)
        return 0
    # 容错：把 "--cargo build" 这类把分隔符和命令写在一起的写法还原成 "cargo build"
    if args and args[0].startswith("--") and len(args[0]) > 2:
        args[0] = args[0][2:]
    if not args:
        _usage()
        return 2

    state = pc.load_state()
    state.update({
        "mood": "building",
        "mood_since_ts": time.time(),
        "command": " ".join(args),
        "exit_code": None,
        "duration_sec": None,
        "updated_ts": time.time(),
    })
    pc.save_state(state)

    t0 = time.perf_counter()
    try:
        proc = subprocess.run(args)
        code = proc.returncode
    except FileNotFoundError:
        code = 127
        print("[终端宠物] 找不到命令: %s" % args[0])
    except KeyboardInterrupt:
        code = 130
        print()
    duration = time.perf_counter() - t0

    mood = "success" if code == 0 else "fail"
    state.update({
        "mood": mood,
        "mood_since_ts": time.time(),
        "exit_code": code,
        "duration_sec": round(duration, 2),
        "updated_ts": time.time(),
    })
    pc.save_state(state)

    # 在命令输出下方原地播放宠物反应
    try:
        pc.animate_inline(mood, state)
    except Exception:
        pass
    return code


if __name__ == "__main__":
    sys.exit(main())
