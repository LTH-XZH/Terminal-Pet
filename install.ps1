<#
.SYNOPSIS
  把终端宠物安装到 PATH，让你在任意目录都能使用 pet-run / pet。

.DESCRIPTION
  运行一次：.\install.ps1
  - 生成 pet-run.cmd / pet.cmd 两个命令
  - 记录项目目录到环境变量 TERMINALPET_HOME（环境变量存的是 Unicode，中文路径安全）
  - 把命令目录加入用户 PATH（新开终端永久生效，当前终端立即生效）

  不想改动注册表（例如只想临时用）：.\install.ps1 -NoPersist
#>
[CmdletBinding()]
param(
    [string]$BinDir = (Join-Path $env:LOCALAPPDATA "TerminalPet\bin"),
    [switch]$NoPersist
)
$ErrorActionPreference = "Stop"

$src = $PSScriptRoot
if (-not $src) { $src = Split-Path -Parent $MyInvocation.MyCommand.Path }

# 找 Python
$py = $null
foreach ($cand in @("python", "py")) {
    $c = Get-Command $cand -ErrorAction SilentlyContinue
    if ($c) { $py = $c.Source; break }
}
if (-not $py) {
    Write-Host "[终端宠物] 未找到 Python，请先安装 Python 3 (https://www.python.org)" -ForegroundColor Red
    exit 1
}

# 建 bin 目录
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

# 生成命令（内容纯 ASCII，避免 cmd 用 GBK 读取 UTF-8 文件导致解析错乱）
$runCmd = @'
@echo off
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY (where py >nul 2>nul && set "PY=py")
if not defined PY (
  echo [TerminalPet] Python 3 not found. Install from https://www.python.org
  exit /b 1
)
%PY% "%TERMINALPET_HOME%\pet-run.py" -- %*
exit /b %ERRORLEVEL%
'@
$petCmd = @'
@echo off
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY (where py >nul 2>nul && set "PY=py")
if not defined PY (
  echo [TerminalPet] Python 3 not found. Install from https://www.python.org
  exit /b 1
)
%PY% "%TERMINALPET_HOME%\pet.py" %*
'@
Set-Content -Encoding Ascii -Path (Join-Path $BinDir "pet-run.cmd") -Value $runCmd
Set-Content -Encoding Ascii -Path (Join-Path $BinDir "pet.cmd") -Value $petCmd

# 环境变量
if (-not $NoPersist) {
    [Environment]::SetEnvironmentVariable("TERMINALPET_HOME", $src, "User")
    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if (-not $userPath) { $userPath = "" }
    $parts = @($userPath -split ';' | Where-Object { $_ -and ($_.TrimEnd('\') -ne $BinDir.TrimEnd('\')) })
    $newPath = (@($parts) + $BinDir) -join ';'
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
}
$env:TERMINALPET_HOME = $src
if (($env:PATH -split ';') -notcontains $BinDir) {
    $env:PATH = "$BinDir;$env:PATH"
}

Write-Host ""
Write-Host "[终端宠物] 安装完成！" -ForegroundColor Green
Write-Host "  宠物窗口：pet" -ForegroundColor Cyan
Write-Host "  编译包装：pet-run cargo build" -ForegroundColor Cyan
if ($NoPersist) {
    Write-Host "  （-NoPersist 模式：仅当前终端生效，未写入注册表）" -ForegroundColor Yellow
} else {
    Write-Host "  新开的终端会自动生效；当前终端已立即可用。" -ForegroundColor Yellow
}
Write-Host ""
