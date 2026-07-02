---
name: surround-scm-extractor
description: Extracts files from Surround SCM 2015.1.0 using CLI automation. Discovers projects (mainline/branch) by keyword, searches files by pattern, retrieves by path/label/timestamp with modular extraction strategy. Use when user asks "extract from Surround", "get SCM files", "download from repository", "提取SCM文件", "从Surround下载", "get source code from SCM", or needs source code/configs/documents from Surround SCM repositories.
---

# Surround SCM Extractor

Intelligently extracts files from Surround SCM 2015.1.0 repositories through CLI automation.

## Configure Credentials (One-time Setup)

**Recommended**: Configure persistent authentication via Surround SCM GUI to eliminate repetitive credential parameters.

> 🔴 **CHECKPOINT · 首次凭证配置**：若用户首次使用 sscm（无 `-y`/`-z` 也无 GUI 持久化凭证），**必须暂停**并引导用户完成 GUI 登录（勾选「Always log in」）。这是用户必须亲自操作的步骤，agent 无法代劳。配置完成前所有 `sscm` 命令都会失败。

**Quick setup**:
1. Open Surround SCM Desktop Client (GUI)
2. Connect to server with ✅ "Always log in with this username and password" checked
3. Credentials persist in Windows Credential Manager (encrypted)

**After setup**:
```powershell
# Commands work without -y and -z parameters
sscm lsmainline
sscm ls -b"Project" -p"Project"
```

**Credential setup provides**: 60% code reduction, no passwords in command history, Windows-encrypted storage.

**Detailed setup guide**: See [credential_setup.md](references/credential_setup.md) for complete instructions, troubleshooting, and security notes.

## Quick Start

**Critical**: NO space between flag and value: `-y"user:pass"` NOT `-y "user:pass"`

**Note**: After configuring default credentials (see above), `-y` and `-z` can be omitted from all commands below.

### 1. Discover Project (Progressive)

**Try mainline first** (most projects are mainlines):

```powershell
# With default credentials configured (recommended)
sscm lsmainline | Select-String "keyword"

# Or with explicit credentials
sscm lsmainline -y"user:pass" -z"server:port" | Select-String "keyword"
```

**If not found**, try branch search:

```powershell
# 1. Find parent mainline
sscm lsmainline ... | Select-String "parent_keyword"

# 2. List branches under parent
sscm lsbranch -b"ParentMainline" -p"ParentMainline" ... | Select-String "keyword"
```

**Note**: Each project has unique name, not generic "Mainline".

> 🔴 **CHECKPOINT · 项目确认**：发现候选项目后、执行任何 `sscm get` 之前，**必须**向用户展示命中列表并等待确认。绝不在用户未确认项目名时直接开跑提取（项目名错误会拉错整个仓库）。

**Complex scenarios**: See [branch_workflows.md](references/branch_workflows.md)

### 2. Verify Access (Lightweight)

Quick permission check before large operations:

```powershell
# List top-level only (fast)
sscm ls -b"ProjectName" -p"ProjectName"
# Or with explicit credentials: ... -y"user:pass" -z"server:port"
```

**Error handling**: See [troubleshooting.md](references/troubleshooting.md)

### 3. Extract Files

**Check labels first** (avoid no-label scenarios):

```powershell
sscm lslabel -b"Branch" -p"Parent"
# If returns empty, branch has no labels - will extract current version
```

**Basic extraction**:

```powershell
# Single file
sscm get "file.ext" -b"Project" -p"Project/Path" -d"output" -wreplace

# Small directory extraction
sscm get /SubDir -b"ProjectName" -p"ProjectName" -r -d"$PWD\output" -wreplace

# Specific version
sscm get ... -l"RELEASE_1.0" ...  # By label
sscm get ... -s"2026020100:00:00" ...  # By timestamp
```

**Finding files when user is unsure of location**:

```powershell
# Output to file first (prevents truncation, enables re-search)
sscm ls -b"Project" -p"Project" -r > all_files.txt

Get-Content all_files.txt | Select-String "\.ldf" -CaseSensitive:$false           # case-insensitive
Get-Content all_files.txt | Select-String "\.ldf" -Context 3,0                    # with dir context
```

**⚠️ Large directories & scattered files**:

> 🔴 **CHECKPOINT · 大目录策略**：递归列出文件数 > 200 或目录层级 ≥ 3 时，**必须**切换到模块化分批提取（见下方 ✅ Step 2），禁止对整个 root 直接 `sscm get -r`（会静默跳过子目录）。

Recursive extraction (`-r`) of large directories may **silently skip subdirectories**. Extract by mid-level functional module instead:

```powershell
# ✅ Step 1: Locate all target files
sscm ls -b"Project" -p"Project" -r > all_files.txt
Get-Content all_files.txt | Select-String "\.ldf" -Context 3,0

# ✅ Step 2: Extract by functional module (medium granularity)
sscm get /03_Software/01_Doc -b"Project" -p"Project" -r -d"output"
sscm get /03_Software/02_SW/07_Workspaces/CANoe -b"Project" -p"Project" -r -d"output"
sscm get /03_Software/02_SW/01_Sources -b"Project" -p"Project" -r -d"output"

# ❌ Avoid: entire root (unreliable) or per-file (too many commands)
```

**Verify extraction** (MANDATORY after each operation):

> 🔴 **CHECKPOINT · 提取验证**：每次 `sscm get` 完成后**必须**立即用下方脚本/命令验证文件数与类型，发现缺口前不得进入下一步。验证未通过 → 触发 [失败模式 F2](#failure-modes) 静默跳过修复流程。

```powershell
# Quick inline verification
$files = Get-ChildItem -Path "output_dir" -Recurse -Filter "*.ldf" -File
Write-Host "✅ Extracted: $($files.Count) files" -ForegroundColor Green

# Or use verification script for detailed report (path relative to this skill's scripts/ dir)
python scripts/verify_extraction.py output_dir --expected-exts .c,.h
```

## Failure Modes

> 主文 inline 三段式表 — 不必跳转 troubleshooting.md 即可处理 80% 常见失败。完整诊断见 [troubleshooting.md](references/troubleshooting.md)。

| # | 触发条件 | 一线修复 | 仍失败兜底 |
|---|---------|---------|-----------|
| **F1** | `sscm lsmainline` 返回空 / "Unable to find mainline" | 项目是 branch 不是 mainline → `sscm lsbranch -b"Parent" -p"Parent"` 在 common parents 下找 | 用 `find_project.py "keyword" --test-access` 模糊搜 mainline+branch |
| **F2** | `sscm get -r` 提取数 < `ls` 显示数（**静默跳过子目录**） | 切模块化分批：`sscm get /Module/Sub -r` 按 mid-level 模块逐个提取 | 用 `verify_extraction.py --compare all_files.txt` 定位缺口 → 逐文件 `sscm get "file"` 补齐 |
| **F3** | `security access denied` | 验证用户对该 project 有 read 权限 → 联系 SCM admin | 换已知可访问的项目测试，排除账号问题 |
| **F4** | `Incorrect input format` / flag 报错 | 检查 flag 与值间**无空格**：`-y"u:p"` 而非 `-y "u:p"` | 查 [cli_commands.md](references/cli_commands.md) 核对精确语法 |
| **F5** | `lslabel` 返回空（branch 无 label） | 该 branch 无版本标签 → 提取当前版本，或改用 timestamp `-s"YYYYMMDDHH:MM:SS"` | 问用户目标版本的近似日期，用 timestamp 兜底 |
| **F6** | 提取产物含 `.zip/.7z/.rar` 但解压后内容缺失/损坏 | 重新解压：`Expand-Archive`（zip）/ `7z x`（7z/rar），检查压缩包完整性 | 原始归档可能损坏 → 重新 `sscm get` 该归档文件 |

## Anti-Patterns（不要做什么）

> 危险动作与反模式清单 — 出现以下行为时应立即停止并修正。

| # | ❌ 不要做 | 为什么 | ✅ 应该做 |
|---|----------|--------|----------|
| **AP1** | 在用户未确认项目名时直接 `sscm get` | 项目名错误会拉错整个仓库，浪费时间且污染 output 目录 | 🔴 先展示 `find_project`/`lsmainline` 命中列表，等用户确认 |
| **AP2** | 对整个 root 执行 `sscm get -r`（大目录） | `-r` 会**静默跳过**部分子目录，产物不完整且无报错 | 按模块化分批提取 + 每批 verify |
| **AP3** | flag 与值之间加空格（`-y "u:p"`） | sscm CLI 解析失败，报 `Incorrect input format` | 紧贴：`-y"u:p"`、`-b"Proj"`、`-p"Path"` |
| **AP4** | `get` 完成后跳过验证直接进入下一步 | 静默跳过无法察觉，下游会基于不完整产物工作 | 🔴 每次 get 后立即 verify（count + 类型） |
| **AP5** | 在命令行明文传递密码（`-y"user:pass"`） | 密码进入 shell history、进程列表，有泄露风险 | 优先 GUI 持久化凭证；次选 `sscm_config.json`；明文仅用于一次性脚本 |
| **AP6** | 递归列出全部文件（`ls -r`）当作默认动作 | 大仓库输出截断、context bloat | 仅当用户明确要求 "show all files" / "list structure" 时才 `-r` |
| **AP7** | 假设 label 名存在而不先 `lslabel` 检查 | label 拼错或不存在会导致 `get -l` 失败或拉到错误版本 | 先 `lslabel` 确认，无 label 则走 timestamp 兜底 |

**Deep-dive**: See [best_practices.md](references/best_practices.md) for search strategies, granularity guidelines, and real-world examples.

**Archives**: If extracted files contain .zip/.7z/.rar, decompress automatically. See [best_practices.md](references/best_practices.md) for commands.

**Credentials**: Use default credentials from Windows Credential Manager (configured via GUI). Legacy support: load from `sscm_config.json` or use explicit `-y`/`-z` parameters.

**Default behavior**: Do NOT recursively list all files unless user explicitly requests "show all files" or "list structure".

## Reference Documentation

- **Project discovery**: See [project_discovery.md](references/project_discovery.md) for finding mainlines and branches
- **Label management**: See [label_management.md](references/label_management.md) for version control strategies
- **Branch workflows**: See [branch_workflows.md](references/branch_workflows.md) for complex hierarchies
- **Error handling**: See [troubleshooting.md](references/troubleshooting.md) for comprehensive debugging
- **CLI reference**: See [cli_commands.md](references/cli_commands.md) for complete command syntax

## Scripts

All scripts support `--help` for full usage.

### `scripts/find_project.py` — Project Discovery
```bash
python scripts/find_project.py "10638"                        # Uses GUI persistent credentials
python scripts/find_project.py "Ctrl_AI" --test-access        # Also checks permissions
python scripts/find_project.py "Preh" --credentials config.json  # Explicit credentials
```
Searches mainlines + common parent branches, ranks by relevance, suggests corrections for typos.

### `scripts/parse_sscm_output.py` — Search & Path Reconstruction
```bash
# After: sscm ls -b"Project" -p"Project" -r > all_files.txt
python scripts/parse_sscm_output.py --input all_files.txt --filter-ext ".ldf" --context
python scripts/parse_sscm_output.py --input all_files.txt --regex "config.*\.xml" --format json
python scripts/parse_sscm_output.py --input all_files.txt --format summary
```
Parses `sscm ls -r` output, reconstructs full paths from directory headers, filters by extension/pattern/regex.

### `scripts/verify_extraction.py` — Post-Extraction Verification
```bash
python scripts/verify_extraction.py output_dir --expected-exts .c,.h
python scripts/verify_extraction.py output_dir --compare all_files.txt --expected-exts .ldf
python scripts/verify_extraction.py output_dir --expected-count 200
```
Validates file counts/types, compares against search results to catch silent extraction failures.

## Troubleshooting

**Common issues**: See [troubleshooting.md](references/troubleshooting.md) for comprehensive error handling, authentication issues, extraction problems, and debugging strategies.

**Quick connection test**: `sscm lsmainline` (uses defaults) or `sscm lsmainline -y"user:pass" -z"server:port"` (explicit credentials)

## Best Practices

**Core principles** for reliable extraction:

1. **Output large directory listings to file** - prevents truncation, enables offline analysis
2. **Use modular extraction by functional area** - extract Doc/SW/Test separately, not entire root
3. **Verify extraction immediately** - compare file counts and sizes after each extraction
4. **Use case-insensitive searches** - handles mixed extension cases (.ldf, .LDF)
5. **Search with context** (`-Context 3,0`) - reveals parent directory structure

**Detailed strategies**: See [best_practices.md](references/best_practices.md) for comprehensive search patterns, extraction workflows, verification checklists, and complete real-world examples.

## Progressive Disclosure Pattern

This skill uses a **three-level approach** to minimize context bloat:

1. **Quick check**: Top-level listing only (fast, lightweight)
2. **Targeted search**: PowerShell pipelines for filtering
3. **Full listing**: Recursive `-r` flag (only when explicitly requested)

**Key principle**: Never recursively list files unless user asks for "detailed structure" or "show all files".
