# 100 Case 全量实验：Windows 一步跑完指南

正式版本：

```text
Branch: fullrun/stable-v1
Commit: 34d0a42
Expected tests: 49 passed
Total jobs: 1200
```

三人固定分工：

```text
队友 A：case_001 ~ case_033
队友 B：case_034 ~ case_066
队友 C：case_067 ~ case_100
```

正式实验开始后不要修改代码、配置、分支和结果目录。

---

## 第 1 步：三个人都拉取同一个正式版本

在项目根目录打开 PowerShell，执行：

```powershell
git fetch origin
git checkout fullrun/stable-v1
git pull origin fullrun/stable-v1
git log -1 --oneline
git status
```

必须看到：

```text
34d0a42 freeze stable distributed full100 runner
```

如果不是 `34d0a42`，停止，不要继续。

---

## 第 2 步：三个人都运行测试

为避免 Windows 临时目录权限/锁定问题，三个人统一使用“每次创建一个全新的 pytest 临时目录”的方式。

执行：

```powershell
$pytestTmp = Join-Path $PWD ("tmp_pytest_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force $pytestTmp | Out-Null

.\.venv\Scripts\python.exe -m pytest -q `
  --basetemp=$pytestTmp `
  -p no:cacheprovider
```

必须看到：

```text
49 passed
```

如果不是 `49 passed`，停止，不要继续。

注意：

```text
不要重复使用旧的 tmp_pytest 目录。
不要因为旧临时目录 PermissionError 去修改项目代码。
```

---

## 第 3 步：三个人都禁止电脑自动睡眠

保持电脑接通电源。

打开：

```text
Windows 设置
→ 系统
→ 电源和电池
→ 屏幕和睡眠
```

将“接通电源后，使设备进入睡眠”设置为：

```text
从不
```

正式实验期间不要关机、重启或进入睡眠。

---

## 第 4 步：创建日志目录

三个人都执行：

```powershell
New-Item -ItemType Directory -Force .\logs
```

---

## 第 5 步：A、B、C 三人分别启动自己的正式实验

### 队友 A 执行

```powershell
$p = Start-Process powershell.exe `
  -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\scripts\run_full100_A.ps1`"" `
  -RedirectStandardOutput ".\logs\full100_A.out.log" `
  -RedirectStandardError ".\logs\full100_A.err.log" `
  -PassThru

$p.Id | Out-File .\logs\full100_A.pid
$p.Id
```

### 队友 B 执行

```powershell
$p = Start-Process powershell.exe `
  -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\scripts\run_full100_B.ps1`"" `
  -RedirectStandardOutput ".\logs\full100_B.out.log" `
  -RedirectStandardError ".\logs\full100_B.err.log" `
  -PassThru

$p.Id | Out-File .\logs\full100_B.pid
$p.Id
```

### 队友 C 执行

```powershell
$p = Start-Process powershell.exe `
  -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\scripts\run_full100_C.ps1`"" `
  -RedirectStandardOutput ".\logs\full100_C.out.log" `
  -RedirectStandardError ".\logs\full100_C.err.log" `
  -PassThru

$p.Id | Out-File .\logs\full100_C.pid
$p.Id
```

执行后不要再启动第二份同组任务。

---

## 第 6 步：确认任务已经真正启动

### 队友 A

```powershell
Get-Process -Id (Get-Content .\logs\full100_A.pid)
Get-Content .\logs\full100_A.out.log -Tail 20
Get-Content .\logs\full100_A.err.log -Tail 20
```

### 队友 B

```powershell
Get-Process -Id (Get-Content .\logs\full100_B.pid)
Get-Content .\logs\full100_B.out.log -Tail 20
Get-Content .\logs\full100_B.err.log -Tail 20
```

### 队友 C

```powershell
Get-Process -Id (Get-Content .\logs\full100_C.pid)
Get-Content .\logs\full100_C.out.log -Tail 20
Get-Content .\logs\full100_C.err.log -Tail 20
```

看到进程存在，并且 `out.log` 开始出现类似：

```text
case_xxx p1 n2: baseline=..., multiseed=..., vns=...
```

说明正式实验已经开始。

如果 `err.log` 中只有类似下面的旧 pytest 临时目录警告：

```text
warning: could not open directory 'tmp_pytest/': Permission denied
```

可以忽略，不要停止正式实验。这个警告与 full100 求解本身无关。

判断正式实验是否正常，应以以下两点为准：

```text
1. out.log 持续出现新的 case_xxx pX nY 结果；
2. results/full100_teammate_* 目录中的结果文件数量持续增加。
```

只有在出现 Python traceback、明确的 job failed、后台进程消失且结果不再增长时，才按“第 8 步：中断续跑”处理。

---

## 第 7 步：运行期间只做进度检查，不改代码

每隔一段时间检查一次。

### 队友 A

```powershell
Get-Process -Id (Get-Content .\logs\full100_A.pid)
Get-Content .\logs\full100_A.out.log -Tail 20
Get-Content .\logs\full100_A.err.log -Tail 20
Get-ChildItem .\results\full100_teammate_A -Recurse -File | Measure-Object
```

### 队友 B

```powershell
Get-Process -Id (Get-Content .\logs\full100_B.pid)
Get-Content .\logs\full100_B.out.log -Tail 20
Get-Content .\logs\full100_B.err.log -Tail 20
Get-ChildItem .\results\full100_teammate_B -Recurse -File | Measure-Object
```

### 队友 C

```powershell
Get-Process -Id (Get-Content .\logs\full100_C.pid)
Get-Content .\logs\full100_C.out.log -Tail 20
Get-Content .\logs\full100_C.err.log -Tail 20
Get-ChildItem .\results\full100_teammate_C -Recurse -File | Measure-Object
```

运行期间禁止：

```text
git pull
git checkout
修改 configs/fullrun_stable.yaml
修改 solver
删除 results/full100_teammate_*
重新启动同组第二个任务
```

补充说明：

```text
如果 err.log 只有 tmp_pytest Permission denied 警告，而 out.log 正常增长，
不要重启、不要停任务、不要修权限。
```

---

## 第 8 步：如果任务意外中断，直接原目录续跑

不要删除任何结果。

### A 组中断后执行

```powershell
$p = Start-Process powershell.exe `
  -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\scripts\run_full100_A.ps1`"" `
  -RedirectStandardOutput ".\logs\full100_A_resume.out.log" `
  -RedirectStandardError ".\logs\full100_A_resume.err.log" `
  -PassThru

$p.Id | Out-File .\logs\full100_A.pid
```

### B 组中断后执行

```powershell
$p = Start-Process powershell.exe `
  -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\scripts\run_full100_B.ps1`"" `
  -RedirectStandardOutput ".\logs\full100_B_resume.out.log" `
  -RedirectStandardError ".\logs\full100_B_resume.err.log" `
  -PassThru

$p.Id | Out-File .\logs\full100_B.pid
```

### C 组中断后执行

```powershell
$p = Start-Process powershell.exe `
  -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\scripts\run_full100_C.ps1`"" `
  -RedirectStandardOutput ".\logs\full100_C_resume.out.log" `
  -RedirectStandardError ".\logs\full100_C_resume.err.log" `
  -PassThru

$p.Id | Out-File .\logs\full100_C.pid
```

runner 已验证支持 resume，会跳过已经完成的 job。

---

## 第 9 步：三组都跑完后，把结果集中到同一台电脑

最终必须同时存在：

```text
results/full100_teammate_A
results/full100_teammate_B
results/full100_teammate_C
```

不要修改目录内部文件。

---

## 第 10 步：检查 1200 个正式 job 是否完整

在汇总结果的电脑上执行：

```powershell
.\.venv\Scripts\python.exe scripts\check_full100_coverage.py
```

最终必须看到：

```text
total 1200 / 1200 jobs
```

并且各组合均完整：

```text
P1 N2
P1 N3
P1 N4
P1 N5
P2 N2
P2 N3
P2 N4
P2 N5
P3 N2
P3 N3
P3 N4
P3 N5
```

如果不是 `1200 / 1200`，根据 `results/full100_missing_jobs.txt` 补跑缺失 job，直到完整。

---

## 第 11 步：合并三组正式结果

确认已经达到：

```text
1200 / 1200 jobs
```

然后执行：

```powershell
.\.venv\Scripts\python.exe scripts\merge_full100_results.py
```

最终结果位于：

```text
results/full100_merged/
```

重点文件：

```text
results/full100_merged/detail.csv
results/full100_merged/summary.csv
```

至此 100 Case 全量正式实验完成。

---

# 最终检查

最终必须满足：

```text
Branch: fullrun/stable-v1
Commit: 34d0a42
pytest: 49 passed
A组: 完成
B组: 完成
C组: 完成
coverage: 1200 / 1200
merged: results/full100_merged
```
