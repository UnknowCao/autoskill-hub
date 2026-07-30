# 📄 MarkItDown-Enhanced

> **Production-ready AI skill that converts *any* office/document file to clean, LLM-ready Markdown — with baked-in fixes for the defects that break RAG pipelines.**
> Enhanced on top of **Microsoft MarkItDown 0.1.5**, with encrypted-file decryption, XLSX formula evaluation, formula-escaping fix and two-stage table-structure auto-repair.

<p align="center">
  <strong>
    <a href="#-quick-start">Quick Start</a> ·
    <a href="#-enhancement-pipeline">Enhancement Pipeline</a> ·
    <a href="#-v-model--aspice-mapping">V-Model Mapping</a> ·
    <a href="#-file-structure">Structure</a>
  </strong>
</p>

<p align="center">
  <img alt="License: Apache-2.0" src="https://img.shields.io/badge/License-Apache_2.0-blue.svg">
  <img alt="Base" src="https://img.shields.io/badge/markitdown-0.1.5-blue.svg">
  <img alt="Languages" src="https://img.shields.io/badge/docs-EN%20%7C%20%E4%B8%AD%E6%96%87-red.svg">
  <img alt="LLM-Agent" src="https://img.shields.io/badge/Agent-SKILL.md-purple.svg">
  <img alt="Formats" src="https://img.shields.io/badge/formats-DOCX%20%7C%20PDF%20%7C%20PPTX%20%7C%20XLSX%20%7C%20HTML%20%7C%20CSV%20%7C%20%E2%80%A6-green.svg">
</p>

---

## English Description

**`markitdown-enhanced`** is a framework-agnostic AI skill (a self-contained `SKILL.md` + reference docs & Python scripts) that turns any LLM agent — Claude Code, GitHub Copilot, Cursor — into a **reliable document-to-Markdown converter**. It enhances Microsoft MarkItDown with robustness fixes that matter for downstream LLM/RAG use.

It solves the most common failure modes in AI-assisted document conversion: **formula cells exported as `NaN`** (XLSX written without a cached `<v>`), **KaTeX-breaking escapes** (`$...$` math turned into `\* \_ \^`), **mangled table structures** (rowspan/colspan collapses that leave silent data corruption), and **encrypted files that silently fail or leak the password into chat**. This skill automates all of these as silent pipeline stages, with a hard **AUTO-FIX POLICY** — known defects are fixed without asking, unknown defects best-effort fix when ground-truth HTML exists, and only a genuinely un-inferrable case ever stops to ask.

It supports **single-file**, **parallel batch**, and **size-aware resumable batch** for large file sets / network drives (thousands of files via background VS Code tasks). Encrypted `docx/xlsx/pptx` are decrypted through the native Windows CredUI dialog or `keyring` — the password never touches AI chat history.

---

## 🌐 中文简介

**`markitdown-enhanced`** 是一个**框架无关**的 AI Skill —— 把一份 `SKILL.md` + 配套参考文档与 Python 脚本加载进任意 LLM Agent（Claude Code / GitHub Copilot / Cursor 等能读 Markdown 的都行），让大模型真正把**任意办公/文档文件可靠地转换成干净的、可喂给 LLM/RAG 的 Markdown**。它在 Microsoft MarkItDown 0.1.5 基础上做了针对性增强。

它解决的是 AI 辅助文档转换最常见的失败模式：**公式单元格导出成 `NaN`**（用 openpyxl 生成的 XLSX 没缓存 `<v>`）、**KaTeX 解析报错**（`$...$` 数学段被错误转义成 `\* \_ \^`）、**表格结构损坏**（rowspan/colspan 坍缩造成静默数据丢失）、以及**加密文件要么静默失败、要么把密码泄露进对话**。本 skill 把这些问题全部做成**静默的管道阶段**，并执行强制的 AUTO-FIX 策略——已知缺陷无需询问直接修、未知但可推断的尽力修、只有真正无法推断的结构才会停下来问。

支持**单文件**、**并行批量**、以及面向大批量/网络盘的**断点续传批量**（通过 VS Code 后台任务跑几千个文件）。加密的 docx/xlsx/pptx 通过 Windows 原生 CredUI 对话框或 `keyring` 解密——密码绝不进入 AI 对话历史。

---

## 🗺️ V-Model × ASPICE Mapping

| Field | Value |
|---|---|
| V-Model Wing | cross_cutting |
| V-Model Phase | Cross-cutting — feeds every left-wing (SYS.1 / SYS.2 / SWE.1..3) and right-wing (SWE.4 / SWE.5 / SYS.5) phase that consumes source documents |
| ASPICE Process | **SUP.8** Configuration Management (work-product normalization) · **SUP.10** Change Management · serves **ACQ.4 / SUP.1** supplier work-product intake |
| ISO 26262 Clause (optional) | Part 8 §11 (configuration items: documentation artifacts) — document-to-Markdown is a CM enabler |
| Traceability | upstream: standards / OEM SOR / supplier DOCX-XLSX-PDF / DOORS exports (any office format) · downstream: LLM-readable Markdown for requirements analysis, VC generation, SDD authoring, test design |

> This is a **toolchain skill**, not a single V-model phase. It normalizes heterogeneous engineering documents (standards packs, supplier SORs, test specs, reviewed DOCX/XLSX) into the canonical Markdown that downstream `autoskill-hub` skills (`verification-criteria`, `automotive-sdd`, …) consume. Without it, DOCX tables collapse, XLSX formulas go `NaN`, and encrypted supplier files block the pipeline.

---

## ✨ Key Features

- ✅ **Auto-formula-evaluation** — pre-evaluates every XLSX formula cell with pure-Python `formulas` and writes results back into `<v>`, so `=A2+B2` exports a real number, not `NaN`
- ✅ **Formula-escaping fix (D1)** — strips the broken `\* \_ \^` escapes inside `$...$` math segments that MarkItDown 0.1.6 emits, so KaTeX no longer fails
- ✅ **Two-stage table auto-repair** — Stage 1 Python script detects vertical-merge (D2) / nested-table collapse against mammoth's HTML ground truth and emits a precise sidecar; Stage 2 agent fixes the `.md` **silently** per the AUTO-FIX POLICY
- ✅ **Encrypted-file handling** — detects password-protected `docx/xlsx/pptx`; resolves credentials via `keyring` first, then the native Windows **CredUI dialog** (desktop) or a one-line `keyring.set_password` (CI/headless). Password never touches chat/logs/disk
- ✅ **Metadata header** — every `.md` gets a `# Title` / `**Source**` / `**Format**` head, injected before table-detect so sidecar line numbers stay valid
- ✅ **Three execution modes** — single-file (`_convert_core.py`), parallel batch (`batch_convert.py`), and size-aware resumable batch (`batch_convert_dynamic.py` for thousands of files / network drives with per-file subprocess isolation, dynamic timeouts, heavy-file concurrency cap)
- ✅ **Zero-leak anti-pattern list** — 13 hard-coded "Do NOT" rules: never `cmdkey`/Credential Manager GUI for passwords, never type passwords into chat, never repad columns heuristically, never run the dynamic batch in the foreground, …

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install "markitdown[all]" msoffcrypto-tool keyring mammoth pywin32
# For XLSX formula evaluation (recommended):
pip install formulas
```

### 2. Load the skill into your agent

**Claude Code / Cursor / Copilot** — copy this folder into your agent's skills directory, or point the agent at `SKILL.md`. The skill auto-routes on keywords like *convert / 转换 / docx 转 md / 文档提取 / 批量转换*.

### 3. Single file — just ask

```
把这个 docx 技术文件转成 markdown：input.docx
```

The agent runs the full enhancement pipeline (encryption → formula eval → conversion → formula escape fix → table detect → metadata header) and returns a one-line summary. Table errors are auto-fixed silently — no per-table prompts.

### 4. Command-line (when you want to run it yourself)

```bash
# Single file (exit 0 clean; exit 1 = table errors detected → AI auto-fixes)
python scripts/_convert_core.py document.docx -o output.md

# Parallel batch of a directory
python scripts/batch_convert.py input_dir/ output_dir/ --extensions .docx --workers 4

# Large set / network drive — run as a background VS Code task, NOT foreground
python scripts/batch_convert_dynamic.py --source standards_dir/ --recursive \
    --outdir output_md/ --workers 13 --heavy-max 3
```

> ⚠️ For large sets, `batch_convert_dynamic.py` **must** run as a *background VS Code task* (`isBackground: true`) and be polled with `get_task_output`. See the `⛔ Do NOT` section in [`SKILL.md`](./SKILL.md) (row 12) — a foreground run wedges the session.

---

## 🔧 Enhancement Pipeline

Every conversion runs three stages automatically (no flags needed):

| Stage | What happens |
|---|---|
| **1. Pre-conversion** | Detect encrypted files; resolve credentials; **evaluate XLSX formulas** |
| **2. Conversion** | Standard markitdown `docx/pdf/pptx/xlsx/... → md` |
| **3. Post-conversion** | (a) prepend Metadata Header → (b) Formula-escaping fix → (c) Table structure validation (sidecar written, exit code 1) |

Pipeline order matters: the Metadata Header is injected **before** table-detect so the sidecar's absolute line numbers match the final written file (see `⛔ Do NOT` row 6).

### AUTO-FIX POLICY (default = fully automatic)

| Case | Trigger | Action |
|---|---|---|
| **Known defect** (D2 / D6 / nested / D3 / D4) | sidecar `Fixable by AI: YES` (or `LLM-describe`) | Fix **silently**, mark with `<!-- AI-corrected -->` / `<!-- AI-describe -->` blockquote, delete sidecar, one-line summary |
| **Unknown defect, has `HTML_REFERENCE`** | `CAUSE` not in the known set, but HTML ground truth usable | Best-effort fix **silently**, mark `<!-- AI-uncertain: verify -->`, surface in the end summary |
| **Unknown defect, NO `HTML_REFERENCE`** | sidecar missing/corrupt, structure not safely inferrable | 🔴 STOP — the *only* case that prompts the user |

See the full `Stage 2 — AI Correction Flow` and the 13-row anti-pattern list in [`SKILL.md`](./SKILL.md).

---

## 🗂️ File Structure

```
markitdown-enhanced/
├── SKILL.md                       # Entry point — agent loads this
├── README.md                      # You are here
├── test-prompts.json              # 15 regression prompts (happy / encrypted / batch / dynamic)
├── assets/
│   └── example_usage.md           # Practical markitdown usage examples
├── references/
│   ├── api_reference.md           # MarkItDown Python API reference
│   └── file_formats.md            # Per-format capabilities & limitations
└── scripts/
    ├── _convert_core.py           # Single-file entry — full enhancement pipeline
    ├── _decrypt.py                # Encrypted-file detection + keyring/CredUI decryption
    ├── _table_detect.py           # Stage-1 table structure detector (mammoth HTML ground truth)
    ├── _xlsx_formula_eval.py      # XLSX formula pre-evaluation (NaN → real value)
    ├── fix_formula_escaping.py    # Standalone $...$ escape repair
    ├── batch_convert.py           # Parallel batch (ThreadPoolExecutor)
    ├── batch_convert_dynamic.py   # Size-aware resumable batch (subprocess isolation, large sets)
    ├── convert_single_enhanced.py # Legacy single-file CLI wrapper
    ├── convert_literature.py      # Literature-review pipeline helper
    ├── convert_with_ai.py         # AI image-description pipeline helper
    ├── generate_schematic.py      # Static schematic helper
    └── generate_schematic_ai.py   # AI-assisted schematic helper
```

---

## 📄 License

This skill is licensed under the repo's **Apache License 2.0** — see [`../../LICENSE`](../../LICENSE).
`markitdown` is © Microsoft under the MIT license; this skill is an independent enhancement layer on top of it.
