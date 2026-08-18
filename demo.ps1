# demo.ps1 - 演示终端宠物如何随编译结果变脸
# 运行: .\demo.ps1   （若提示禁止执行脚本: powershell -ExecutionPolicy Bypass -File demo.ps1）
$here = $PSScriptRoot
if (-not $here) { $here = Split-Path -Parent $MyInvocation.MyCommand.Path }

$py = $null
foreach ($cand in @("python", "py")) {
    $cmd = Get-Command $cand -ErrorAction SilentlyContinue
    if ($cmd) { $py = $cmd.Source; break }
}
if (-not $py) {
    Write-Host "[终端宠物] 未找到 Python，请先安装 Python 3 (https://www.python.org)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "===== 演示 1：编译成功 =====" -ForegroundColor Cyan
& $py "$here\pet-run.py" -- python -c "import time; time.sleep(2); print('gcc main.c -o main   (模拟编译成功)')"

Write-Host ""
Write-Host "===== 演示 2：编译失败 =====" -ForegroundColor Cyan
& $py "$here\pet-run.py" -- python -c "import time; time.sleep(2); print('gcc main.c -o main   (模拟编译失败)'); import sys; sys.exit(1)"

Write-Host ""
Write-Host "提示：另开一个终端窗口运行 python pet.py，就能看到宠物实时变脸！" -ForegroundColor Yellow
exit 0
