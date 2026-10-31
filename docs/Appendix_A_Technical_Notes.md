# Appendix A — Technical Notes (v2.1, AUTHORITATIVE)

## A.1 Design decision

Regressions target the **generated construct scores**, because that is the level at
which the anchor-study parameters are defined. Item indicators are generated in a
**separate layer used only for the measurement calibration check** and never enter
any regression. Analysing noisy item means (the v1.0 approach) attenuated every
coefficient and was the principal cause of the v1.0 manuscript–code mismatch.

## A.2 Imposed parameters

All structural coefficients are declared in the `TARGETS` dictionary at the top of
`simulate.py` — a single source of truth. `tableA2_imposed_parameters.csv` is written
directly from it.

Key values: SD_ESG .110 · SD_Myopia −.082 · SD_IndivF .300 · SD_FC −.188 ·
SD_ESGxMyopia −.058 · SD_ESGxIndivF .115 · StD_ESG .043 · StD_ESGxMyopia .037 ·
OP_SubstDig .549 · **FC_ESG −.180** (H1c, encoded ex ante) · FC_SAindex .600.

These values are unchanged in v2.1. No imposed parameter, distribution or structural
equation was altered between v2.0 and v2.1.

## A.3 Generation procedure

1. **Exogenous constructs** — ESG ~ TN(4.24, .65²) on [1,9]; Myopia ~ |N(0,.091²)| on
   [.01,.40]; IndivF ~ TN(3.09,.87²); OrgF ~ TN(3.20,.80²); TechF ~ TN(3.15,.82²);
   EnvF ~ TN(3.05,.85²); ln(Size) ~ N(3.50,.80²); Age ~ Gamma(2,8);
   ROA ~ N(.045,.060²); Leverage ~ Beta(2,3). Mutually independent by construction.
2. **Financing constraints** — SA index (Hadlock & Pierce 2010):
   `SA = −0.737·ln(Size) + 0.043·ln(Size)² − 0.040·Age`;
   then `FC = .600·z(SA) + (−.180)·z(ESG) + ε`, ε ~ N(0,.55²).
   The ESG→FC path is encoded **explicitly and ex ante**; it did not exist in v1.0.
3. **Endogenous constructs** — structural equations with the imposed coefficients and
   residual SDs σ(SubstDig)=.92, σ(StratDig)=.96, σ(OpPerf)=.80.
4. **Measurement layer (check only)** — `x_ij = λ·L_i + √(1−λ²)·ε_ij`, λ ≈ .74–.82.
5. **Interactions** — z-standardised products of standardised constituents.
   This standardisation matters for interpretation and is discussed in A.6.

---

# v2.1 additions

Sections A.5 to A.7 document what changed in v2.1. Sections A.1 to A.4 describe the
data-generating structure, which is unchanged, and A.4 retains the v2.0 account of
the Monte Carlo design for continuity.

## A.5 The `MED_X` common covariate specification

### Why the v2.0 mediation was not identified

In v2.0 the total effect `c` was read from `M1_SubstDig_baseline`. That model already
contains `FC` as a regressor. A path estimated while holding the mediator fixed is a
direct effect, not a total effect, so `c` and `c′` were both direct effects obtained
under different covariate sets.

The three equations also disagreed on controls:

| Path | v2.0 model | Covariates |
|---|---|---|
| `c` | `M1_SubstDig_baseline` | Myopia, IndivF, OrgF, TechF, EnvF, **FC**, lnSize, Age, ROA, Leverage |
| `a` | `M5a_FC_on_ESG` | **SA_index**, ROA, Leverage |
| `b`, `c′` | `M5b_SubstDig_with_FC` | IndivF, OrgF, lnSize, Age, ROA, Leverage |

With different conditioning sets the quantities are not comparable, and the
decomposition `c = c′ + a·b` has no reason to hold.

### The v2.1 specification

v2.1 defines one covariate set and uses it in every equation:

```python
MED_X = ("Myopia + IndivF + OrgF + TechF + EnvF + "
         "lnSize + Age + ROA + Leverage")
```

| Model | Equation | Supplies |
|---|---|---|
| `M5c_SubstDig_total` | `SubstDig ~ ESG + MED_X` | `c`, the **total effect**, FC absent |
| `M5a_FC_on_ESG` | `FC ~ ESG + MED_X` | `a` |
| `M5b_SubstDig_with_FC` | `SubstDig ~ ESG + FC + MED_X` | `b` and `c′`, the **direct effect**, FC present |

The only difference between the `c` equation and the `c′` equation is the presence of
`FC`. Everything else is held identical. Under OLS this is exactly the condition under
which the decomposition is an algebraic identity rather than an approximation, and the
realised residual is `|c − (c′ + a·b)| = 2.2e-16`, i.e. machine precision.

### Results at seed 42, N = 500

| Quantity | Estimate |
|---|---|
| `c` total | **0.20864** |
| `a` ESG → FC | **−0.21237** |
| `b` FC → SubstDig | **−0.17492** |
| `c′` direct | **0.17149** |
| `a·b` indirect | **0.03715** |
| `c′ + a·b` | **0.20864** |
| Proportion mediated | **17.8%** |

The bootstrap of `a·b` uses the same two equations, so the interval refers to the same
quantity as the point estimate: 5,000 resamples give 0.0369 with a 95% percentile
interval of [0.0100, 0.0690].

Because `c′` remains significant and the indirect path carries a minority of the total
effect, the pattern is **partial** mediation. The proportion is computed, not assumed.

### Reading the rounded figures

Reported to three decimals, `c′ = 0.171` and `a·b = 0.037` sum to 0.208 while `c`
rounds to 0.209. Each figure is rounded independently; the identity holds at full
precision, not between rounded values. Manuscript Table 8 and Section 5.6 state this
explicitly.

## A.6 Why `SA_index` is omitted from `MED_X`

The v2.0 code comment said `SA_index` was omitted because it is a deterministic
function of `lnSize` and `Age`. That statement was wrong, and the correction matters
because it changes the reason for the choice.

`SA` is a deterministic function of `lnSize`, **`lnSize²`** and `Age`. A model
containing only the linear terms does not span the quadratic one, so the three
regressors are **not** exactly collinear:

```
R²(SA ~ lnSize + Age)              = 0.995
R²(SA ~ lnSize + lnSize² + Age)    = 1.000
```

Entering all three together is therefore estimable, but severely ill-conditioned.
Variance inflation factors in that specification:

| Regressor | VIF |
|---|---|
| `SA_index` | **221** |
| `Age` | **148** |
| `lnSize` | **81** |
| `ESG` | 1.03 |
| `FC` | ≈ 1 |

The focal paths are unaffected because `ESG` and `FC` sit outside the
ill-conditioned block. Re-estimating all three mediation equations with `SA_index`
added changes `c`, `a`, `b` and `c′` by **less than 0.0004**:

| Path | without `SA_index` | with `SA_index` | change |
|---|---|---|---|
| `c` | 0.2086 | 0.2086 | < 0.0001 |
| `a` | −0.2124 | −0.2124 | < 0.0001 |
| `b` | −0.1749 | −0.1753 | 0.0004 |
| `c′` | 0.1715 | 0.1713 | 0.0002 |

`SA_index` is omitted to keep the control block interpretable, not because its
inclusion would change any conclusion. The data-generating structure places `SA` in
the `FC` equation only, so its exclusion from the `SubstDig` equations is also
consistent with how the data were generated.

## A.7 H1c in the Monte Carlo study

Correcting the `a`-path specification changes the Monte Carlo row for H1c. No other
row moves, because no other path depends on `M5a`.

| Statistic | v2.0 | v2.1 |
|---|---|---|
| Bias | −0.035 | **−0.036** |
| RMSE | 0.047 | **0.048** |
| 95% CI coverage | 0.776 | **0.786** |
| Empirical power | 1.00 | 1.00 |

### This is not a small bias, and the coverage is not near nominal

The v2.0 notes described the H1c deviation as a "small bias" and reported coverage as
"≈ .95 except" for this path. Both descriptions understate the problem and are
withdrawn.

The imposed value is −0.180 and the mean recovered value is −0.216. The bias of
−0.036 is **20% of the imposed coefficient**, an order of magnitude larger than the
next-largest absolute bias in the table (0.005 for H4). Coverage of **0.786** means
that in roughly one replication in five the 95% interval fails to contain the imposed
value; nominal behaviour would miss it in one in twenty. Neither figure should be
summarised alongside the other six paths, which have |bias| ≤ 0.005 and coverage
between 0.940 and 0.962.

### Why H1c behaves differently

`FC` is standardised after generation. The imposed coefficient `FC_ESG = −0.180`
applies to `FC` on its generating scale, whereas the recovered coefficient is
estimated on `z(FC)`. The two differ by the realised standard deviation of the
generated `FC`, which itself varies across replications because each replication
perturbs `FC_SAindex` and `FC_ESG` independently. The estimator is therefore
recovering a target that moves with the perturbation, which displaces the sampling
distribution relative to the fixed nominal value used for the coverage calculation.

This is a property of the calibration design, not a defect in the estimator. The
honest reading is that **the H1c row quantifies how far the standardised mediator
path can be trusted, and the answer is: less than the other six paths**. The
manuscript reports the figures without adjustment and treats them as a calibration
diagnostic rather than as evidence about mediation in real SMEs.

### Unchanged Monte Carlo elements

Perturbation remains independent Uniform(0.8, 1.2) per coefficient over 500
replications with the same seed sequence. Empirical power is unchanged for every
path: H1a .648 · H1b .194 · H1c 1.000 · H2 1.000 · H3a .266 · H3b .134 · H4 .742.

## A.4 Monte Carlo performance and power

*(Retained from v2.0 for continuity. Where this section and A.7 differ on H1c, A.7
supersedes it.)*

Each coefficient is perturbed **independently** by Uniform(0.8, 1.2) over 500
replications. Reported per hypothesis: imposed mean, recovered mean, bias, RMSE,
empirical power, 95% CI coverage.

Recovery is unbiased for six of the seven paths (|bias| ≤ .005, coverage .940–.962).
The seventh, the standardised mediator path H1c, is the exception discussed in A.7.

**Empirical power at n = 500:** H1a .65 · H1b .19 · H1c 1.00 · H2 1.00 ·
H3a .27 · H3b .13 · H4 .74.

**Power curve** (`tableA4_power_curve.csv`) shows the interactions need roughly
n ≈ 2,000–4,000 to reach conventional power. Consequently Table 9 decisions are
**power-aware**: significance in a single draw is not treated as reliable recovery
when power is below .80.

## A.8 Conditional slopes with a standardised interaction

The interaction regressor is `z(ESG×Myopia)`, not the raw product. The derivative of
the standardised product with respect to `ESG` therefore carries a `1/SD` factor:

```
∂Ŷ/∂ESG = β_ESG + β_int · Myopia / SD(ESG×Myopia)
```

With `SD = 0.9752` at seed 42, the conditional slopes for substantive digitalization
are **+0.296** at −1 SD of myopia and **+0.033** at +1 SD, an attenuation of 89%.
v2.0 omitted the divisor and reported +0.292 and +0.036 with 88%. Figure 2 and
manuscript Section 5.3 use the corrected formula. `_simple_slope` takes the divisor
as the `sd_product` argument.
