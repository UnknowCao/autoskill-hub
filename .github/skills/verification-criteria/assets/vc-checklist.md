# VC Quality Checklist

> Use for self-check before peer review. Score each VC.

## Per-VC SMARTR-OC Self-Check Card

**VC ID**: `_______________`  **Linked Requirement**: `_______________`

| # | Check | Question | ✓/✗ | Notes |
|---|-------|----------|-----|-------|
| S | Specific | Points to exactly one requirement unambiguously? | ☐ | |
| M | Measurable | Contains numeric threshold or explicit boolean condition? | ☐ | |
| A | Achievable | Executable with current equipment and schedule? | ☐ | |
| R | Relevant | Directly verifies the requirement intent, no irrelevant checks? | ☐ | |
| T | Traceable | Bidirectional link (ReqID ↔ VC ID) established? | ☐ | |
| R | Repeatable | Different engineer → same conclusion? | ☐ | |
| O | Objective | Free of "good", "beautiful", "sufficient", "appropriate"? | ☐ | |
| C | Complete | Covers normal + boundary + abnormal conditions? | ☐ | |

**Score**: ___ / 8   **Result**: ☐ ≥ 6 (submit for review) / ☐ < 6 (revise)

---

## Peer Review Checklist (CK-01~CK-10)

> Used by AI in B.2 pre-review dry run, and by human reviewers in formal peer review meetings. Fill per VC.

**VC ID**: `_______________`  **Review**: ☐ AI Pre-Review / ☐ Human Peer Review

| # | Check Item | Severity | Pass? | Notes |
|---|-----------|----------|-------|-------|
| CK-01 | VC-to-requirement one-to-one mapping (no orphans) | 🔴 Critical | ☐ | |
| CK-02 | VC ID naming convention compliance | 🟡 Minor | ☐ | |
| CK-03 | Verification method matches requirement type | 🔴 Critical | ☐ | |
| CK-04 | Test conditions complete (environment, equipment, precision) | 🔴 Critical | ☐ | |
| CK-05 | Criterion quantified with thresholds | 🔴 Critical | ☐ | |
| CK-06 | Sample size reasonable with statistical significance | 🟡 Minor | ☐ | |
| CK-07 | Boundary conditions covered (normal + boundary + abnormal) | 🟡 Minor | ☐ | |
| CK-08 | Achievability confirmed (equipment, manpower, time) | 🟡 Minor | ☐ | |
| CK-09 | Bidirectional traceability (Req → VC → Test Case → Result) | 🔴 Critical | ☐ | |
| CK-10 | Language unambiguous, directly executable by test engineer | 🔴 Critical | ☐ | |

**Outcome**: ☐ ✅ Ready for Peer Review / ☐ ⚠️ Conditional Pass / ☐ ❌ Needs Revision

---

## Coverage Audit Matrix

| Requirement ID | Has VC? | VC ID(s) | SMARTR-OC Score | Gaps Noted |
|---------------|---------|----------|-----------------|------------|
| | ☐ Yes ☐ No | | /8 | |
| | ☐ Yes ☐ No | | /8 | |
| | ☐ Yes ☐ No | | /8 | |
| | ☐ Yes ☐ No | | /8 | |
| | ☐ Yes ☐ No | | /8 | |

**Coverage Summary**:
- Total Requirements: ___
- With VC: ___ (___%)
- Without VC (Gaps): ___
- Orphan VCs (no linked requirement): ___
- Average SMARTR-OC Score: ___/8
