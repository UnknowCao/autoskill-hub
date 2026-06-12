# VC Report Templates

## Quality Audit Report (Workflow B)

```
## VC Quality Audit Report

**Source**: [filename]
**Total VCs reviewed**: N
**Average SMARTR-OC score**: X.X/8

### SMARTR-OC Score Distribution
- 8/8 (Excellent): N
- 6-7/8 (Acceptable): N
- <6/8 (Needs Revision): N

### CK-01~CK-10 Pre-Review Summary
- ✅ Ready for Peer Review: N
- ⚠️ Conditional Pass (Minor items only): N
- ❌ Needs Revision (Critical items): N

### Per-VC Results

| VC ID | SMARTR-OC | Failed Attributes | CK Critical ❌ | CK Minor ❌ | Disposition | Recommendation |
|-------|-----------|-------------------|---------------|------------|-------------|----------------|
| VC-REQ-001 | 7/8 | C | — | CK-07 | ⚠️ Conditional | Add boundary conditions |
| VC-REQ-003 | 4/8 | M, R, O | CK-05 | CK-04, CK-06 | ❌ Needs Revision | Add numeric threshold, specify conditions, replace "good" with quantified criteria |
| VC-REQ-005 | 8/8 | — | — | — | ✅ Ready | — |
| ... | ... | ... | ... | ... | ... | ... |

### Top Issues
1. [Most common issue across SMARTR-OC and CK results]
2. [Second most common]
3. [Third most common]
```

## Coverage Audit Report (Workflow C)

```
## VC Coverage Audit Report

**Requirements source**: [filename]
**VCs source**: [filename]

### Summary
- Total requirements: N
- Covered (≥1 VC): N (X%)
- Uncovered (0 VCs): N (X%)
- Total VCs: N
- Orphan VCs (no valid link): N

### Uncovered Requirements
| Req ID | Description |
|--------|-------------|
| REQ-002 | [description] |
| ... | ... |

### Orphan VCs
| VC ID | Linked Req (invalid) | Issue |
|-------|---------------------|-------|
| VC-UNKNOWN-001 | REQ-999 | Requirement not found |
| VC-REQ-005-orphan | (none) | No linked requirement |

### Coverage Matrix
[table from C.4]
```
