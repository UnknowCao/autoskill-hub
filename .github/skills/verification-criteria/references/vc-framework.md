# VC Definition Framework & Methodology Reference

> Condensed from ASPICE SYS.2 BP5 practice, INCOSE Handbook, ISO/IEC 29148.

## VC Definition (What, Why, When, Who)

**Verification Criteria (VC)** is a measurable, repeatable judgment condition that determines whether a system requirement has been met.

A qualified VC must answer three questions:
1. **What to verify**: Which aspect of which requirement?
2. **How to verify**: What method (Analysis/Inspection/Test/Demonstration)?
3. **Pass/Fail criterion**: What result counts as pass?

```
Requirement: "System shall respond to CAN wake-up signal within 500ms"
       ↓
VC:  "Under normal supply voltage (9V~16V), send CAN network wake-up frame via CAN tool,
      measure at ECU Wake-Up pin the time from frame transmission end to pin level rise,
      repeat 100 times, max ≤ 500ms, no single measurement > 550ms."
      ↑ What              ↑ How                         ↑ Criterion
```

### Why VC Exists

| Level | Value |
|-------|-------|
| **Engineering** | Makes requirements verifiable — eliminates "translation loss" between requirements and testing |
| **Quality** | Prevents requirement drift — VC is the "anchor point" for requirements |
| **Process** | Enables bidirectional traceability: Stakeholder Req → System Req → VC → Test Case → Test Result |

### When — VC Timing

| Timing | Approach | Consequence |
|--------|----------|-------------|
| ✅ Synchronous | Write VC simultaneously with requirement | Mutual calibration, built-in quality |
| ❌ Post-freeze | Batch-fill VC after requirement baseline | VC becomes a documentation task, disconnected from requirements |
| ❌ Testing phase | Test engineers reverse-derive VC | Requirement intent distorted, insufficient verification |

### Who — VC Ownership

- **Primary**: System Requirements Engineer (VC is part of requirement definition)
- **Reviewer**: Test Engineer (provides testability feedback)
- **Approver**: Technical lead / review committee
- **Consultant**: Functional safety engineer (for ASIL requirements)

## VC Classification System

### By Verification Method (4-Type Method)

| Method | Definition | Typical Application |
|--------|-----------|-------------------|
| **Analysis** | Verify via mathematical models, simulation, calculation | Thermal analysis, EMC simulation, WCA, reliability prediction |
| **Inspection** | Verify via visual review, document review | Connector selection check, PCB layout review, wiring check |
| **Test** | Verify by running system/component under controlled conditions | Functional test, performance test, durability test, HIL/SIL |
| **Demostration** | Verify via actual operation demonstration | UI workflow, maintenance accessibility, assembly feasibility |

### By Requirement Type

| Requirement Type | VC Core Elements | Example |
|-----------------|-----------------|---------|
| **Functional** | Input-output behavior, state transitions | "Press SPORT button → VehModeSt signal changes to 0x02 within 200ms, repeat 10 times, 0 failures" |
| **Performance** | Quantified metric + measurement conditions + statistical method | "CAN bus load ≤ 50%, measured at 500kbps for 1 hour average" |
| **Reliability** | Confidence level + sample size + failure criterion | "95% confidence, 80% reliability, 1000 cycles without failure" |
| **Timing** | Start/end event definition + time window | "From KL15 ON to HMI first screen rendered ≤ 2.5s" |
| **Safety (ASIL)** | Safety goal + FTTI + safe state | "Overvoltage protection must disconnect main circuit within 50ms of detection" |
| **Interface** | Signal monitoring + timing + data integrity | "CAN-FD message ID 0x3A1: period 20ms ±1ms avg, max interval ≤25ms, frame loss = 0" |

## SMARTR-OC Extended Quality Model

| Attribute | Definition | Anti-Example |
|-----------|-----------|--------------|
| **S**pecific | VC points to specific requirement and verification object unambiguously | "Verify system functionality is normal" |
| **M**easurable | Criterion includes quantifiable numeric or boolean condition | "Response speed is fast enough" |
| **A**chievable | Executable within project constraints (cost, equipment, time) | Requires 1M km real-vehicle verification |
| **R**elevant | VC directly corresponds to requirement, no irrelevant verification | Verifying connector appearance for communication rate requirement |
| **T**raceable | VC uniquely traces to requirement and can be referenced by test cases | Multiple requirements share one vague VC |
| **R**epeatable | Same conditions → same conclusion across different engineers | "Expert judges whether qualified" |
| **O**bjective | Criterion excludes subjective interpretation | "Interface is beautiful and elegant" |
| **C**omplete | Covers all key aspects: normal, boundary, abnormal conditions | Only verifies 25°C normal condition |

## VC-First Methodology — Four Layers

```
L1: Mindset
    "Every requirement is a hypothesis awaiting verification"
    VC is not a post-annotation; it's synchronous evidence of the requirement

L2: Principles
    P1: Synchronization — VC and requirement created/reviewed/changed together
    P2: Concretization — Abstract requirements transformed into concrete verification via VC
    P3: Boundary — VC must cover normal, boundary, and abnormal conditions
    P4: Traceability — Each VC bidirectionally linked to requirement and test case

L3: Process
    Understand intent → Select method → Define criterion → Set conditions → Write VC → Self-check (SMARTR-OC) → Peer review

L4: Tools & Methods
    VC template library, quality checklist, verification method decision tree, classification reference
```

### Key Cognitive Shifts

| From (Traditional) | To (VC-First) |
|--------------------|---------------|
| "What should the system do?" | "How do we prove the system did it?" |
| Requirements frozen first, testing adapts later | Requirements and verification co-evolve |
| VC is test team's job | VC is requirement engineer's core responsibility |
| VC as documentation appendix | VC as integral part of requirement |
| Quality found in testing phase | Quality built-in at requirement definition phase |

### VC-First Operating Process

```
1. Understand Intent    2. Select Method     3. Define Criterion
   • Who needs it?         • Analysis?           • Pass threshold
   • Why needed?           • Inspection?         • Measurement precision
   • Core objective?       • Test?               • Statistical method
   • Failure consequence?  • Demonstration?      • Sample size
         │                                             │
         └────────── Iterative Calibration ────────────┘
              If VC can't be defined, revise the requirement

4. Set Test Conditions  5. Write VC Statement  6. Quality Check
   • Environment           • Template-based       • SMARTR-OC self-check
   • Preconditions         • Structured           • Peer review
   • Equipment/Rig         • Traceable            • Test confirmation
```

### Adoption Resistance & Counter-Strategies

| Resistance | Counter-Strategy |
|------------|-----------------|
| "Too time-consuming" | Data shows VC investment reduces rework (typical ROI 1:4) |
| "I don't know how" | Provide VC template library and training |
| "Requirements still changing" | VC should also be lightweight and iterative |
| "Tools don't support it" | Build Excel side-table first, then push tooling upgrade |

## Traceability Chain

```
Stakeholder Req (SYS.1) → System Req (SYS.2) → VC (SYS.2 BP5) → Test Case (SYS.5) → Test Result
```

Every link must have bidirectional traceability. Breakage at any point = ASPICE non-conformance.
