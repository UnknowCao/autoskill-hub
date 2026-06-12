# VC Development Practical Handbook

> Quick reference for system requirements engineers. Condensed from VC开发实用参考手册 V1.0.

## 1. VC 5-Element Structure

Every qualified VC must contain these five elements:

| # | Element | Must Include |
|---|---------|--------------|
| 1 | **VC ID** | Unique identifier, linked to requirement ID (e.g. `VC-REQ-001`) |
| 2 | **Linked Requirement** | Which requirement and which aspect is being verified |
| 3 | **Verification Method** | One of: Test / Analysis / Inspection / Demonstration; complex VCs may combine methods |
| 4 | **Test Conditions** | **Five sub-dimensions** (all must be addressed):<br>• **Environmental**: Temperature range, humidity, supply voltage, EMC environment<br>• **Preconditions**: System state (e.g. KL15 ON, vehicle speed = 0, gear = P)<br>• **Equipment**: Rig type (HIL/SIL/Vehicle), measurement device model & precision<br>• **Sample size**: Number of repetitions, statistical confidence requirements<br>• **Time window**: Start/end trigger events and measurement duration |
| 5 | **Pass/Fail Criterion** | **Three sub-elements** (see §1.1 for details):<br>• **Threshold**: Numeric pass/fail boundary (e.g. `≤ 100ms`, `≥ 95%`, `= 0`)<br>• **Statistical method**: How to conclude from multiple measurements (max/avg/Cpk)<br>• **Precision requirement**: Required accuracy of measurement equipment (e.g. `±1% current probe`) |

### Standard Table Header

```markdown
| VC ID | Linked Requirement | Verification Method | Test Conditions | Measurement Target | Pass/Fail Criterion |
|-------|-------------------|---------------------|-----------------|--------------------|--------------------|
```

### Good vs Bad VC Examples

**✅ Good VC:**

| VC ID | Linked Req | Method | Test Conditions | Target | Criterion |
|-------|-----------|--------|-----------------|--------|-----------|
| VC-BMS-001 | BMS-001 (Cell voltage accuracy) | Test | Rig: BMS HIL + programmable cell voltage simulator (accuracy ≤1mV); Temp: 25°C; Inject known reference voltage to all cell channels | ADC sampled value vs. injected reference per channel | All channels: \|sampled - reference\| ≤ 5mV; Sampling period: adjacent samples ≤ 100ms |

**❌ Bad VC:**

| VC ID | Linked Req | Method | Test Conditions | Target | Criterion |
|-------|-----------|--------|-----------------|--------|-----------|
| VC-001 | Voltage acquisition | Test | Lab | Voltage | Accuracy meets requirements |

> The bad VC fails on every element: equipment unspecified, conditions unqualified, criterion has no numeric value.

### 1.1 Pass/Fail Criterion Decomposition

A well-formed criterion must address three sub-elements. Do not conflate them — each serves a distinct purpose:

| # | Sub-Element | Purpose | Format Example |
|---|------------|---------|---------------|
| **Threshold** | The numeric boundary between pass and fail | `≤ 100ms`, `≥ 95%`, `= 0`, `± 5mV` |
| **Statistical method** | How to draw a conclusion from multiple measurements | `max value ≤ X across N trials`, `Cpk ≥ 1.33`, `avg ± 3σ within bounds` |
| **Precision requirement** | Required accuracy of measurement equipment relative to the threshold | `using current probe with ±1% accuracy`, `oscilloscope sampling ≥ 1kHz` |

**Why separate statistical method from threshold?** A common mistake is writing `"response time ≤ 100ms"` without specifying whether that's a single-trial max, an average, or a 99th percentile. Without the statistical method qualifier, the criterion is ambiguous and not repeatable.

#### Threshold Sources

When justifying a threshold value, cite one of three sources. This is frequently audited in ASPICE assessments:

| Source | Description | Example |
|--------|-------------|---------|
| **Standard / Regulation driven** | Mandated by GB/T, ISO, ECE, or other normative documents | ECE R13 stopping distance, ISO 26262 FTTI tables |
| **System architecture derived** | Derived from safety analysis (FMEA/FTA) or architecture constraints | FTTI from HARA, voltage tolerance from WCA |
| **Engineering benchmark** | Based on competitive analysis, historical project data, or expert judgment | "Competitor X achieves 2.0s; we target ≤ 2.5s" |

> If a threshold cannot be traced to any of these three sources, flag it 🟠 **VC-ASSUMPTION** and escalate.

### 1.2 Test Conditions Decomposition

Test conditions are often under-specified. Use these five sub-dimensions as a mandatory checklist:

| # | Sub-Dimension | Must Answer | Example |
|---|--------------|-------------|---------|
| **Environmental** | What temperature, humidity, voltage, EMC conditions? | `-40°C to 85°C, 9V–16V supply` |
| **Preconditions** | What system state must be established first? | `KL15 ON, vehicle speed = 0 km/h, gear = P` |
| **Equipment** | What rig + measurement devices + their precision? | `BMS HIL + programmable cell voltage simulator (±1mV)` |
| **Sample size** | How many repetitions? What statistical confidence? | `100 repetitions, 95% confidence` |
| **Time window** | What start/end events define the measurement window? | `from KL15 rising edge to HMI first frame rendered` |

**Common omission**: Sample size and time window are the two most frequently forgotten dimensions. Without them, the VC is not executable — the test engineer doesn't know how long to monitor or how many trials to run.

## 2. SMARTR-OC Self-Check Flow

The 8-point SMARTR-OC scoring rubric is defined in SKILL.md §A.3. The serial self-check process below walks through each attribute in order when a VC needs revision:

### Self-Check Flow

```
VC written
    ↓
S: Unambiguous? ─No→ Add requirement reference → Recheck
    ↓ Yes
M: Has numbers? ─No→ Add quantified threshold → Recheck
    ↓ Yes
A: Achievable? ─No→ Adjust method or conditions → Recheck
    ↓ Yes
R: Relevant? ─No→ Remove irrelevant checks → Recheck
    ↓ Yes
T: Traceable? ─No→ Add bidirectional link → Recheck
    ↓ Yes
R: Repeatable? ─No→ Clarify conditions → Recheck
    ↓ Yes
O: Objective? ─No→ Replace subjective terms → Recheck
    ↓ Yes
C: Complete? ─No→ Add boundary/abnormal conditions → Recheck
    ↓ Yes
Score ≥ 6/8? → Yes → Submit for review
            → No  → Revise VC
```

## 3. Peer Review Checklist (10 Items)

| # | Review Item | Severity |
|---|------------|----------|
| CK-01 | VC-to-requirement one-to-one mapping (no orphans) | 🔴 Critical |
| CK-02 | VC ID naming convention compliance | 🟡 Minor |
| CK-03 | Verification method matches requirement type | 🔴 Critical |
| CK-04 | Test conditions complete (environment, equipment, precision) | 🔴 Critical |
| CK-05 | Criterion quantified with thresholds | 🔴 Critical |
| CK-06 | Sample size reasonable with statistical significance | 🟡 Minor |
| CK-07 | Boundary conditions covered (normal + boundary + abnormal) | 🟡 Minor |
| CK-08 | Achievability confirmed (equipment, manpower, time) | 🟡 Minor |
| CK-09 | Bidirectional traceability (Req → VC → Test Case → Result) | 🔴 Critical |
| CK-10 | Language unambiguous, directly executable by test engineer | 🔴 Critical |

> 🔴 Critical = must fix before pass | 🟡 Minor = recommend fix, can pass conditionally

### Review Roles

| Role | Responsibility | Required? |
|------|---------------|-----------|
| System Requirements Engineer (VC Author) | Present VC logic, respond to challenges | ✅ Yes |
| Test Engineer | Assess testability, equipment feasibility | ✅ Yes |
| Functional Safety Engineer | Review ASIL-related VC adequacy | If ASIL applies |
| Technical Lead / Review Chair | Final approval | ✅ Yes |

### Review Outcomes

| Outcome | Condition |
|---------|-----------|
| ✅ Pass | CK-01 ~ CK-10 all satisfied |
| ⚠️ Conditional Pass | Only 🟡 items remain, with clear remediation plan and deadline |
| ❌ Fail | Any 🔴 item unsatisfied |

## 4. Top 10 Pitfalls

### Pitfall 1: Restating the requirement as VC

| ❌ Wrong | ✅ Right |
|---------|---------|
| Req: "System shall support CAN wake-up"<br>VC: "Verify CAN wake-up function is normal" | VC: "In VBAT=12V, ECU Sleep state, send NM wake-up frame ID=0x7DF, measure Wake pin level change time ≤ 100ms" |

**Root cause**: Zero information gain. **Countermeasure**: VC must be more specific than the requirement.

### Pitfall 2: "Execute per test case TC-xxx"

| ❌ Wrong | ✅ Right |
|---------|---------|
| "Verify per test case TC-001" | Write method, conditions, criteria directly in VC |

**Root cause**: Circular reference — VC is upstream of test cases. **Countermeasure**: VC → Test Case → Test Result is a one-way chain.

### Pitfall 3: Only verifying normal conditions

| ❌ Wrong | ✅ Right |
|---------|---------|
| VC only at 25°C, 12V | Add boundary (-40°C/+85°C, 9V/16V) and abnormal (overvoltage, short circuit, sensor disconnect) |

**Root cause**: Most automotive electronics failures occur at extreme conditions.

### Pitfall 4: Criterion has no numbers

| ❌ Wrong | ✅ Right |
|---------|---------|
| "Response time meets spec" | "Response time ≤ 100ms" |

**Root cause**: Without numbers, no objective pass/fail judgment is possible.

### Pitfall 5: Unreasonable sample size

| ❌ Wrong | ✅ Right |
|---------|---------|
| "Test once, if passes then passes" or "Test 10,000 times" | Functional: ≥10 times; Reliability: per statistical confidence; Protection: add false-trigger test (e.g., 100 times with 0 false triggers) |

### Pitfall 6: VC written solely by test engineers

| ❌ Wrong | ✅ Right |
|---------|---------|
| Requirements engineer only writes requirements, VC entirely handed to test team | Requirements engineer **primary author**; test engineer **reviews** for testability |

### Pitfall 7: VC added after requirement freeze

| ❌ Wrong | ✅ Right |
|---------|---------|
| Batch-fill VC after requirement baseline | VC and requirement produced, reviewed, changed **synchronously** |

### Pitfall 8: Wrong verification method

| ❌ Wrong | ✅ Right |
|---------|---------|
| All VCs use "Test", including EMC simulation, thermal analysis | Use decision tree: physical measurement → Test; theoretical derivation → Analysis; appearance/layout → Inspection; operation experience → Demonstration |

### Pitfall 9: Subjective language in VC

| ❌ Wrong | ✅ Right |
|---------|---------|
| "Interface is beautiful", "Reliability is good" | "SUS score ≥ 80", "95% confidence reliability ≥ 99.9%" |

### Pitfall 10: VC granularity too coarse or too fine

| ❌ Wrong | ✅ Right |
|---------|---------|
| Too coarse: 1 VC covers 10 requirements<br>Too fine: 1 requirement split into 20 VCs | 1 VC corresponds to **one independently verifiable aspect** of one requirement |

## 5. Verification Method Decision Tree

```
Does the requirement involve physical phenomena measurement (V/I/Temp/Vibration/EMC)?
  ├─ Yes → Test
  │        └─ Sub-type: HIL test / Vehicle test / Environmental chamber test
  └─ No → Can it be verified by mathematical derivation/simulation?
            ├─ Yes → Analysis
            │        └─ Sub-type: WCA / Simulation / Statistical modeling
            └─ No → Needs human judgment (appearance/layout/document)?
                      ├─ Yes → Inspection or Demonstration
                      │        └─ Inspection: document review, design review
                      │        └─ Demonstration: prototype operation, mockup display
                      └─ No → Consider combining multiple methods
```

## 6. Quick Mnemonic

> **"Has numbers, has conditions, has method, traceable, repeatable, not subjective"**
> — Six-phrase mnemonic. Recite after writing each VC.

### One-Sentence VC Template

```
Under [test conditions], using [verification method], measure/check [target],
verify [criterion], repeat [sample size] times.
```

### One-Sentence Quality Summary

> **"If another engineer, reading only your VC (without the original requirement), can independently complete the verification and reach the same conclusion — the VC is qualified."**
