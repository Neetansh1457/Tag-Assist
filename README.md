# TagAssist: Tag Change Validation Prototype

## Overview

TagAssist is a prototype validation engine designed to assist investigators in reviewing tag change requests related to suspected fraud accounts.

The system evaluates both structured behavioral signals and investigator annotations to generate a confidence-based recommendation for:

- Auto-Approval  
- Manual Review  

This tool is intended as an operational assist system, not a fraud detection engine.

---

## Problem Statement

In the current workflow:

1. An investigator identifies potential fraud.
2. A tag change request is raised.
3. A specialized review team validates the request.
4. Backlogs can accumulate.
5. Manual review consumes operational bandwidth.

Given that experienced investigators are correct approximately ~90% of the time, there is an opportunity to:

- Validate high-confidence cases automatically
- Reduce manual review load
- Preserve review bandwidth for edge cases

TagAssist explores a confidence-based assist mechanism for this queue.

---

## System Design

The prototype combines two independent signals:

### 1. Behavioral Risk Signal (Structured Data)

Features include:

- Order velocity
- Device changes (7 days)
- IP changes (7 days)
- Unpaid ratio
- High-risk category flag

These are modeled using XGBoost to estimate fraud-related behavioral risk.

---

### 2. Investigator Reasoning Alignment (Text Signal)

Investigator annotations are embedded using a sentence transformer model.

The system evaluates semantic alignment with known fraud-related reasoning patterns.

This allows the model to assess whether the written reasoning supports elevated fraud risk.

---

## Final Decision Logic

Final Validation Confidence is computed as a weighted blend:

Final Score = α * Behavioral Signal + (1 - α) * Text Signal

A configurable threshold determines:

- APPROVE (auto-validation eligible)
- REJECT (manual review required)

---

## Operational Framing

The system estimates:

- Auto-Approval Rate
- Manual Review Reduction (Session-level)
- Confidence under configurable thresholds

This allows leadership to simulate policy sensitivity before operational rollout.

---

## Key Characteristics

- Binary validation prototype (Approve / Manual Review)
- Lightweight Flask deployment
- Session-level approval tracking
- Leadership-ready UI framing
- Modular architecture for future expansion

---

## What This Is Not

- Not a full fraud detection engine
- Not trained on production data
- Not a final policy enforcement system

This is a prototype to explore feasibility and operational impact.

---

## Future Enhancements

- Threshold sensitivity analysis dashboard
- Historical queue replay simulation
- Human-error modeling
- Feature attribution transparency (SHAP)
- Production model retraining pipeline
- Deployment with monitoring hooks

---

## Deployment

The application can be deployed via:

- Render
- Railway
- Internal container platform

Requires:

- Python 3.11+
- Flask
- XGBoost
- Sentence Transformers
- scikit-learn

---

## Author
Neetansh Shah

Prototype designed and implemented to explore ML-assisted tag validation workflows in operational fraud environments.
