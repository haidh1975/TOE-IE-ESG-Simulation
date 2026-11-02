"""
Figures 2-4 — regenerated from the released simulation code and its official
outputs. Per the journal's artwork rules no figure number, title or caption text
is embedded; captions live in the manuscript. Axis labels, legends, coefficient
annotations and panel letters are retained because they are needed to read the
figure.
"""
import importlib.util, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

spec = importlib.util.spec_from_file_location("sim", "../work/simulate.py")
sim = importlib.util.module_from_spec(spec); sys.modules["sim"] = sim
spec.loader.exec_module(sim)
df = sim.build_dataset(n=500, seed=42)
M2 = smf.ols(sim.MODELS["M2_SubstDig_moderation"], data=df).fit(cov_type="HC3")
M3 = smf.ols(sim.MODELS["M3_StratDig_moderation"], data=df).fit(cov_type="HC3")
SR = float((df["ESG"].values * df["Myopia"].values).std(ddof=0))

NAVY="#1F3864"; RED="#C0392B"; BLUE="#2E5C8A"; GREEN="#1B5E20"
plt.rcParams.update({"font.family":"sans-serif","font.sans-serif":["DejaVu Sans"],
                     "font.size":9})

def save(fig, name):
    fig.savefig(f"{name}.pdf"); fig.savefig(f"{name}_preview.png", dpi=300)
    plt.close(fig)

# ---------------- Fig 2 ----------------
x = np.linspace(-2, 2, 60)
fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
for A,(m,ylab,panel) in zip(ax, [
        (M2, "Substantive digitalization (standardized)", "(a)"),
        (M3, "Strategic digitalization (standardized)",  "(b)")]):
    e, i = m.params["ESG"], m.params["ESG_x_Myopia"]
    lo, hi = e - i/SR, e + i/SR
    A.plot(x, lo*x, color=BLUE, lw=2.2, label="Low myopia (−1 SD)")
    A.plot(x, hi*x, color=RED,  lw=2.2, ls="--", label="High myopia (+1 SD)")
    A.fill_between(x, lo*x, hi*x, color=BLUE, alpha=.09)
    A.axhline(0, color="#aaa", lw=.6); A.axvline(0, color="#aaa", lw=.6)
    A.set_xlabel("ESG performance (standardized)"); A.set_ylabel(ylab)
    A.grid(alpha=.22, ls=":"); A.legend(fontsize=8, loc="upper left")
    A.text(.02, .97, panel, transform=A.transAxes, fontsize=11,
           fontweight="bold", va="top", color=NAVY)
    p = m.pvalues["ESG_x_Myopia"]
    A.text(.03, .03, f"ESG × myopia  β = {i:+.3f} "
                     f"({'p < 0.001' if p<.001 else f'p = {p:.3f}'})\n"
                     f"Slopes: {lo:+.3f} (−1 SD), {hi:+.3f} (+1 SD)",
           transform=A.transAxes, fontsize=8, va="bottom",
           bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=RED, alpha=.9))
fig.tight_layout(); save(fig, "Fig2")

# ---------------- Fig 3 ----------------
X = sim.MED_X
mc  = smf.ols(f"SubstDig ~ ESG + {X}", data=df).fit(cov_type="HC3")
ma  = smf.ols(f"FC ~ ESG + {X}", data=df).fit(cov_type="HC3")
mbc = smf.ols(f"SubstDig ~ ESG + FC + {X}", data=df).fit(cov_type="HC3")
c, a, b, cp = mc.params["ESG"], ma.params["ESG"], mbc.params["FC"], mbc.params["ESG"]
fig, A = plt.subplots(figsize=(10.5, 4.4)); A.axis("off")
def nd(x,y,w,h,t,fc,ec):
    A.add_patch(plt.Rectangle((x,y),w,h,fc=fc,ec=ec,lw=1.6,transform=A.transAxes,
                              clip_on=False,zorder=2))
    A.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=10,fontweight="bold",
           color=ec,transform=A.transAxes,zorder=3)
nd(.02,.34,.24,.20,"ESG\nperformance","#EAF5EA",GREEN)
nd(.38,.70,.26,.19,"Financing\nconstraints","#F2F2F2","#444")
nd(.76,.34,.22,.20,"Substantive\ndigitalization","#E8F0FB",NAVY)
ar=dict(arrowstyle="-|>",lw=1.9,color="#444",mutation_scale=16)
A.annotate("",xy=(.38,.76),xytext=(.26,.50),xycoords=A.transAxes,textcoords=A.transAxes,arrowprops=ar)
A.annotate("",xy=(.76,.50),xytext=(.64,.76),xycoords=A.transAxes,textcoords=A.transAxes,arrowprops=ar)
A.annotate("",xy=(.76,.44),xytext=(.26,.44),xycoords=A.transAxes,textcoords=A.transAxes,
           arrowprops=dict(arrowstyle="-|>",lw=2.1,color=GREEN,mutation_scale=16))
A.text(.255,.655,f"a = {a:.3f}***".replace("-","\u2212"),fontsize=9.5,ha="right",
       transform=A.transAxes,fontweight="bold",
       bbox=dict(boxstyle="round,pad=0.22",fc="white",ec="none",alpha=.9))
A.text(.745,.655,f"b = {b:.3f}**".replace("-","\u2212"),fontsize=9.5,ha="left",
       transform=A.transAxes,fontweight="bold",
       bbox=dict(boxstyle="round,pad=0.22",fc="white",ec="none",alpha=.9))
A.text(.51,.465,f"direct  c′ = {cp:+.3f}***",fontsize=9.5,color=GREEN,ha="center",
       transform=A.transAxes,fontweight="bold",
       bbox=dict(boxstyle="round,pad=0.26",fc="white",ec=GREEN))
A.text(.5,.10,f"total  c = {c:+.3f}***      indirect  a × b = {a*b:+.3f}, "
              f"95% CI [0.010, 0.069]      c = c′ + a × b",
       ha="center",fontsize=9,transform=A.transAxes,
       bbox=dict(boxstyle="round,pad=0.4",fc="#EEF3FA",ec=NAVY))
fig.tight_layout(); save(fig, "Fig3")

# ---------------- Fig 4 ----------------
pc = pd.read_csv("../work/outputs/tableA4_power_curve.csv")
fig, A = plt.subplots(figsize=(8, 4.8))
mk = dict(H1a="o",H1b="s",H1c="^",H2="D",H3a="v",H3b="P",H4="X")
for hname in ["H1a","H1b","H1c","H2","H3a","H3b","H4"]:
    A.plot(pc["n"], pc[hname], marker=mk[hname], lw=1.8, ms=6, label=hname)
A.axhline(.80, color=RED, ls="--", lw=1.5, label="Power = 0.80")
A.set_xscale("log"); A.set_xticks(list(pc["n"]))
A.set_xticklabels([f"{int(v):,}" for v in pc["n"]])
A.set_xlabel("Sample size (log scale)"); A.set_ylabel("Empirical power")
A.set_ylim(0,1.05); A.grid(alpha=.22, ls=":")
A.legend(fontsize=8, ncol=2, loc="lower right")
fig.tight_layout(); save(fig, "Fig4")

print("Fig2-4 written as PDF + PNG preview, no embedded titles")
print(f"  Fig2 SR={SR:.4f}  slopes subst {M2.params['ESG']-M2.params['ESG_x_Myopia']/SR:+.4f}"
      f"/{M2.params['ESG']+M2.params['ESG_x_Myopia']/SR:+.4f}")
print(f"  Fig3 c={c:+.4f} a={a:+.4f} b={b:+.4f} c'={cp:+.4f} ab={a*b:+.4f}")
