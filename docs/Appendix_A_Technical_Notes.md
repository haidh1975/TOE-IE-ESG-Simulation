# Appendix A — Technical Notes on Calibration-Based Simulation

This document provides the complete technical specification for the reference
dataset construction, corresponding to Appendix A of the manuscript.

## A.1 Overview and Rationale

The study adopts a calibration-based simulation design. The reference dataset
(N = 500) is a Monte Carlo simulation in which all data-generating parameters
are anchored to published empirical benchmarks from three studies. The purpose
is to verify the internal coherence of the proposed framework and to confirm
that hypothesized effect sizes are statistically detectable at realistic SME
sample sizes — NOT to independently confirm the hypotheses in actual SMEs.

## A.2 Anchor Parameters

| Anchor Study | Parameters |
|---|---|
| Ramos-Vecino et al. (2026) | β(IndivF→Dig) ≈ 0.302; β(Dig→Perf) ≈ 0.549; AVE(OpPerf) ≈ 0.477; CR ≈ 0.864 |
| Guo et al. (2024) | β(ESG) ≈ 0.11; β(Myopia) ≈ −0.082; β(ESG×Myopia) ≈ −0.058; ESG μ=4.11, σ=0.72 |
| Nykänen et al. (2023) | ≈50% opportunity-dominant schemas (conceptual utility + procedural data) |

## A.3 Variable Generation (5 Steps)

**Step 1 — Exogenous variables**

All exogenous variables are generated as approximately independent
(pairwise |r| < 0.05 by construction).

| Variable | Distribution | Parameters | Bounds |
|---|---|---|---|
| ESG | Truncated Normal | μ=4.24, σ=0.65 | [1, 9] |
| Myopia | Half-Normal | σ=0.091 | [0.01, 0.40] |
| IndivF | Truncated Normal | μ=3.09, σ=0.87 | [1, 5] |
| OrgF | Truncated Normal | μ=3.20, σ=0.80 | [1, 5] |
| ln(Size) | Normal | μ=3.50, σ=0.80 | — |
| Age | Gamma | shape=2, scale=8 | — |

**Step 2 — Endogenous variable equations**

All inputs standardized (mean=0, SD=1) before estimation.

```
SubstDig = 0.110·ESG − 0.082·Myopia + 0.300·IndivF + 0.060·OrgF
           − 0.188·FC − 0.058·(ESG×Myopia) + 0.115·(ESG×IndivF) + ε₁
           ε₁ ~ N(0, 0.85)  →  baseline R² ≈ 0.15

StratDig = 0.043·ESG + 0.005·Myopia + 0.085·IndivF
           + 0.037·(ESG×Myopia) + ε₂
           ε₂ ~ N(0, 0.92)

OpPerf   = 0.549·SubstDig + 0.094·StratDig + 0.104·IndivF + ε₃
           ε₃ ~ N(0, 0.63)
```

**Step 3 — Financing Constraints (Kaplan-Zingales index)**

```
FC_raw = −0.737·ln(Size) + 0.043·ln(Size)² − 0.040·Age
FC     = (FC_raw − mean(FC_raw)) / SD(FC_raw)   [standardized]
```

where Size = total assets (log-transformed), Age = years since founding.
Following Guo et al. (2024).

**Step 4 — Multi-item construct scores**

For each latent construct L with k items:

```
x_ij = loading × L_i + sqrt(1 − loading²) × ε_ij
     where ε_ij ~ N(0, 1)
```

Composite score = mean(x_i1, ..., x_ik)

| Construct | Items | Loading | Expected AVE |
|---|---|---|---|
| SubstDig | 5 | 0.80 | 0.64 |
| StratDig | 4 | 0.80 | 0.64 |
| IndivF | 4 | 0.80 | 0.64 |
| OrgF | 3 | 0.78 | 0.61 |
| OpPerf | 7 | 0.70 | 0.49 |
| ESG | 1 (index) | 1.00 | — |

**Step 5 — Interaction terms**

Mean-centered products to reduce multicollinearity:

```
ESG_x_Myopia = (ESG − mean(ESG)) × (Myopia − mean(Myopia))
ESG_x_IndivF = (ESG − mean(ESG)) × (IndivF − mean(IndivF))
```

## A.4 Sensitivity Analysis

**Procedure:**
- Vary all structural coefficients simultaneously by a random scale factor
  drawn from Uniform(0.80, 1.20) [i.e., ±20%]
- Repeat across 500 Monte Carlo replications (random_state = seed+1000+rep)
- Record % of replications where each coefficient retains hypothesized sign

**Results (from `python simulate.py --sensitivity`):**

| Hypothesis | Direction | Stability (%) | Assessment |
|---|---|---|---|
| H1a: ESG → SubstDig | >0 | 99.4% | High |
| H1b: ESG → StratDig | >0 | 82.0% | Moderate |
| H3a: ESG×Myopia → SubstDig | <0 | 88.4% | Moderate |
| H3b: ESG×Myopia → StratDig | >0 | 79.2% | Low–Moderate |
| H4: ESG×IndivF → SubstDig | >0 | 98.0% | High |

H3b's 79.2% stability confirms it as the lowest-confidence finding and the
highest-priority hypothesis for primary-data empirical testing.
(All percentages reproducible with seed=42.)
