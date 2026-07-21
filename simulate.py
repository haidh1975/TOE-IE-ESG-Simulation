"""
=============================================================================
TOE-IE-ESG Framework: Calibration-Based Simulation
=============================================================================
Paper  : "An integrated TOE-IE-ESG framework linking ESG performance and
          managerial cognition to digital transformation quality in SMEs"
Journal: Discover Sustainability (Springer Nature)
Authors: Nguyen Tien Minh · Do Huu Hai (corresponding)
ORCID  : 0000-0001-5811-7154
=============================================================================

PURPOSE
-------
This script generates the calibrated reference dataset (N = 500 simulated
SMEs) used to illustrate the internal coherence of the Extended TOE-IE-ESG
Framework. All data-generating parameters are anchored to published empirical
benchmarks from three anchor studies (see Section 4.1 and Appendix A of the
manuscript). The outputs are ILLUSTRATIVE — they are NOT independent empirical
evidence for the hypotheses in actual SME populations.

ANCHOR STUDIES
--------------
[1] Ramos-Vecino et al. (2026). Sustain Technol Entrep, 5, 100136.
    β(IndivF → Dig) ≈ 0.302 ; β(Dig → Perf) ≈ 0.549
    AVE(OpPerf) ≈ 0.477    ; CR(OpPerf)  ≈ 0.864
[4] Guo et al. (2024). China A-share firms, OLS with firm FE.
    β(ESG → SubstInnov) ≈ 0.11  ; β(Myopia) ≈ −0.082
    β(ESG×Myopia)       ≈ −0.058 ; ESG mean = 4.11, SD = 0.72
    FC = −0.737·ln(Size) + 0.043·ln(Size)² − 0.040·Age  [Kaplan-Zingales]
[6] Nykänen et al. (2023). Finnish growth SMEs (N=8, qualitative).
    ≈ 50% opportunity-dominant schema in conceptual utility & procedural data.

USAGE
-----
    python simulate.py                  # run full pipeline, save outputs
    python simulate.py --seed 99        # reproducible run with custom seed
    python simulate.py --n 1000         # larger sample
    python simulate.py --sensitivity    # also run sensitivity analysis
    python simulate.py --help           # show all options

OUTPUTS (saved to ./outputs/)
-------
    reference_dataset.csv      – the 500-firm simulated dataset
    descriptives.csv           – descriptive statistics (Table 2 in paper)
    correlations.csv           – Pearson correlation matrix (Table 3)
    ols_results.txt            – OLS regression Models 1–4 (Tables 5–8)
    measurement_check.csv      – PLS-SEM calibration check (Table 4)
    sensitivity_results.csv    – sensitivity analysis results (Appendix A.4)
    figures/                   – moderation plots (Figures 2, 3, 4)
=============================================================================
"""

import argparse
import os
import warnings
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

warnings.filterwarnings("ignore")

# ─── CLI ─────────────────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        description="TOE-IE-ESG Calibration-Based Simulation"
    )
    parser.add_argument("--seed",        type=int,   default=42,
                        help="Random seed (default: 42)")
    parser.add_argument("--n",           type=int,   default=500,
                        help="Number of simulated firms (default: 500)")
    parser.add_argument("--sensitivity", action="store_true",
                        help="Run sensitivity analysis (±20%% perturbation × 500 reps)")
    parser.add_argument("--outdir",      type=str,   default="outputs",
                        help="Output directory (default: ./outputs)")
    return parser.parse_args()


# ─── STEP 1: Generate exogenous variables ────────────────────────────────────
def generate_exogenous(n, rng):
    """
    Generate all exogenous variables according to Appendix A.3, Step 1.

    Distributions are calibrated to anchor-study descriptive statistics:
      ESG         : N(4.24, 0.65²) truncated [1, 9]  — Guo et al. [4]
      Myopia      : Half-normal(σ=0.091) bounded [0.01, 0.40] — Guo et al. [4]
      IndivF      : N(3.09, 0.87²) bounded [1, 5] — Ramos-Vecino et al. [1]
      OrgF        : N(3.20, 0.80²) bounded [1, 5] — Ramos-Vecino et al. [1]
      ln_Size     : N(3.50, 0.80²)  — employees (log-transformed)
      Age         : Gamma(shape=2, scale=8) — years since founding
    All exogenous variables are generated as approximately independent
    (|r| < 0.05 by construction).
    """
    def trunc_normal(mu, sigma, lo, hi, size):
        a, b = (lo - mu) / sigma, (hi - mu) / sigma
        return stats.truncnorm(a, b, loc=mu, scale=sigma).rvs(size=size, random_state=rng)

    ESG     = trunc_normal(4.24, 0.65, 1.0, 9.0, n)
    Myopia  = np.abs(rng.normal(0, 0.091, n)).clip(0.01, 0.40)
    IndivF  = trunc_normal(3.09, 0.87, 1.0, 5.0, n)
    OrgF    = trunc_normal(3.20, 0.80, 1.0, 5.0, n)
    ln_Size = rng.normal(3.50, 0.80, n)
    Age     = rng.gamma(shape=2, scale=8, size=n)

    return ESG, Myopia, IndivF, OrgF, ln_Size, Age


# ─── STEP 2: Compute Financing Constraints ───────────────────────────────────
def compute_fc(ln_Size, Age):
    """
    Kaplan-Zingales index following Guo et al. [4]:
        FC = −0.737·ln(Size) + 0.043·ln(Size)² − 0.040·Age
    Standardized to mean=0, SD=1.
    """
    FC_raw = -0.737 * ln_Size + 0.043 * ln_Size**2 - 0.040 * Age
    return (FC_raw - FC_raw.mean()) / FC_raw.std()


# ─── STEP 3: Generate endogenous variables ───────────────────────────────────
def generate_endogenous(ESG, Myopia, IndivF, OrgF, FC, rng, n,
                        scale=1.0):
    """
    Generate endogenous variables (Appendix A.3, Step 2).
    All inputs are standardized before structural equations.
    Coefficients anchored to Guo et al. [4] and Ramos-Vecino et al. [1].
    'scale' parameter is used for sensitivity analysis (±20% perturbation).
    """
    # Standardize exogenous inputs
    def z(x): return (x - x.mean()) / x.std()
    esg = z(ESG); myopia = z(Myopia); indivf = z(IndivF)
    orgf = z(OrgF); fc = z(FC)

    # ── Substantive Digitalization ──────────────────────────────────────────
    # Anchored to: Guo et al. [4] β_ESG ≈ 0.11, β_Myopia ≈ −0.082,
    #              β_ESG×Myopia ≈ −0.058; Ramos-Vecino et al. [1] β_IndivF ≈ 0.302
    coef_SD = {
        "ESG":        0.110 * scale,
        "Myopia":    -0.082 * scale,
        "IndivF":     0.300 * scale,
        "OrgF":       0.060 * scale,
        "FC":        -0.188 * scale,   # Guo et al. [4] financing channel
        "ESG_Myopia":-0.058 * scale,
        "ESG_IndivF": 0.115 * scale,
    }
    sigma_SD = np.sqrt(0.85)   # calibrated to R² ≈ 0.15 baseline
    SubstDig = (
          coef_SD["ESG"]        * esg
        + coef_SD["Myopia"]     * myopia
        + coef_SD["IndivF"]     * indivf
        + coef_SD["OrgF"]       * orgf
        + coef_SD["FC"]         * fc
        + coef_SD["ESG_Myopia"] * (esg * myopia)
        + coef_SD["ESG_IndivF"] * (esg * indivf)
        + rng.normal(0, sigma_SD, n)
    )
    SubstDig = SubstDig * 0.58 + 2.75   # rescale to mean≈2.75, SD≈0.58

    # ── Strategic Digitalization ─────────────────────────────────────────────
    # Front-end / compliance-oriented adoption; myopia slightly positive
    coef_StD = {
        "ESG":        0.043 * scale,
        "Myopia":     0.005 * scale,
        "IndivF":     0.085 * scale,
        "ESG_Myopia": 0.037 * scale,   # H3b: marginal positive
    }
    sigma_StD = np.sqrt(0.92)
    StratDig = (
          coef_StD["ESG"]        * esg
        + coef_StD["Myopia"]     * myopia
        + coef_StD["IndivF"]     * indivf
        + coef_StD["ESG_Myopia"] * (esg * myopia)
        + rng.normal(0, sigma_StD, n)
    )
    StratDig = StratDig * 0.71 + 3.29   # rescale to mean≈3.29, SD≈0.71

    # ── Operational Performance ──────────────────────────────────────────────
    # Anchored to Ramos-Vecino et al. [1] β_Dig ≈ 0.549
    sd_z = z(SubstDig); strd_z = z(StratDig)
    OpPerf = (
          0.549 * scale * sd_z
        + 0.094 * scale * strd_z
        + 0.104 * scale * indivf
        + rng.normal(0, np.sqrt(0.63), n)
    )
    OpPerf = OpPerf * 0.65 + 3.50   # rescale to realistic mean

    return SubstDig, StratDig, OpPerf


# ─── STEP 4: Generate multi-item construct scores ────────────────────────────
def generate_items(latent, n_items, loading, rng):
    """
    Generate n_items observed indicators for a latent variable.
    x_ij = loading * L_i + sqrt(1 - loading²) * ε_ij
    where ε_ij ~ N(0,1), so Var(x_ij) = 1 and
    Cor(x_ij, x_ik) = loading² = AVE.
    Returns composite mean score.
    """
    items = np.column_stack([
        loading * latent + np.sqrt(1 - loading**2) * rng.normal(0, 1, len(latent))
        for _ in range(n_items)
    ])
    return items.mean(axis=1)


# ─── STEP 5: Build interaction terms ─────────────────────────────────────────
def mean_center_interact(a, b):
    """Mean-centered product interaction term."""
    ac = a - a.mean()
    bc = b - b.mean()
    return ac * bc


# ─── Assemble dataset ─────────────────────────────────────────────────────────
def build_dataset(n=500, seed=42, scale=1.0):
    """
    Full data-generation pipeline (Appendix A.3, Steps 1–5).
    Returns a pandas DataFrame with all variables.
    """
    rng = np.random.default_rng(seed)

    # Step 1
    ESG, Myopia, IndivF, OrgF, ln_Size, Age = generate_exogenous(n, rng)

    # Step 2
    FC = compute_fc(ln_Size, Age)

    # Step 3
    SubstDig, StratDig, OpPerf = generate_endogenous(
        ESG, Myopia, IndivF, OrgF, FC, rng, n, scale=scale
    )

    # Step 4 — composite mean scores (calibrated loadings ≈ 0.80 → AVE ≈ 0.64)
    ESG_c       = generate_items(ESG,      1, 1.00, rng)   # single-item index
    SubstDig_c  = generate_items(SubstDig, 5, 0.80, rng)   # 5 items
    StratDig_c  = generate_items(StratDig, 4, 0.80, rng)   # 4 items
    IndivF_c    = generate_items(IndivF,   4, 0.80, rng)   # 4 items
    OrgF_c      = generate_items(OrgF,     3, 0.78, rng)   # 3 items
    OpPerf_c    = generate_items(OpPerf,   7, 0.70, rng)   # 7 items (AVE≈0.49)

    # Step 5 — interaction terms (mean-centered)
    ESG_x_Myopia = mean_center_interact(ESG_c, Myopia)
    ESG_x_IndivF = mean_center_interact(ESG_c, IndivF_c)

    df = pd.DataFrame({
        # Exogenous
        "ESG":            ESG_c,
        "Myopia":         Myopia,
        "IndivF":         IndivF_c,
        "OrgF":           OrgF_c,
        "ln_Size":        ln_Size,
        "Age":            Age,
        # Mediator
        "FC":             FC,
        # Endogenous
        "SubstDig":       SubstDig_c,
        "StratDig":       StratDig_c,
        "OpPerf":         OpPerf_c,
        # Interaction terms
        "ESG_x_Myopia":   ESG_x_Myopia,
        "ESG_x_IndivF":   ESG_x_IndivF,
    })
    return df


# ─── Descriptive statistics ───────────────────────────────────────────────────
def compute_descriptives(df):
    cols = ["ESG","Myopia","IndivF","OrgF","FC","SubstDig","StratDig","OpPerf"]
    desc = df[cols].describe().T[["mean","std","min","max"]]
    desc.columns = ["Mean","SD","Min","Max"]
    return desc.round(3)


# ─── Correlation matrix ───────────────────────────────────────────────────────
def compute_correlations(df):
    cols = ["ESG","Myopia","IndivF","OrgF","FC","SubstDig","StratDig","OpPerf"]
    return df[cols].corr().round(3)


# ─── Measurement calibration check ───────────────────────────────────────────
def compute_measurement_check(df):
    """
    Compute Cronbach's alpha and AVE proxies for each multi-item construct.
    This is a CALIBRATION VALIDATION CHECK (Appendix A.3, Step 4) —
    NOT an independent measurement instrument assessment.
    """
    rng2 = np.random.default_rng(999)
    constructs = {
        "SubstDig (5 items)": {"latent": df["SubstDig"], "n_items": 5, "loading": 0.80},
        "StratDig (4 items)": {"latent": df["StratDig"], "n_items": 4, "loading": 0.80},
        "IndivF   (4 items)": {"latent": df["IndivF"],   "n_items": 4, "loading": 0.80},
        "OrgF     (3 items)": {"latent": df["OrgF"],     "n_items": 3, "loading": 0.78},
        "OpPerf   (7 items)": {"latent": df["OpPerf"],   "n_items": 7, "loading": 0.70},
    }
    rows = []
    for name, cfg in constructs.items():
        items = np.column_stack([
            cfg["loading"] * cfg["latent"].values
            + np.sqrt(1 - cfg["loading"]**2) * rng2.normal(0, 1, len(df))
            for _ in range(cfg["n_items"])
        ])
        k     = cfg["n_items"]
        alpha = _cronbach_alpha(items)
        ave   = cfg["loading"]**2
        cr    = (k * cfg["loading"])**2 / ((k * cfg["loading"])**2 + k * (1 - ave))
        rows.append({
            "Construct": name,
            "Items": k,
            "Loading (avg)": round(cfg["loading"], 3),
            "Cronbach α":    round(alpha, 3),
            "CR":            round(cr, 3),
            "AVE":           round(ave, 3),
            "Threshold α≥.70": "✔" if alpha >= 0.70 else "✘",
            "Threshold CR≥.85":"✔" if cr    >= 0.85 else "✘",
            "Threshold AVE≥.50":"✔" if ave   >= 0.50 else "✘",
        })
    return pd.DataFrame(rows)


def _cronbach_alpha(items):
    """Compute Cronbach's alpha from item matrix."""
    k = items.shape[1]
    item_vars = items.var(axis=0, ddof=1).sum()
    total_var = items.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - item_vars / total_var)


# ─── OLS Models ───────────────────────────────────────────────────────────────
def run_ols_models(df):
    """
    Four OLS models following the structural architecture
    of Ramos-Vecino et al. [1] and Guo et al. [4].

    Model 1 : SubstDig ~ ESG + Myopia + IndivF + OrgF + FC   (baseline)
    Model 2 : SubstDig ~ Model1 + ESG×Myopia + ESG×IndivF    (moderation)
    Model 3 : OpPerf   ~ SubstDig + StratDig + IndivF         (performance)
    Model 4 : SubstDig ~ ESG + FC + IndivF + OrgF (FC mediation, H1c)
    """
    # Standardize continuous predictors
    def s(col): return (df[col] - df[col].mean()) / df[col].std()
    dfs = pd.DataFrame({
        "SubstDig":     s("SubstDig"),
        "StratDig":     s("StratDig"),
        "OpPerf":       s("OpPerf"),
        "ESG":          s("ESG"),
        "Myopia":       s("Myopia"),
        "IndivF":       s("IndivF"),
        "OrgF":         s("OrgF"),
        "FC":           s("FC"),
        "ESG_x_Myopia": s("ESG_x_Myopia"),
        "ESG_x_IndivF": s("ESG_x_IndivF"),
    })

    results = {}

    # Model 1 — baseline
    m1 = smf.ols(
        "SubstDig ~ ESG + Myopia + IndivF + OrgF + FC", data=dfs
    ).fit(cov_type="HC3")
    results["Model1_SubstDig_Baseline"] = m1

    # Model 2 — with moderation interactions
    m2 = smf.ols(
        "SubstDig ~ ESG + Myopia + IndivF + OrgF + FC "
        "+ ESG_x_Myopia + ESG_x_IndivF", data=dfs
    ).fit(cov_type="HC3")
    results["Model2_SubstDig_Moderation"] = m2

    # Model 2b — StratDig (for H3b quality-quantity trade-off)
    m2b = smf.ols(
        "StratDig ~ ESG + Myopia + IndivF + ESG_x_Myopia", data=dfs
    ).fit(cov_type="HC3")
    results["Model2b_StratDig_Moderation"] = m2b

    # Model 3 — Operational Performance (H2 mediation)
    m3 = smf.ols(
        "OpPerf ~ SubstDig + StratDig + IndivF + ESG", data=dfs
    ).fit(cov_type="HC3")
    results["Model3_OpPerf"] = m3

    # Model 4 — FC mediation path (H1c)
    m4a = smf.ols("FC ~ ESG", data=dfs).fit(cov_type="HC3")
    m4b = smf.ols("SubstDig ~ ESG + FC + IndivF + OrgF", data=dfs).fit(cov_type="HC3")
    results["Model4a_FC_on_ESG"]          = m4a
    results["Model4b_SubstDig_with_FC"]   = m4b

    return results


def format_ols_summary(model_results):
    """Format OLS results into a readable text table."""
    lines = []
    lines.append("=" * 70)
    lines.append("OLS REGRESSION RESULTS — TOE-IE-ESG Calibration Illustration")
    lines.append("NOTE: All results are calibration-based, NOT empirical confirmations.")
    lines.append("=" * 70)
    for name, res in model_results.items():
        lines.append(f"\n{'─'*70}")
        lines.append(f"  {name}")
        lines.append(f"  N = {int(res.nobs)}  |  R² = {res.rsquared:.3f}  |  Adj-R² = {res.rsquared_adj:.3f}")
        lines.append(f"  F({int(res.df_model)}, {int(res.df_resid)}) = {res.fvalue:.2f}  p = {res.f_pvalue:.4f}")
        lines.append(f"{'─'*70}")
        lines.append(f"  {'Variable':<22} {'β':>8} {'SE':>8} {'t':>8} {'p':>8}  Sig.")
        lines.append(f"  {'-'*22} {'-'*8} {'-'*8} {'-'*8} {'-'*8}  ----")
        for var in res.params.index:
            b   = res.params[var]
            se  = res.bse[var]
            t   = res.tvalues[var]
            p   = res.pvalues[var]
            sig = "***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else "†" if p<0.10 else ""
            lines.append(f"  {var:<22} {b:>8.3f} {se:>8.3f} {t:>8.3f} {p:>8.4f}  {sig}")
    lines.append(f"\n{'='*70}")
    lines.append("Significance: *** p<.001  ** p<.01  * p<.05  † p<.10  (HC3 robust SE)")
    lines.append("All continuous predictors standardized (mean=0, SD=1).")
    lines.append("Interaction terms are mean-centered products of standardized variables.")
    return "\n".join(lines)


# ─── Sensitivity Analysis ─────────────────────────────────────────────────────
def run_sensitivity(n=500, n_reps=500, seed=42, perturb=0.20):
    """
    Appendix A.4 — Sensitivity analysis.
    Vary all structural coefficients simultaneously by ±perturb (default ±20%)
    across n_reps Monte Carlo replications. Record directional stability
    (% of replications where coefficient sign matches baseline).
    """
    print(f"\nRunning sensitivity analysis: {n_reps} replications × ±{int(perturb*100)}% perturbation...")
    rng_main = np.random.default_rng(seed + 1000)

    # Hypotheses and their expected directions
    hypotheses = {
        "H1a: β(ESG → SubstDig)":        ("ESG",         "SubstDig", ">0"),
        "H1b: β(ESG → StratDig)":        ("ESG",         "StratDig", ">0"),
        "H3a: β(ESG×Myopia → SubstDig)": ("ESG_x_Myopia","SubstDig", "<0"),
        "H3b: β(ESG×Myopia → StratDig)": ("ESG_x_Myopia","StratDig", ">0"),
        "H4:  β(ESG×IndivF → SubstDig)": ("ESG_x_IndivF","SubstDig", ">0"),
    }

    counters = {h: 0 for h in hypotheses}
    total    = {h: 0 for h in hypotheses}

    for rep in range(n_reps):
        scale = rng_main.uniform(1 - perturb, 1 + perturb)
        rep_seed = seed + rep + 1
        df_rep = build_dataset(n=n, seed=rep_seed, scale=scale)
        def s(col): return (df_rep[col] - df_rep[col].mean()) / df_rep[col].std()
        dfs = pd.DataFrame({c: s(c) for c in
              ["SubstDig","StratDig","ESG","Myopia","IndivF","OrgF","FC",
               "ESG_x_Myopia","ESG_x_IndivF"]})
        # SubstDig model
        m_sd = smf.ols(
            "SubstDig ~ ESG + Myopia + IndivF + OrgF + FC + ESG_x_Myopia + ESG_x_IndivF",
            data=dfs).fit()
        # StratDig model
        m_st = smf.ols(
            "StratDig ~ ESG + Myopia + IndivF + ESG_x_Myopia",
            data=dfs).fit()

        for h, (pred, dep, direction) in hypotheses.items():
            m = m_sd if dep == "SubstDig" else m_st
            if pred in m.params:
                b = m.params[pred]
                total[h] += 1
                if direction == ">0" and b > 0:
                    counters[h] += 1
                elif direction == "<0" and b < 0:
                    counters[h] += 1

    rows = []
    for h in hypotheses:
        pct = 100 * counters[h] / total[h] if total[h] > 0 else 0
        stability = "High" if pct >= 90 else "Moderate" if pct >= 75 else "Low"
        rows.append({
            "Hypothesis":         h,
            "Replications":       total[h],
            "Directionally stable": counters[h],
            "Stability (%)":      round(pct, 1),
            "Assessment":         stability,
        })
    return pd.DataFrame(rows)


# ─── Save outputs ─────────────────────────────────────────────────────────────
def save_outputs(df, desc, corr, meas, ols_results, outdir, sensitivity_df=None):
    os.makedirs(outdir, exist_ok=True)

    df.to_csv(f"{outdir}/reference_dataset.csv", index=False)
    desc.to_csv(f"{outdir}/descriptives.csv")
    corr.to_csv(f"{outdir}/correlations.csv")
    meas.to_csv(f"{outdir}/measurement_check.csv", index=False)

    with open(f"{outdir}/ols_results.txt", "w") as fh:
        fh.write(format_ols_summary(ols_results))

    if sensitivity_df is not None:
        sensitivity_df.to_csv(f"{outdir}/sensitivity_results.csv", index=False)

    print(f"\nOutputs saved to: ./{outdir}/")
    print(f"  reference_dataset.csv   ({len(df)} rows × {len(df.columns)} columns)")
    print(f"  descriptives.csv")
    print(f"  correlations.csv")
    print(f"  measurement_check.csv")
    print(f"  ols_results.txt")
    if sensitivity_df is not None:
        print(f"  sensitivity_results.csv")


# ─── Print summary ────────────────────────────────────────────────────────────
def print_summary(desc, corr, meas, ols_results):
    print("\n" + "="*70)
    print("DESCRIPTIVE STATISTICS")
    print("="*70)
    print(desc.to_string())

    print("\n" + "="*70)
    print("PEARSON CORRELATIONS  (upper triangle)")
    print("="*70)
    print(corr.to_string())

    print("\n" + "="*70)
    print("MEASUREMENT CALIBRATION CHECK")
    print("NOTE: Benchmarking against anchor studies, NOT instrument validation.")
    print("="*70)
    print(meas.to_string(index=False))

    print("\n" + format_ols_summary(ols_results))


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    args = parse_args()

    print("=" * 70)
    print("TOE-IE-ESG Calibration-Based Simulation")
    print(f"Seed: {args.seed}  |  N: {args.n}  |  Output: ./{args.outdir}/")
    print("IMPORTANT: All outputs are ILLUSTRATIVE, not empirical confirmations.")
    print("=" * 70)

    # Generate dataset
    print("\n[1/5] Generating calibrated reference dataset...")
    df = build_dataset(n=args.n, seed=args.seed)

    # Compute statistics
    print("[2/5] Computing descriptive statistics and correlations...")
    desc = compute_descriptives(df)
    corr = compute_correlations(df)

    print("[3/5] Running measurement calibration check...")
    meas = compute_measurement_check(df)

    print("[4/5] Running OLS regression models (HC3 robust SEs)...")
    ols_results = run_ols_models(df)

    # Optional sensitivity analysis
    sensitivity_df = None
    if args.sensitivity:
        print("[5/5] Running sensitivity analysis (500 replications × ±20%)...")
        sensitivity_df = run_sensitivity(n=args.n, seed=args.seed)
        print("\nSENSITIVITY ANALYSIS RESULTS")
        print(sensitivity_df.to_string(index=False))
    else:
        print("[5/5] Skipping sensitivity analysis (use --sensitivity to enable).")

    # Print and save
    print_summary(desc, corr, meas, ols_results)
    save_outputs(df, desc, corr, meas, ols_results, args.outdir, sensitivity_df)

    print("\n✔  Simulation complete.")
    print("    Cite this code: Do Huu Hai (2025). TOE-IE-ESG Simulation.")
    print("    OSF: https://osf.io/[OSF-ID]")


if __name__ == "__main__":
    main()
