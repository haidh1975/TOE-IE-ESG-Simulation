# Appendix A — Technical Notes (v2.0, AUTHORITATIVE)

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

## A.4 Monte Carlo performance and power

Each coefficient is perturbed **independently** by Uniform(0.8, 1.2) over 500
replications. Reported per hypothesis: imposed mean, recovered mean, bias, RMSE,
empirical power, 95% CI coverage.

Recovery is essentially unbiased (|bias| ≤ .005) and coverage ≈ .95, except the
standardised mediator path (H1c), whose small bias is a scaling artefact of
standardising FC after generation.

**Empirical power at n = 500:** H1a .65 · H1b .19 · H1c 1.00 · H2 1.00 ·
H3a .27 · H3b .13 · H4 .74.

**Power curve** (`tableA4_power_curve.csv`) shows the interactions need roughly
n ≈ 2,000–4,000 to reach conventional power. Consequently Table 9 decisions are
**power-aware**: significance in a single draw is not treated as reliable recovery
when power is below .80.
