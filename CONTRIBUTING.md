# Contributing to autoskill-hub

First off, thanks for taking the time to contribute! 🎉

This document explains how to add a new skill, what conventions to follow, and
how your PR will be reviewed. The goal is to keep every skill **anchored to a
V-model phase and an ASPICE process reference**, so the whole repository stays
navigable as a lifecycle map.

---

## 🧭 Core Principle

Every skill in `autoskill-hub` must answer two questions up front:

1. **Which V-model phase does this skill serve?** (left wing / right wing / cross-cutting)
2. **Which ASPICE process reference does it map to?** (e.g. SYS.2 BP5, SWE.4)

If a skill cannot answer both, it does not belong in this repository. We are a
**process-driven** skill hub, not a grab-bag of prompt snippets.

---

## 📁 Repository Structure

```
autoskill-hub/
├── README.md                  # Repository overview + skill catalog
├── LICENSE                    # Apache-2.0
├── NOTICE                     # Attribution + third-party trademark notes
├── CONTRIBUTING.md            # You are here
├── .github/                   # Issue/PR templates, workflows (optional)
└── skills/
    └── <your-skill-name>/     # One folder per skill
        ├── SKILL.md           # REQUIRED — entry point (agent loads this)
        ├── README.md          # REQUIRED — user-facing overview + badges
        ├── test-prompts.json  # RECOMMENDED — regression test prompts
        ├── references/        # On-demand loaded reference docs
        ├── assets/            # Templates, checklists, scorecards
        └── scripts/           # Supporting Python/JS scripts (optional)
```

---

## 🆕 Adding a New Skill

### Step 1 — Name it

- Use **lowercase-kebab-case** (`verification-criteria`, `hara-drafting`).
- The name should describe the *engineering activity*, not a product domain.
- Avoid trademarked names (AUTOSAR, ISO) in the skill name — use them in
  description/keywords instead.

### Step 2 — Create the folder

```bash
mkdir -p skills/<your-skill-name>/{references,assets,scripts}
```

### Step 3 — Write `SKILL.md` (required)

This is what the agent loads. It MUST contain:

#### 3.1 YAML Frontmatter

```yaml
---
name: <your-skill-name>          # MUST match folder name
description: >
  One-paragraph description. MUST include trigger keywords (both EN and 中文)
  so the agent knows when to activate. Example:
  "Generate, audit, and trace verification criteria. Use when: 生成VC,
   验证标准, SMARTR-OC, 覆盖率, coverage audit."
---

# <Skill Title>
```

#### 3.2 V-Model × ASPICE Declaration (required)

Place this block immediately after the title:

```markdown
## 🗺️ V-Model × ASPICE Mapping

| Field | Value |
|---|---|
| V-Model Wing | left / right / cross_cutting |
| V-Model Phase | SYS.2 / SWE.4 / SYS.5 / ... |
| ASPICE Process | SYS.2.5 / SWE.4.BP1 / MAN.3 / ... |
| ISO 26262 Clause (optional) | Part 3-7 / Part 4-6 / ... |
| Traceability | upstream: [...] · downstream: [...] |
```

> This table is **mandatory** — reviewers will block PRs that omit it.

#### 3.3 Body

Follow the structure used by [`verification-criteria/SKILL.md`](./skills/verification-criteria/SKILL.md):
quick mode selector, workflow steps, decision tables, anti-patterns, references
loaded on-demand. Keep the entry `SKILL.md` as a router; push long content into
`references/*.md`.

### Step 4 — Write `README.md` (required)

User-facing overview with badges. See
[`verification-criteria/README.md`](./skills/verification-criteria/README.md)
as the template. MUST include:

- English + 中文 description
- V-Model × ASPICE mapping
- Quick start example
- File structure listing
- License note (Apache-2.0, links to repo root)

### Step 5 — Add test prompts (recommended)

Create `test-prompts.json` — a list of prompts that should activate the skill
and produce expected behavior. Used for regression checks.

### Step 6 — Update the catalog

Add a row for your skill in the root [`README.md`](./README.md) "Skill Catalog"
table with the correct V-model phase + ASPICE process columns filled.

---

## ✅ Skill Quality Checklist

Before opening a PR, confirm:

- [ ] `SKILL.md` frontmatter has `name` (matches folder) + `description` (with EN/中文 triggers)
- [ ] V-Model × ASPICE mapping table present and filled
- [ ] No copyrighted standard text reproduced (ISO, AUTOSAR, MISRA originals are paid — reference numbers + summaries only)
- [ ] No subjective quality claims ("excellent", "the best") — show concrete behavior instead
- [ ] If scripts are included, they are documented and have no hard-coded secrets
- [ ] `README.md` has both EN and 中文 descriptions
- [ ] Test prompts cover at least: happy path, one edge case, one anti-pattern rejection
- [ ] All Markdown links resolve (relative paths verified)
- [ ] License remains Apache-2.0 (no sub-licensing unless discussed in an issue first)

---

## 🚫 What Belongs Elsewhere

| You want to... | It belongs in... |
|---|---|
| Share a one-off prompt snippet | a Gist or the project's `discussions/` |
| Wrap a specific product/tool (CANoe, DaVinci) | your own repo — we are methodology-focused |
| Redistribute ISO/AUTOSAR standard text | ❌ nowhere in this repo — that's a copyright violation |
| Add a BMS-specific or product-specific skill | only if it's framed as methodology reusable across domains |

---

## 🧪 Review Process

1. Open a PR with a clear title: `skill: add <name>` or `skill(<name>): <change>`.
2. A maintainer will check:
   - V-model × ASPICE mapping correctness
   - Frontmatter + README completeness
   - No copyrighted standard text
   - Trigger keywords coverage (EN + 中文)
   - Test prompt sanity
3. Expect 1–3 rounds of review for new skills. Bug fixes usually merge same day.

---

## 📜 Licensing of Contributions

By submitting a pull request, you agree to license your contribution under the
project's [Apache-2.0 license](./LICENSE). If your contribution includes code
under a different license, please disclose it in the PR description.

We do **not** require a CLA for individuals. Corporate contributors should
ensure their employment agreement permits Apache-2.0 contributions.

---

## 💬 Questions?

- Open a [Discussion](https://github.com/UnknowCao/autoskill-hub/discussions) for "how do I..." questions
- Open an [Issue](https://github.com/UnknowCao/autoskill-hub/issues) for bugs, skill requests, or process mapping debates

Thanks for helping automotive engineers ship safer software. 🚗
