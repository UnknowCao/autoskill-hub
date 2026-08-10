<sub>🌐 <a href="README.md">中文</a> · <b>English</b></sub>

<div align="center">

# 🎨 Patent FigForge

> *"What you render is what the examiner accepts — or it doesn't leave the gate."*

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-patent--figforge-blueviolet)](SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Darwin Verified](https://img.shields.io/badge/Darwin%20Verified-85.8%2F100-brightgreen)](results.tsv)
[![Output](https://img.shields.io/badge/Output-SVG%20%2B%20PNG%20dual-green.svg)](#)
[![CJK](https://img.shields.io/badge/CJK-SimHei%20auto-red.svg)](#)
[![Filing](https://img.shields.io/badge/Filing-CNIPA%20%7C%20USPTO%20%7C%20EPO-blue.svg)](#)

**Turn any LLM agent into a patent diagram generator that refuses to ship non-compliant figures — 3 mandatory GATEs block bad output before you ever see it.**

[See It](#-see-it) · [Install](#-quick-start) · [Triggers](#-triggers) · [vs Alternatives](#-vs-alternatives) · [Security](#-security-boundary)

</div>

---

<p align="center">
  <img src="assets/showcase/hero-comparison.png" alt="Before/After: raw graphviz vs patent-figforge" width="100%">
  <sub><i>Same prompt. Left: a generic agent output — colored fills, Chinese tofu (□□□), curved splines, crossing lead lines. Instant examiner rejection. Right: patent-figforge — B&W, SimHei-rendered Chinese, polyline routing, CNIPA §Part 1 Chapter 1 compliant.</i></sub>
</p>

---

## 💡 The Problem It Solves

Here's what happens: you ask an agent to draw a patent figure. The agent happily produces a diagram — green fills for "normal", red borders for "warning", blue modules for "communication", Chinese characters rendered as □□□, edges curved and overlapping, reference numbers either missing or scattered.

It looks pretty. The examiner disagrees.

**37 CFR §1.84(a)(1) says: black ink on white.** CNIPA examination guidelines say: sharp-rectangle block diagrams, no crossing lead lines, text ≥ 14pt. A generic agent knows none of this — it just translates "draw a diagram" into the fanciest picture it's seen.

**patent-figforge takes a different approach: don't trust the agent's taste.** It hard-codes B&W compliance into the Graphviz rendering pipeline (`bgcolor="white"`, `fillcolor="white"`), enforces polyline orthogonal routing (no ortho, no curved), auto-resolves CJK fonts (SimHei → no more □□□), then runs **3 mandatory GATEs** before declaring the figure done — file existence check → Chinese rendering verification → final visual human confirmation. **Fail one GATE, and the figure doesn't ship.**

Supports **method flowcharts** (method claims), **system block diagrams** (system claims), and **custom DOT rendering** (architectures). Every render automatically produces **dual SVG + PNG** output.

---

## 📸 See It

### Method Flowchart

<p align="center">
  <img src="assets/showcase/bms-method-flowchart.png" alt="BMS method flowchart" width="70%">
</p>

> BMS overvoltage protection method: Start(10) → Sample(20) → Decide(30) → Protect(40) → End(50). Loop-back edge uses `constraint="false"` — no crossing.

### System Block Diagram

<p align="center">
  <img src="assets/showcase/bms-block-diagram.png" alt="BMS system block diagram" width="70%">
</p>

> BMS system: Voltage Acquisition(10) → Main MCU(20) → Communication(30) / Balancing Driver(40). rankdir=LR, 4 independent reference numbers, black-on-white.

---

## 🚀 Quick Start

### 1. Install Graphviz

```bash
# Windows:  choco install graphviz
# Linux:    sudo apt install graphviz
# Mac:      brew install graphviz
```

```bash
pip install graphviz
```

### 2. Drop the skill into your skills directory

```
skills/patent-figforge/
├── SKILL.md
├── python/diagram_generator.py
├── references/compliance.md
└── test-prompts.json
```

### 3. Talk to your agent

```text
Draw a BMS system block diagram: voltage acquisition → MCU →
communication module / balancing driver. Black-on-white,
with patent reference numbers (10/20/30/40), for CNIPA filing.
```

> **First prompt after install** (copy-paste ready):
>
> ```text
> Use patent-figforge to draw a patent figure: I'm filing a patent for
> a battery management system with sampling, overvoltage detection,
> and protection steps. Add reference numbers to each step. Output SVG.
> ```

---

## 🗣️ Triggers

Any of these will invoke patent-figforge:

- "Draw a patent method flowchart"
- "Generate a BMS block diagram for CNIPA filing"
- "Create a patent figure with reference numbers for this claim"
- "Generate a USPTO-compliant system architecture diagram"
- "专利附图、流程图、框图、架构图"
- "patent figures, reference numbers, 专利图"

---

## 📦 What It Delivers

| Input | Deliverable | Typical Time |
|---|---|---|
| Method step descriptions | `.svg` flowchart (TB, top-down) + `.png` copy | < 5 sec |
| System module list + connections | `.svg` block diagram (LR, left-right) + `.png` copy | < 5 sec |
| Raw DOT source code | `.svg` + `.png` dual output (dot/neato/fdp/circo/twopi) | < 5 sec |
| Template name (e.g. `component_hierarchy`) | Custom diagram generated from template | < 10 sec |

**Every figure automatically includes**: B&W compliant styling, SimHei Chinese (no tofu), polyline orthogonal routing, patent reference numbers (10/20/30 primary, 12/14/16 secondary), 3-GATE verification pass record.

---

## ⚔️ vs Alternatives

| Dimension | Generic approach (Mermaid / raw Graphviz) | patent-figforge |
|---|---|---|
| Color | 🟢🔵🔴 Colored fills | ⬛⬜ B&W only, hard-coded enforcement |
| CJK text | □□□ tofu / ??? garbage | SimHei auto-resolution, 3-platform fallback chain |
| Compliance check | ❌ None — won't know the figure is bad | ✅ 3 mandatory GATEs, fail one = not done |
| Reference numbers | Manually added text, lead lines everywhere | `ref=20` parameter, auto-appends `(20)` suffix |
| Edge routing | ortho drops labels / curved is irreproducible | `splines=polyline` hard-coded, labels preserved |
| Failure diagnosis | "Wrong? Redraw." | 8 failure modes + 10 anti-patterns table — know why it broke and how to fix |
| Focus | General-purpose diagramming tool | **Patent figures only** — no UI mockups, no architecture doodles |

> 8-competitor deep-dive: RobThePCGuy (167⭐ superset), PatentFig.ai (commercial SaaS), kimlawtech (KIPO-specialized), Hallmark (65-gate branding), handsomestWei (4.6k⭐ disclosure skill), and more — see the Luban audit report.

---

## 🛡️ Security Boundary

**What this skill will NOT do:**
- ❌ Delete, move, or modify any files outside its `output_dir`
- ❌ Make outbound network requests (all rendering is local Graphviz)
- ❌ Execute shell commands beyond `dot` rendering
- ❌ Auto-generate additional figures or modify claim text without confirmation (🛑 STOP gate)
- ❌ Read or transmit your patent disclosure content

**When it will stop and ask:**
- 🔴 GATE 1: Before rendering non-trivial structures (≥8 nodes, decision branches, loop-back edges)
- 🔴 GATE 3: When visual inspection fails (tofu/crossing/color detected)
- 🛑 STOP: After presenting each verified figure — no auto-generation of additional figures

---

## 📁 File Structure

```
patent-figforge/
├── SKILL.md                  # Entry point — agent loads this first
├── README.md                 # 中文 README
├── README.en.md              # You're reading this
├── LICENSE                   # MIT
├── test-prompts.json         # 8 test prompts (Darwin-verified, 6/8 full_test)
├── results.tsv               # Darwin optimization log (6 rounds, 79.6→85.8)
├── .claude-plugin/
│   └── marketplace.json      # Claude Code plugin marketplace registration
├── python/
│   └── diagram_generator.py  # Self-locating PatentDiagramGenerator (323 lines)
├── references/
│   └── compliance.md         # 8 failure modes + 10 anti-patterns + legal basis
├── scripts/
│   └── generate_showcase.py  # Reproducible showcase image generator
├── assets/
│   └── showcase/             # Hero comparison + sample output images
└── examples/                 # Real output samples + usage guide
```

---

## 🧪 Verified Test Coverage

Darwin Skill 2.0 evaluation: 8 prompts, 6 full_test runs:

| Prompt | Baseline | With Skill | Δ |
|---|---|---|---|
| P1 BMS method flowchart | 5 | 8 | +3 |
| P2 CNIPA block diagram | 5 | 9 | +4 |
| P5 Anti-pattern prevention | 3 | 9 | +6 |
| P6 Multi-figure split recommendation | 4 | 8 | +4 |
| P8 Chinese tofu fix | 6 | 8 | +2 |

**Darwin Score: 85.8/100** (6-round optimization log in `results.tsv`)

### Try It Yourself

```text
Draw a BMS system block diagram with: green fill for voltage acquisition
(normal), red border for overvoltage protection (warning), blue for
communication module. Use ortho routing. Add ✓ checkmarks for implemented
status on each module.
```

> **Expected behavior**: The skill intercepts all 5 violations (3 color→B&W, ortho→polyline, ✓→text "已实现") and delivers a compliant B&W figure.

---

## 🙏 Acknowledgements

This skill is a compliance-hardened fork of the `patent-diagram-generator` sub-module from [RobThePCGuy/Claude-Patent-Creator](https://github.com/RobThePCGuy/Claude-Patent-Creator) (167⭐, MIT). Upstream provided the solid Graphviz Python API design and reference-number injection logic. Key additions in this fork: 3 compliance GATEs, CJK font auto-resolution, 8+10 failure/anti-pattern diagnostic tables, dual SVG+PNG output. Upstream attribution retained per MIT license.

Inspired by peer projects: [kimlawtech/korean-patent-diagram](https://github.com/kimlawtech/korean-patent-diagram) (KIPO compliance table design), [PatentFig.ai](https://patentfig.ai/) (compliance checker productization), [Hallmark](https://github.com/nutlope/hallmark) (65-gate branding approach).

---

<p align="center">
  <sub>Made with 🔨 by 鲁班工坊 · <a href="https://github.com/alchaincyf/patent-figforge">GitHub</a></sub>
</p>
