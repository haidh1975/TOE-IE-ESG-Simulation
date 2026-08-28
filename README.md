# TOE-IE-ESG Framework — Calibration-Based Simulation (v2.0, AUTHORITATIVE)

> [!IMPORTANT]
> ### Authoritative source
> **`simulate.py` (v2.0) is the single authoritative source for every number in the
> manuscript.** Tables 2–9, Appendix Tables A2–A4 **and Figures 2–4** are all generated
> by this one script from one declared parameter set (`TARGETS`). No number in the
> paper is entered by hand.
>
> **Reproduce everything with one command:**
> ```bash
> python simulate.py --seed 42 --n 500 --all --reps 500
> ```
>
> This is a **calibration-based simulation, not an empirical study**. Every number is
> an illustrative output of an imposed data-generating structure and is not evidence
> about real SME populations.
>
> Version 1.0 is superseded and must not be used: Revision-3 reviewers correctly
> established that it did not reproduce the manuscript. See “Version 2.0” below.

Replication package for:

> Nguyen Tien Minh & Do Huu Hai. *An integrated TOE-IE-ESG framework linking ESG
> performance and managerial cognition to digital transformation quality in SMEs.*
> **Discover Sustainability** (Springer Nature). Submission ID 94739b1f-6b60-48f4-880a-088c7e4839d7.
> Corresponding author ORCID: 0000-0001-5811-7154

Repository: https://github.com/haidh1975/TOE-IE-ESG-Simulation

---

## Version 2.0 — what changed from v1.0 and why

Revision-3 reviewers correctly established that v1.0 outputs did **not** match the
manuscript. All causes were diagnosed and fixed:

| # | Problem in v1.0 | Fix in v2.0 |
|---|---|---|
| 1 | Construct scores were generated, rescaled, then **re-generated as noisy item means** and analysed. This second measurement layer attenuated every coefficient (reliability ≈ .75) and shifted all means, so fitted estimates could never equal imposed parameters. | Regressions are estimated on the **generated construct scores** — the level at which anchor parameters are defined. Item indicators are a **separate layer used only for the measurement check** and are never used in estimation. Imposed *and* recovered parameters are both reported. |
| 2 | **`ESG → FC` was never encoded.** FC depended only on size and age, both independent of ESG, so the true effect was exactly zero and H1c could not hold. | The H1c mechanism is now **encoded ex ante and explicitly** (`FC_ESG = −0.180`), justified by sustainability-linked credit access (Guo et al. 2026). The indirect effect is **bootstrapped directly** (5,000 draws), not inferred. |
| 3 | Index called **Kaplan-Zingales**. | It is the **SA index** (Hadlock & Pierce 2010). Corrected. `Size = ln(total assets)`, `Age = years since founding`. |
| 4 | **HTMT reported but never computed.** | HTMT is now computed from the retained item matrix. |
| 5 | Single-item **ESG appeared in α/CR/AVE**. | ESG is excluded; α, CR and AVE are undefined for one indicator. |
| 6 | Sensitivity applied **one common multiplier** to all coefficients and reported only sign retention. | Each coefficient is perturbed **independently**; the script reports **empirical power, mean recovered β, bias, RMSE and 95% CI coverage**, plus a power curve across sample sizes. |
| 7 | `TechF`, `EnvF` and the controls appeared in manuscript equations but **were never generated**. | All are generated and entered in the fitted models. |
| 8 | Text said **"clustered at firm level"**; code used HC3. | Everything now says **HC3 heteroskedasticity-robust**. |

A collinearity error was also removed: `SA_index` is a deterministic function of
`lnSize` and `Age`, so those two no longer enter the FC equation alongside it.

---

## Headline result you should not miss

At **n = 500**, only **H1c** and **H2** are reliably recovered (power = 1.00).
The interaction hypotheses are **not** reliably detectable:

| Hypothesis | Empirical power at n = 500 |
|---|---|
| H1a ESG → Substantive digitalization | 0.65 |
| H1b ESG → Strategic digitalization | 0.19 |
| H1c ESG → Financing constraints | **1.00** |
| H2 Substantive dig. → Performance | **1.00** |
| H3a ESG × Myopia → Substantive dig. | 0.27 |
| H3b ESG × Myopia → Strategic dig. | 0.13 |
| H4 ESG × IndivF → Substantive dig. | 0.74 |

These figures come from `tableA3_monte_carlo_performance.csv`, in which every
coefficient is perturbed independently, so they incorporate parameter uncertainty as
well as sampling variability. `tableA4_power_curve.csv` holds the coefficients fixed
at their imposed values and therefore reports slightly higher power at the same
n = 500 (H1a .70, H1b .21, H3a .28, H3b .17, H4 .77). Both are correct; they answer
different questions, and the manuscript uses the perturbed values because they are
the more conservative of the two.

A single replication can cross p < .05 by a favourable draw when power is this low,
so **Table 9 decisions are power-aware**: a path is called reliably recovered only if
it is significant *and* power ≥ .80. This is a substantive finding — future primary
studies testing these interactions need roughly **n ≈ 2,000–4,000** (see `tableA4_power_curve.csv`).

---

## Repository layout

```
simulate.py                     authoritative script — generates everything
requirements.txt                dependencies
README.md                       this file
LICENSE                         MIT
CITATION.cff                    citation metadata
docs/Appendix_A_Technical_Notes.md   design decision, imposed parameters, generation steps
outputs/                        11 generated tables + reference dataset
outputs/figures/                Figures 2–4 (PNG 300 dpi + PDF)
```

---

## Quick start

```bash
git clone https://github.com/haidh1975/TOE-IE-ESG-Simulation.git
cd TOE-IE-ESG-Simulation
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python simulate.py --seed 42 --n 500 --all --reps 500
```

That single command reproduces **every** manuscript table, appendix table and figure.

| Flag | Effect |
|---|---|
| `--seed 42` | Seed used for the manuscript (default) |
| `--n 500` | Sample size used for the manuscript (default) |
| `--sensitivity` | Monte Carlo performance study (power/bias/RMSE/coverage) |
| `--power` | Power curve across n = 250…4,000 |
| `--all` | Both of the above |
| `--reps 500` | Monte Carlo replications |

Runtime for `--all --reps 500`: roughly 10–20 minutes.

---

## Output → manuscript map

| Output file | Manuscript element |
|---|---|
| `reference_dataset.csv` | The N = 500 analysed dataset |
| `table2_descriptives.csv` | Table 2 |
| `table3_correlations.csv` | Table 3 |
| `table4_measurement_check.csv` | Table 4 (α, CR, AVE) |
| `table4b_htmt.csv` | Table 4b (HTMT) |
| `tables5to8_ols_results.txt` | Tables 5–8 (Models M1–M5b) |
| `table8_indirect_effect.txt` | Bootstrapped ESG → FC → SubstDig |
| `table9_hypotheses.csv` | Table 9 (power-aware decisions) |
| `tableA2_imposed_parameters.csv` | Appendix Table A2 |
| `tableA3_monte_carlo_performance.csv` | Appendix Table A3 |
| `tableA4_power_curve.csv` | Appendix Table A4 |
| `figures/figure2_myopia_moderation.png/.pdf` | Figure 2 |
| `figures/figure3_mediation_path.png/.pdf` | Figure 3 |
| `figures/figure4_power_curve.png/.pdf` | Figure 4 |

---

## Design decision you should understand before reading the code

The anchor parameters are defined at construct level, so **regressions target the
generated construct scores**. The item layer exists only to show that the calibration
reproduces anchor-study reliability benchmarks. Analysing noisy item means instead
would attenuate every coefficient — that was exactly the v1.0 error. Both imposed and
recovered parameters are reported so recovery can be verified directly
(`tableA3_monte_carlo_performance.csv`: all biases ≤ .005 except the standardised
mediator path, a known scaling artefact discussed in the manuscript).

---

## Anchor studies

| Source | Parameters used |
|---|---|
| Ramos-Vecino et al. (2026), *Sustain Technol Entrep* 5:100136 | β(IndivF→Dig) ≈ .302; β(Dig→Perf) ≈ .549 |
| Guo C, Wang Y, Yang Z (2026), *Energy Convers Manag X* 31:101947 | β(ESG→Substantive) ≈ .11; β(Myopia) ≈ −.082; β(ESG×Myopia) ≈ −.058 |
| Nykänen N, Vuori T, Luoma J (2026), *Long Range Plan* 59:102637 | ≈ 50% opportunity-dominant cognitive schemas |
| Hadlock & Pierce (2010), *Rev Financ Stud* 23(5):1909–1940 | SA index |

## Requirements

`numpy≥1.24`, `scipy≥1.10`, `pandas≥2.0`, `statsmodels≥0.14`, `matplotlib≥3.7` — Python 3.9+.

## Citation

```bibtex
@article{NguyenDo2025TOEIEESG,
  title   = {An integrated TOE-IE-ESG framework linking ESG performance and
             managerial cognition to digital transformation quality in
             small and medium-sized enterprises},
  author  = {Nguyen, Tien Minh and Do, Huu Hai},
  journal = {Discover Sustainability},
  year    = {2025},
  url     = {https://github.com/haidh1975/TOE-IE-ESG-Simulation}
}
```

## License

MIT — see `LICENSE`.

## Contact

Do Huu Hai (corresponding author) · ORCID 0000-0001-5811-7154 · haidh1975@gmail.com
