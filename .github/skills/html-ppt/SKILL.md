---
name: html-ppt
description: HTML PPT Studio — author professional static HTML presentations in many styles, layouts, and animations, all driven by templates. Use when the user asks for a presentation, PPT, slides, keynote, deck, slideshow, "幻灯片", "演讲稿", "做一份 PPT", "做一份 slides", a reveal-style HTML deck, a 小红书 图文, or any kind of multi-slide pitch/report/sharing document that should look tasteful and be usable with keyboard navigation. Triggers include keywords like "presentation", "ppt", "slides", "deck", "keynote", "reveal", "slideshow", "幻灯片", "演讲稿", "分享稿", "小红书图文", "talk slides", "pitch deck", "tech sharing", "technical presentation".
---

# html-ppt — HTML PPT Studio

Author professional HTML presentations as static files. One theme file = one
look. One layout file = one page type. One animation class = one entry effect.
All pages share a token-based design system in `assets/base.css`.

## Install

```bash
npx skills add https://github.com/lewislulu/html-ppt-skill
```

One command, no build. Pure static HTML/CSS/JS with only CDN webfonts.

## What the skill gives you

- **36 themes** (`assets/themes/*.css`) — minimal-white, editorial-serif, soft-pastel, sharp-mono, arctic-cool, sunset-warm, catppuccin-latte/mocha, dracula, tokyo-night, nord, solarized-light, gruvbox-dark, rose-pine, neo-brutalism, glassmorphism, bauhaus, swiss-grid, terminal-green, xiaohongshu-white, rainbow-gradient, aurora, blueprint, memphis-pop, cyberpunk-neon, y2k-chrome, retro-tv, japanese-minimal, vaporwave, midcentury, corporate-clean, academic-paper, news-broadcast, pitch-deck-vc, magazine-bold, engineering-whiteprint
- **15 full-deck templates** (`templates/full-decks/<name>/`) — complete multi-slide decks with scoped `.tpl-<name>` CSS. 8 extracted from real-world decks (xhs-white-editorial, graphify-dark-graph, knowledge-arch-blueprint, hermes-cyber-terminal, obsidian-claude-gradient, testing-safety-alert, xhs-pastel-card, dir-key-nav-minimal), 7 scenario scaffolds (pitch-deck, product-launch, tech-sharing, weekly-report, xhs-post 3:4, course-module, **presenter-mode-reveal** — 演讲者模式专用)
- **31 layouts** (`templates/single-page/*.html`) with realistic demo data
- **27 CSS animations** (`assets/animations/animations.css`) via `data-anim`
- **20 canvas FX animations** (`assets/animations/fx/*.js`) via `data-fx` — particle-burst, confetti-cannon, firework, starfield, matrix-rain, knowledge-graph (force-directed), neural-net (pulses), constellation, orbit-ring, galaxy-swirl, word-cascade, letter-explode, chain-react, magnetic-field, data-stream, gradient-blob, sparkle-trail, shockwave, typewriter-multi, counter-explosion
- **Keyboard runtime** (`assets/runtime.js`) — arrows, T (theme), A (anim), F/O, **S (presenter mode: magnetic-card popup with CURRENT / NEXT / SCRIPT / TIMER cards)**, N (notes drawer), R (reset timer in presenter)
- **FX runtime** (`assets/animations/fx-runtime.js`) — auto-inits `[data-fx]` on slide enter, cleans up on leave
- **Showcase decks** for themes / layouts / animations / full-decks gallery
- **Headless Chrome render script** for PNG export

## When to use

Use when the user asks for any kind of slide-based output or wants to turn
text/notes into a presentable deck. Prefer this over building from scratch.

### 🎤 Presenter Mode (演讲者模式 + 逐字稿)

If the user mentions any of: **演讲 / 分享 / 讲稿 / 逐字稿 / speaker notes / presenter view / 演讲者视图 / 提词器**, or says things like "我要去给团队讲 xxx", "要做一场技术分享", "怕讲不流畅", "想要一份带逐字稿的 PPT" — **use the `presenter-mode-reveal` full-deck template** and write 150–300 words of 逐字稿 in each slide's `<aside class="notes">`.

See [references/presenter-mode.md](references/presenter-mode.md) for the full authoring guide including the 3 rules of speaker script writing:
1. **不是讲稿，是提示信号** — 加粗核心词 + 过渡句独立成段
2. **每页 150–300 字** — 2–3 分钟/页的节奏
3. **用口语，不用书面语** — "因此"→"所以"，"该方案"→"这个方案"

All full-deck templates support the S key presenter mode (it's built into `runtime.js`). **S opens a new popup window with 4 magnetic cards**:
- 🔵 **CURRENT** — pixel-perfect iframe preview of the current slide
- 🟣 **NEXT** — pixel-perfect iframe preview of the next slide
- 🟠 **SPEAKER SCRIPT** — large-font 逐字稿 (scrollable)
- 🟢 **TIMER** — elapsed time + slide counter + prev/next/reset buttons

Each card is **draggable by its header** and **resizable by the bottom-right corner handle**. Card positions/sizes persist to `localStorage` per deck. A "Reset layout" button restores the default arrangement.

**Why the previews are pixel-perfect**: each preview is an `<iframe>` that loads the actual deck HTML with a `?preview=N` query param; `runtime.js` detects this and renders only slide N with no chrome. So the preview uses the **same CSS, theme, fonts, and viewport as the audience view** — colors and layout are guaranteed identical.

**Smooth navigation**: on slide change, the presenter window sends `postMessage({type:'preview-goto', idx:N})` to each iframe. The iframe just toggles `.is-active` between slides — **no reload, no flicker**. The two windows also stay in sync via `BroadcastChannel`.

Only `presenter-mode-reveal` is designed from the ground up around the feature with proper example 逐字稿 on every slide.

Keyboard in presenter window: `← →` navigate (syncs audience) · `R` reset timer · `Esc` close popup.
Keyboard in audience window: `S` open presenter · `T` cycle theme · `← →` navigate (syncs presenter) · `F` fullscreen · `O` overview.

## Before you author anything — ALWAYS ask or recommend

**🔴 CHECKPOINT · 🛑 STOP: Do not start writing slides until you understand three things.**
Either ask the user directly, or — if they already handed you rich content — propose a
tasteful default and confirm.

1. **Content & audience.** What's the deck about, how many slides, who's
   watching (engineers / execs / 小红书读者 / 学生 / VC)?
2. **Style / theme.** Which of the 36 themes fits? If unsure, recommend 2-3
   candidates based on tone:
   - Business / investor pitch → `pitch-deck-vc`, `corporate-clean`, `swiss-grid`
   - Tech sharing / engineering → `tokyo-night`, `dracula`, `catppuccin-mocha`,
     `terminal-green`, `blueprint`
   - 小红书图文 → `xiaohongshu-white`, `soft-pastel`, `rainbow-gradient`,
     `magazine-bold`
   - Academic / report → `academic-paper`, `editorial-serif`, `minimal-white`
   - Edgy / cyber / launch → `cyberpunk-neon`, `vaporwave`, `y2k-chrome`,
     `neo-brutalism`
3. **Starting point.** One of the 14 full-deck templates, or scratch? Point
   to the closest `templates/full-decks/<name>/` and ask if it fits. If the
   user's content suggests something obvious (e.g. "我要做产品发布会" →
   `product-launch`), propose it confidently instead of asking blindly.

A good opening message looks like:

> 我可以给你做这份 PPT！先确认三件事：
> 1. 大致内容 / 页数 / 观众是谁？
> 2. 风格偏好？我建议从这 3 个主题里选一个：`tokyo-night`（技术分享默认好看）、`xiaohongshu-white`（小红书风）、`corporate-clean`（正式汇报）。
> 3. 要不要用我现成的 `tech-sharing` 全 deck 模板打底？

**🔴 CHECKPOINT: Only after those 3 questions are answered (or defaults confirmed), proceed to scaffold.** If the user's content is rich enough to infer all three, propose your defaults and proceed — but state your assumptions explicitly so the user can correct before you invest in authoring.

## Delivery mode: static vs interactive (decide first)

Before scaffolding, classify the deliverable. This determines whether you
include `runtime.js`, speaker notes, and keyboard features.

| Mode | Examples | Include `runtime.js`? | Speaker notes? | Export target |
|---|---|---|---|---|
| **Interactive deck** | 技术分享、演讲、路演、课堂 | ✅ Yes | ✅ Yes (use `<div class="notes">`) | Live browser / full-screen `F` |
| **Static image set** | 小红书图文、产品图册、海报式 slides | ❌ No | ❌ No | PNG screenshot per slide (3:4 or 16:9) |

**Decision rule**: if the user will **stand up and talk** through the slides →
interactive. If the slides are meant to be **viewed as standalone images**
(小红书, Instagram, static report) → static.

For static mode: strip `<script src="...runtime.js">`, do NOT add `<div
class="notes">`, and set an explicit aspect ratio (e.g. `aspect-ratio: 3/4`
on `.slide`) so each slide renders as a clean standalone image.

## Quick start

### 1. Scaffold a new deck

**macOS / Linux:**
```bash
./scripts/new-deck.sh my-talk && open examples/my-talk/index.html
```
**Windows (PowerShell)** — `new-deck.sh` is bash-only, use manual fallback:
```powershell
New-Item -ItemType Directory -Path examples\my-talk -Force
Copy-Item templates\deck.html examples\my-talk\index.html
Invoke-Item examples\my-talk\index.html
```

### 2. Pick a theme
Press `T` to cycle, or hard-code: `<link rel="stylesheet" id="theme-link"
href="../assets/themes/aurora.css">`. Catalog: [references/themes.md](references/themes.md).

### 3. Pick layouts
Copy `<section class="slide">...</section>` blocks from
`templates/single-page/` into your deck. Replace demo data.
Catalog: [references/layouts.md](references/layouts.md).

### 4. Add animations
`data-anim="fade-up"` on any element. `anim-stagger-list` for grids/lists.
Canvas FX: `<div data-fx="knowledge-graph">` + `<script
src="../assets/animations/fx-runtime.js">`.
Catalog: [references/animations.md](references/animations.md).

### 5. Use a full-deck template
Copy `templates/full-decks/<name>/` into `examples/my-talk/`.
Catalog: [references/full-decks.md](references/full-decks.md).

### 6. Render to PNG
**macOS:** `./scripts/render.sh examples/my-talk/index.html 12`
**Windows (PowerShell)** — `render.sh` hardcodes Mac Chrome path, use:
```powershell
$chrome = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
1..12 | ForEach-Object { & $chrome --headless --screenshot="slide-$_.png" --window-size=1920,1080 "file:///$(Resolve-Path 'examples/my-talk/index.html')#/$_" }
```

## Content skeletons (don't build hollow decks)

A great theme + layout is just the shell. The **content structure** is what
makes a deck effective. Use these skeletons as starting outlines, then map
each page to a layout from `references/layouts.md`.

### Tech sharing (技术分享, 15-30 min → 8-15 slides)
```
cover → background/problem (2 slides) → solution overview → 
3-4 deep-dive pages (architecture diagram + code/demo + data results) → 
lessons learned → roadmap → Q&A / thanks
```
- **Page count rule**: 1 slide per 1.5-2 minutes of talk time.
- **Deep-dive rhythm**: 1 concept per slide. Use `arch-diagram` or `flow-diagram`
  for architecture, `code` or `terminal` for demos, `chart-bar`/`stat-highlight`
  for results.

### VC pitch deck (融资路演, 10-12 slides)
```
cover → problem → solution → market size → business model →
traction / metrics → competitive landscape → team →
financial projections → the ask (funding amount + use of funds) → contact
```
- **Tone**: confident, data-driven. Use `stat-highlight` for market size,
  `comparison` for competitive landscape, `kpi-grid` for traction metrics.
- **The ask slide** must state: amount raising, valuation (if appropriate),
  use of funds breakdown.

### 小红书图文 (Xiaohongshu, 6-9 cards, 3:4 ratio)
```
封面hook (大字标题 + 视觉钩子) → 痛点共鸣 → 核心方法/步骤 1-3 →
效果对比 → 总结/收藏提示 → 互动引导
```
- **Text rhythm**: 标题 < 15 字, 正文每段 1-2 行, 用 emoji 做视觉分隔
- **Aspect ratio**: set `aspect-ratio: 3/4` on `.slide` for vertical cards
- **No runtime.js** — these are static images, not interactive decks
- **Layout mapping**: 封面 → `cover.html` (enlarged), 痛点 → `big-quote.html` or `bullets.html`, 步骤 → `process-steps.html` or `three-column.html`, 效果对比 → `comparison.html`, 总结 → `stat-highlight.html` or `cta.html`

### Weekly report (周报, 5-8 slides)
```
cover → KPI summary (kpi-grid) → accomplishments this week →
blockers / risks → next week plan → appendix (data details)
```

### Trimming skeletons to a page count
When the user specifies an exact slide count (e.g. "10 页") but the skeleton
has more items, prioritize in this order:
1. **Keep**: cover, core problem/solution, the ask/CTA, thanks — these are non-negotiable
2. **Merge**: combine related items (e.g. "market size" + "business model" → one slide with two halves)
3. **Cut**: appendix, deep-dive sub-pages, secondary metrics
4. **Never cut**: cover and the final CTA/thanks — a deck without bookends feels unfinished

## Presenter mode vs tech-sharing template (decision rule)

Both `presenter-mode-reveal` and `tech-sharing` are valid for a 技术分享.
Use this decision tree:

```
Does the user need 逐字稿 / 提词器 / speaker notes?
├── YES (explicitly mentioned 演讲/讲稿/怕忘词/提词器) → presenter-mode-reveal
└── NO (just "做个分享"/"做个 slides")
    ├── Will they present live to an audience? → presenter-mode-reveal (add notes proactively)
    └── Just slides for reference/static viewing? → tech-sharing (no notes needed)
```

**Rule**: when in doubt for a live talk, default to `presenter-mode-reveal` and
write 150-300 words of 逐字稿 per slide. The cost of extra notes is low; the
cost of a presenter freezing mid-talk is high.

**⚠️ Effort warning**: 逐字稿 at 150-300 words/slide × N slides = significant
output. For a 13-slide deck that's 1,950-3,900 words of script. Before writing
all scripts, state the scope to the user: "这份 deck 有 N 页，逐字稿大概 X 千字，
我先写前 3 页你看节奏对不对？" Write 2-3 sample slides first, confirm the tone,
then batch the rest.

## Authoring rules (important)

- **Always start from a template.** Don't author slides from scratch — copy the
  closest layout from `templates/single-page/` first, then replace content.
- **Use tokens, not literal colors.** Every color, radius, shadow should come
  from CSS variables defined in `assets/base.css` and overridden by a theme.
  Good: `color: var(--text-1)`. Bad: `color: #111`.
- **Don't invent new layout files.** Prefer composing existing ones. Only add
  a new `templates/single-page/*.html` if none of the 30 fit.
- **Respect chrome slots.** `.deck-header`, `.deck-footer`, `.slide-number`
  and the progress bar are provided by `assets/base.css` + `runtime.js`.
- **Keyboard-first.** Always include `<script src="../assets/runtime.js"></script>`
  so the deck supports ← → / T / A / F / S / O / hash deep-links.
- **One `.slide` per logical page.** `runtime.js` makes `.slide.is-active`
  visible; all others are hidden.
- **Supply notes.** Wrap speaker notes in `<div class="notes">…</div>` inside
  each slide. Press S to open the overlay.
- **NEVER put presenter-only text on the slide itself.** Descriptive text like
  "这一页展示了……" or "Speaker: 这里可以补充……" or small explanatory captions
  aimed at the presenter MUST go inside `<div class="notes">`, NOT as visible
  `<p>` / `<span>` elements on the slide. The `.notes` class is `display:none`
  by default — it only appears in the S overlay. Slides should contain ONLY
  audience-facing content (titles, bullet points, data, charts, images).

## Writing guide

See [references/authoring-guide.md](references/authoring-guide.md) for a
step-by-step walkthrough: file structure, naming, how to transform an outline
into a deck, how to choose layouts and themes per audience, how to do a
Chinese + English deck, and how to export.

## 🚫 Antipatterns & blacklisted actions (do NOT do these)

These are common mistakes that degrade deck quality or break functionality.

| # | ❌ Antipattern | Why it's wrong | ✅ Do this instead |
|---|---|---|---|
| 1 | **Putting presenter-only text on slides** | Descriptive captions like "这一页展示了…" or "Speaker: 补充说明…" are visible to the audience and look unprofessional | Put all speaker cues in `<div class="notes">` — it's `display:none`, only shows in S overlay |
| 2 | **Using literal hex colors** | Breaks theme switching — hardcoded `#111` won't change when user presses T | Always use tokens: `color: var(--text-1)`, `background: var(--surface)` |
| 3 | **Stuffing runtime.js into static decks** | 小红书图文 / 产品图册 are static images — keyboard nav and presenter mode are dead weight that confuse the export | For static mode: omit `<script src="runtime.js">`, set explicit `aspect-ratio`, render each slide as PNG |
| 4 | **More than one accent animation per slide** | Visual chaos — multiple entry effects compete for attention | Pick ONE accent animation per slide. Everything else stays calm |
| 5 | **Repeating the same layout back-to-back** | Monotony — three `bullets.html` in a row feels like a Word document | Alternate layouts: `bullets` → `two-column` → `stat-highlight` → `code` |
| 6 | **Writing 逐字稿 in 书面语** | "因此/该方案/综上所述" sounds like reading an essay, not talking to people | Use 口语: "所以/这个方案/简单来说" — see presenter-mode.md 三铁律 |
| 7 | **Skipping the 3-question opening** | Jumping straight into slides without confirming audience/style/length leads to rework | Always ask or propose-default the 3 questions before authoring (see "Before you author" section) |
| 8 | **Inventing new CSS instead of using tokens** | Creates visual inconsistency, breaks across themes | Compose from `base.css` tokens + theme overrides. Only add new `single-page/*.html` if none of 31 fit |

## Catalogs (load when needed)

- [references/themes.md](references/themes.md) — all 36 themes with when-to-use.
- [references/layouts.md](references/layouts.md) — all 31 layout types.
- [references/animations.md](references/animations.md) — 27 CSS + 20 canvas FX animations.
- [references/full-decks.md](references/full-decks.md) — all 15 full-deck templates.
- [references/presenter-mode.md](references/presenter-mode.md) — **演讲者模式 + 逐字稿编写指南（技术分享/演讲必看）**.
- [references/authoring-guide.md](references/authoring-guide.md) — full workflow.

## File structure

```
html-ppt/
├── SKILL.md                 (this file)
├── references/              (detailed catalogs, load as needed)
├── assets/
│   ├── base.css             (tokens + primitives — do not edit per deck)
│   ├── fonts.css            (webfont imports)
│   ├── runtime.js           (keyboard + presenter + overview + theme cycle)
│   ├── themes/*.css         (36 token overrides, one per theme)
│   └── animations/
│       ├── animations.css   (27 named CSS entry animations)
│       ├── fx-runtime.js    (auto-init [data-fx] on slide enter)
│       └── fx/*.js          (20 canvas FX modules: particles/graph/fireworks…)
├── templates/
│   ├── deck.html                  (minimal 6-slide starter)
│   ├── theme-showcase.html        (36 slides, iframe-isolated per theme)
│   ├── layout-showcase.html       (iframe tour of all 31 layouts)
│   ├── animation-showcase.html    (20 FX + 27 CSS animation slides)
│   ├── full-decks-index.html      (gallery of all 14 full-deck templates)
│   ├── full-decks/<name>/         (14 scoped multi-slide deck templates)
│   └── single-page/*.html         (31 layout files with demo data)
├── scripts/
│   ├── new-deck.sh                (scaffold a deck from deck.html)
│   └── render.sh                  (headless Chrome → PNG)
└── examples/demo-deck/            (complete working deck)
```

## Rendering to PNG

`scripts/render.sh` wraps headless Chrome at
`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`. For multi-slide
capture, runtime.js exposes `#/N` deep-links, and render.sh iterates 1..N.

```bash
./scripts/render.sh templates/single-page/kpi-grid.html        # single page
./scripts/render.sh examples/demo-deck/index.html 8 out-dir    # 8 slides, custom dir
```

## Keyboard cheat sheet

```
←  →  Space  PgUp  PgDn  Home  End    navigate
F                                       fullscreen
S                                       open presenter window (magnetic cards: current/next/script/timer)
N                                       quick notes drawer (bottom overlay)
R                                       reset timer (in presenter window)
?preview=N                              URL param — force preview-only mode (single slide, no chrome)
O                                       slide overview grid
T                                       cycle themes (reads data-themes attr)
A                                       cycle demo animation on current slide
#/N in URL                              deep-link to slide N
Esc                                     close all overlays
```

## License & author

MIT. Copyright (c) 2026 lewis &lt;sudolewis@gmail.com&gt;.
