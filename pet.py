# -*- coding: utf-8 -*-
"""
宠物窗口
========
在独立终端窗口运行：python pet.py
实时读取状态文件，根据编译结果改变表情和动画。

子命令：
  python pet.py                动画窗口（Ctrl+C 退出）
  python pet.py --name 名字    给宠物改名字（例如 --name 大橘）
  python pet.py --once         只打印当前心情的一帧（用于调试/脚本）
  python pet.py --status       打印当前状态文件内容
"""

import json
import sys
import time

import petcore as pc


def main():
    name = pc.load_config()["name"]
    state = pc.load_state()
    tick = 0
    try:
        sys.stdout.write("\033[?25l\033[2J")   # 隐藏光标 + 清屏
        while True:
            state = pc.load_state()
            mood = pc.decide_mood(state)
            idx = pc.pick_frame(mood, tick)
            rows = pc.render_rows(mood, idx, state, name)
            sys.stdout.write("\033[H")          # 回到左上角
            pc.draw_rows(rows)
            time.sleep(0.12)
            tick += 1
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h\033[0m\n")  # 恢复光标


if __name__ == "__main__":
    if "--name" in sys.argv:
        argv = sys.argv[1:]
        idx = argv.index("--name")
        name = argv[idx + 1] if idx + 1 < len(argv) else ""
        if not name:
            print("用法: pet --name <新名字>")
            print("示例: pet --name 大橘")
            sys.exit(2)
        cfg = pc.load_config()
        cfg["name"] = name
        pc.save_config(cfg)
        print("已把宠物名字改为「%s」。重新打开宠物窗口（pet）即可看到。" % name)
    elif "--once" in sys.argv:
        state = pc.load_state()
        mood = pc.decide_mood(state)
        name = pc.load_config()["name"]
        rows = pc.render_rows(mood, 0, state, name, header="终端宠物 · %s · 快照" % name)
        print("\n".join(rows))
    elif "--status" in sys.argv:
        print(json.dumps(pc.load_state(), ensure_ascii=False, indent=2))
    else:
        main()
