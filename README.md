# 终端宠物 🐱

一只**活在终端里的小猫**，会跟着你的编译结果变脸：

- 编译**成功** → 开心地跳起来，冒出小爱心 `( ^.^ )♥`
- 编译**失败** → 沮丧地耷拉下来，掉眼泪 `( ;_; )`
- 编译**进行中** → 专注地盯着你，尾巴变成旋转的齿轮 ⚙
- 长时间没动静 → 打盹睡觉 💤

## 快速开始

### 0. 安装到 PATH（推荐，做一次即可）

在项目目录里运行一次安装脚本：

```powershell
.\install.ps1
```

它会生成 `pet-run` / `pet` 两个命令并加入你的用户 PATH，
之后**在任何目录**都能直接使用（中文路径也没问题）。

> 只想临时用、不想改环境变量：`.\install.ps1 -NoPersist`（仅当前终端生效）。

### 1. 打开宠物窗口（新开一个终端标签页/窗格）

```bash
pet
```

> 💡 建议用 **Windows Terminal**，把窗口分屏：左侧跑编译、右侧住着宠物。
> 快捷键：`Alt+Shift+D` 垂直分屏，`Alt+Shift+-` 水平分屏。

### 2. 用宠物感知的方式跑编译

在任何目录，把编译命令前加上 `pet-run` 即可：

```bash
# 原来
cargo build

# 现在
pet-run cargo build
```

其它示例：

```bash
pet-run cargo build
pet-run npm run build
pet-run gcc main.c -o main
pet-run make
pet-run cl /EHsc main.cpp
```

`pet-run` 的退出码与原命令一致，可以照常接 `&&` / `if ($LASTEXITCODE)` 使用。

### 未安装时也可以直接用（需在项目目录内）

```bash
python pet-run.py -- cargo build
```

- 分隔符 `--` **可以省略**：`python pet-run.py cargo build` 同样有效；
- 手滑写成 `--cargo build` 也会被自动识别成 `cargo build`；
- PowerShell 里也可以用 `.\pet-run.ps1 cargo build`。

## 工作原理

```
┌─────────────┐   写状态文件    ┌──────────────────┐
│  pet-run.py │ ──────────────▶ │ ~/.terminal-pet/ │
│ (编译包装器) │  心情/命令/退出码 │   state.json     │
└─────────────┘                 └────────┬─────────┘
                                         │ 轮询读取
                              ┌──────────▼──────────┐
                              │      pet.py         │
                              │  (宠物窗口·实时动画)  │
                              └─────────────────────┘
```

- `pet-run` 在命令运行前把心情写成 `building`，结束后按退出码写成 `success` / `fail`；
- `pet.py` 每 0.12 秒读一次状态文件并重绘画面，所以宠物窗口和编译窗口可以不在同一个终端；
- 状态文件用「临时文件 + 原子替换」写入，宠物永远不会读到写了一半的内容。

## 心情一览

| 心情      | 触发条件                       | 表现                        | 持续时间 |
|-----------|--------------------------------|-----------------------------|----------|
| 待机      | 无构建记录 / 心情自然消退       | 眨眼、摇尾巴                 | 一直     |
| 构建中    | pet-run 开始运行命令            | 齿轮旋转、冒汗               | 直到结束 |
| 成功      | 命令退出码 = 0                 | 蹦跳、爱心、音符             | 12 秒    |
| 失败      | 命令退出码 ≠ 0                 | 泪眼、雨云、掉眼泪           | 25 秒    |
| 睡觉      | 空闲超过 5 分钟                | 打呼噜 z Z                  | 直到下次构建 |

## 自定义

### 改名字

编辑 `%USERPROFILE%\.terminal-pet\config.json`：

```json
{ "name": "大橘" }
```

### 调整心情持续时间 / 动画

打开 `petcore.py`，顶部附近的常量可以直接改：

```python
SUCCESS_SHOW_SEC = 12    # 成功后开心多久
FAIL_SHOW_SEC    = 25    # 失败后难过多久
SLEEP_AFTER_SEC  = 300   # 空闲多久开始打盹
```

### 换宠物 / 加新心情

每帧都是几行文本，在 `petcore.py` 的 `MOODS` 里增删即可。注意保持主体行的缩进一致，画面就不会抖。

## 文件结构

```
终端宠物/
├── petcore.py      # 核心库：心情、动画帧、状态文件读写
├── pet.py          # 宠物窗口（实时动画）
├── pet-run.py      # 编译包装器（写状态 + 播放反应）
├── install.ps1     # 一键安装：生成 pet-run / pet 命令并加入 PATH
├── pet-run.ps1     # PowerShell 启动器
├── pet.bat         # 宠物窗口启动器（双击/命令行）
├── pet-run.bat     # 编译包装器启动器
├── demo.ps1        # 一键演示成功/失败两种反应
└── README.md
```

## 小贴士

- 在 **Windows Terminal** 下效果最佳（支持 truecolor 和 UTF-8）；
- 如果是在旧版 `cmd` 里运行，宠物会自动启用 ANSI 转义，但建议用 Windows Terminal；
- 构建卡死超过 1 小时，宠物会从「构建中」回到「待机」，避免一直转齿轮；
- 想看宠物当前状态：`pet --once`（打印一帧）或 `pet --status`（打印状态 JSON）；
- 卸载：删除 `%LOCALAPPDATA%\TerminalPet\bin`，并从用户环境变量里移除该目录与 `TERMINALPET_HOME`。
