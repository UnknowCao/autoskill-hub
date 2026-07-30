<div align="center">

# 🔧 autoskill-hub

**The open skill repository that walks the entire automotive V-model, mapped to ASPICE.**

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Skills: 4](https://img.shields.io/badge/Skills-4-green.svg)](./skills)
[![skills.sh](https://skills.sh/b/UnknowCao/autoskill-hub)](https://skills.sh/UnknowCao/autoskill-hub)
[![ASPICE](https://img.shields.io/badge/ASPICE-v4.0-orange.svg)](#-v-model--aspice-mapping)
[![ISO 26262](https://img.shields.io/badge/ISO-26262-green.svg)](#-v-model--aspice-mapping)
[![AUTOSAR](https://img.shields.io/badge/AUTOSAR-Classic%20%7C%20Adaptive-blueviolet.svg)](#-v-model--aspice-mapping)
[![Bilingual](https://img.shields.io/badge/docs-EN%20%7C%20%E4%B8%AD%E6%96%87-red.svg)](#-中文简介)

</div>

> From left-wing requirements (SYS.1 / SYS.2) to right-wing verification (SWE.5 / SWE.6),
> every skill targets a specific V-model phase and ASPICE process — turning general-purpose
> LLMs into **process-aware engineering partners** for safety-critical automotive development.

---

## 🚀 Why autoskill-hub?

Automotive development lives and dies by **process**: the V-model defines *what to do when*,
ASPICE defines *how well to do it*, and ISO 26262 defines *how safe to do it*. Yet generic LLMs:

- ❌ Conflate SYS.3 system architecture with SWE.1 software architecture
- ❌ Draft HARA without traceability to safety goals
- ❌ Write unit tests that miss SWE.4 structural coverage intent
- ❌ Produce VCs that paraphrase the requirement instead of being testable
- ❌ Cannot navigate the left↔right wing correspondence of the V

`autoskill-hub` fixes this. Every skill is **anchored to a V-model phase and an ASPICE process
reference** — so the AI always knows *where it is* in the lifecycle and *what artifacts must
connect* upstream/downstream.

## 📐 V-Model × ASPICE Mapping

```
    Left Wing (Design ↓)              Right Wing (Verification ↑)
    ─────────────────────             ─────────────────────────
    SYS.1  Stakeholder Req.   ←→     SYS.5  System Verification
    SYS.2  System Req.        ←→     (acceptance criteria / VC)
    SYS.3  System Architecture←→     SWE.6  Software Verification
    SWE.1  Software Req.      ←→
    SWE.2  Software Architecture←→   SWE.5  Software Integration
    SWE.3  Software Detailed Design→  SWE.4  Unit Verification
                       │
                       ▼
                   Implementation (SWE.4 / coding)
```

## 📦 Skill Catalog

| Skill | V-Model Phase | ASPICE | What it does |
|---|---|---|---|
| 🎯 [**verification-criteria**](./skills/verification-criteria/) | SYS.2 / SYS.5 / SWE.1 / SWE.6 | **SYS.2 BP5** · SYS.5 · SWE.6 | Generate, audit, and trace Verification Criteria; VC-First + SMARTR-OC + Source Depth + 100 % coverage |
| 📜 [**patent-forge**](./skills/patent-forge/) | Cross-cutting (IP / SUP.10) | **SUP.10** · CNIPA 专利法 26 条 · 审查指南 2023 | Draft Chinese patent documents — 专利申请表 (filing-ready) / 技术交底书 (for patent agents); 4-phase workflow with prior-art search, 禁用词 gate, ACIP .docx fill |
| 🎨 [**patent-figforge**](./skills/patent-figforge/) | Cross-cutting (IP / SUP.10) | **SUP.10** · CNIPA / USPTO / EPO filing | Generate patent-style technical diagrams (flowcharts / block diagrams / system architectures) with automatic reference numbering; dual SVG+PNG output, CJK auto-resolution |
| 📄 [**markitdown-enhanced**](./skills/markitdown-enhanced/) | Cross-cutting (toolchain / SUP.8) | **SUP.8** Configuration Mgmt · **SUP.10** · document work-product intake | Convert any office/document file (DOCX / PDF / PPTX / XLSX / HTML / CSV / JSON / …) to clean, LLM-ready Markdown with auto XLSX-formula eval, formula-escaping fix, two-stage table auto-repair, and encrypted-file decryption; single-file / parallel batch / size-aware resumable batch |
| _More skills coming soon_ | — | — | _Requirements authoring, HARA, AUTOSAR, OEM standards forensics…_ |

> Want a skill that's not listed? Open an [issue](https://github.com/UnknowCao/autoskill-hub/issues)
> with your V-model phase + ASPICE process — contributions are welcome.

## ✨ Highlights

- ✅ **V-model native** — every skill declares which wing & phase it serves
- ✅ **ASPICE-anchored** — skills map to specific process references (BP / GP / WP)
- ✅ **Traceability-first** — left↔right wing correspondence enforced by design
- ✅ **Framework-agnostic** — works with Claude Code, GitHub Copilot, Cursor, Continue, or any agent that reads `SKILL.md`
- ✅ **Domain-agnostic** — applicable to any vehicle electronic domain (powertrain, body, chassis, ADAS…)
- ✅ **Battle-tested** — every skill ships with lint checks, test prompts, and verification gates
- ✅ **Bilingual** — English + 中文 documentation for global teams

## 📥 Install / Use a Skill

Each skill is a self-contained folder with a `SKILL.md` entry point. Pick one and load it
into your agent — no build step, no dependencies.

### Via skills.sh CLI (recommended)

Install a single skill:

```bash
npx skills add UnknowCao/autoskill-hub@verification-criteria
npx skills add UnknowCao/autoskill-hub@patent-forge
npx skills add UnknowCao/autoskill-hub@patent-figforge
npx skills add UnknowCao/autoskill-hub@markitdown-enhanced
```

Or install all three in one shot:

```bash
npx skills add UnknowCao/autoskill-hub
```

### Manual install

**Claude Code / Cursor / Continue** — copy or symlink the skill folder into your agent's
skills directory:

```bash
git clone https://github.com/UnknowCao/autoskill-hub.git
# then point your agent at autoskill-hub/skills/<skill-name>/SKILL.md
```

**GitHub Copilot** — reference the `SKILL.md` from your `.github/copilot-instructions.md`
or workspace instructions.

Then just ask in natural language — each skill auto-routes based on keywords. Example:

```
为 BMS_System_Requirements.md 生成验证标准（verification-criteria skill 自动激活）

把这个 AR 手势识别方案写成华进 ACIP 交底书（patent-forge skill 自动激活）

给这个 BMS 均衡方法画一张方法流程图和系统框图，带参考标号（patent-figforge skill 自动激活）
```

## 🤝 Contributing

PRs welcome. New skills **must declare** their V-model phase + ASPICE process reference in
the `SKILL.md` frontmatter. See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the skill spec,
frontmatter conventions, and review checklist.

By submitting a PR you agree to license your contribution under the project's
[Apache-2.0 license](./LICENSE).

## 📜 License

Licensed under the **Apache License 2.0** — see [`LICENSE`](./LICENSE). Includes an explicit
patent grant and NOTICE protection, suitable for commercial use inside OEMs and Tier 1s.

## 🙏 Acknowledgements

Built by hands-on automotive systems engineers. Inspired by the real pain of watching
generic LLMs hallucinate on AUTOSAR layering, confuse ASIL levels, and invent OEM norm numbers.

If `autoskill-hub` saves your team hours, please ⭐ the repo and share it with a colleague
who still writes VCs by hand.

---

<div align="center">

## 🌐 中文简介

</div>

`autoskill-hub` 是一个围绕**汽车 V 模型全生命周期**与 **ASPICE 过程模型**组织的开源 AI Skill 仓库。

**核心理念**：汽车电子开发成败在**流程**——V 模型规定"何时做什么"，ASPICE 规定"做到什么程度"，
ISO 26262 规定"做到多安全"。然而通用 LLM 经常混淆 SYS.3 系统架构与 SWE.1 软件架构、写 HARA 却
接不上安全目标、做单元测试却丢掉 SWE.4 结构覆盖意图、生成的 VC 只是把需求复述一遍。

本仓库的每一个 skill 都**锚定到一个 V 模型阶段 + 一个 ASPICE 过程引用**——让 AI 始终清楚自己在
生命周期中的位置，以及上下游必须衔接哪些工作产物。

**覆盖范围**：
- **左翼（设计↓）**：SYS.1/SYS.2 需求 → SYS.3/SYS.4 架构 → SWE.1/SWE.2/SWE.3 软件设计
- **右翼（验证↑）**：SWE.4 单元 → SWE.5 集成 → SYS.5/SWE.6 系统验收
- **横切**：ISO 26262 功能安全、MAN.x 管理过程、SUP.x 支持过程、**知识产权产出**（`patent-forge` 专利文档撰写 + `patent-figforge` 专利附图生成，对齐 SUP.10 变更/配置管理之外的 IP 产出）
- **全程**：左右翼追溯关系、验证标准（VC）、安全案例（Safety Case）

> 已收录的 4 个 skill：🎯 `verification-criteria`（VC 生成/审核/覆盖追溯）· 📜 `patent-forge`（中国专利申请表/技术交底书撰写）· 🎨 `patent-figforge`（专利附图生成）· 📄 `markitdown-enhanced`（任意办公/文档文件转 LLM 可用 Markdown，带 XLSX 公式求值、公式转义修复、两阶段表格自动修复、加密文件解密）。其余方向（需求撰写、HARA、AUTOSAR、OEM 标准取证）陆续上线，欢迎在 [issue](https://github.com/UnknowCao/autoskill-hub/issues) 提需求。

**适合谁？** 系统工程师、软件架构师、功能安全经理、需求工程师、测试工程师、ASPICE 评估协调人，
以及任何想把 AI 变成"懂流程"的开发搭档的从业者。

---

<div align="center">

<sub>Built with ❤️ for automotive engineers who care about process.</sub>

</div>
