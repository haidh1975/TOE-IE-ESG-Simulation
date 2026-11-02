"""
Figure 1 — Extended TOE-IE-ESG conceptual framework.

Editable vector source. This is a CONCEPTUAL figure: it states the proposed
relationships and their expected directions. It is not a diagram of the
data-generating process, the regression equations, or which hypotheses the
simulation supported. No coefficients, p-values, power values or support
statuses appear here; those belong in Tables 5-9.

The original architecture is preserved: left-to-right flow, the same boxes and
colours, and the combined central construct Digital Transformation
(Substantive / Strategic). The substantive/strategic distinction is carried by
path labels rather than by splitting the construct.

Conventions
  solid arrow     : proposed direct relationship
  dashed connector: proposed moderation acting on a relationship
  small grey node : proposed mediating mechanism (H1c)
  grey note       : proposition not tested in the current design (H5)

No figure number, title or caption is embedded; those belong in the manuscript.
"""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Patch
from matplotlib.lines import Line2D

GREEN="#1B5E20"; BLUE="#1F4E79"; RED="#B22222"; PURPLE="#5B2C6F"
TEAL="#0E6B63"; GREY="#777777"
plt.rcParams.update({"font.family":"sans-serif","font.sans-serif":["DejaVu Sans"]})

fig, ax = plt.subplots(figsize=(13.4, 8.0))
ax.set_xlim(0, 134); ax.set_ylim(0, 80); ax.axis("off")

def box(x,y,w,h,title,sub,ec,fc,fs=10):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.6,rounding_size=1.2",
                                ec=ec,fc=fc,lw=1.6))
    ax.text(x+w/2,y+h/2+1.7,title,ha="center",va="center",fontsize=fs,
            fontweight="bold",color=ec)
    ax.text(x+w/2,y+h/2-2.2,sub,ha="center",va="center",fontsize=7.6,
            style="italic",color="#555")

# ---- constructs: unchanged from the original architecture -------------------
box(  3, 63, 26, 10, "ESG Performance",      "(Environmental Driver)",        GREEN, "#EAF5EA")
box(  3, 49, 26, 10, "Individual Factor",    "(Digital Skills & Leadership)", BLUE,  "#E8F0FB")
box(  3, 35, 26, 10, "Organizational Factor","(Size, Resources, Maturity)",   BLUE,  "#E8F0FB")
box(  3, 21, 26, 10, "Technological Factor", "(Compatibility, Ease of Use)",  BLUE,  "#E8F0FB")
box(  3,  7, 26, 10, "Environmental Factor", "(Competition, Regulation)",     BLUE,  "#E8F0FB")
box( 53, 36, 32, 13, "Digital Transformation","(Substantive / Strategic)",    BLUE,  "#D6E4F5", fs=11)
box( 53,  5, 32, 11, "Managerial Myopia",    "(Short-term Orientation)",      RED,   "#FBEAEA")
box(102, 36, 29, 13, "Operational Performance","(Financial & Process)",       PURPLE,"#F2E8F7")

def arrow(p1,p2,color,lw=1.7,ls="-",rad=0.0):
    ax.add_patch(FancyArrowPatch(p1,p2,arrowstyle="-|>",color=color,lw=lw,
                 linestyle=ls,mutation_scale=14,shrinkA=2,shrinkB=2,
                 connectionstyle=f"arc3,rad={rad}"))
def lab(x,y,t,color,fs=8.8,ec="none"):
    ax.text(x,y,t,fontsize=fs,color=color,ha="center",va="center",fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.26",fc="white",ec=ec,alpha=.95,
                      lw=1.0 if ec!="none" else 0))

# ---- H1c: compact mediating mechanism, routed clear of the direct paths -----
ax.add_patch(FancyBboxPatch((36,67.5),17,7.0,boxstyle="round,pad=0.45,rounding_size=0.9",
             ec=GREY,fc="#F4F4F4",lw=1.2))
ax.text(44.5,71.0,"Financing\nConstraints",ha="center",va="center",fontsize=8.0,
        fontweight="bold",color="#444",linespacing=1.3)
arrow((29,70.5),(36,71.0),GREY,1.5)
arrow((53,68.5),(58,49.5),GREY,1.5,rad=0.14)
lab(32.5,73.0,"(\u2212)",GREY,fs=8.4)
lab(58.5,60.0,"(\u2212)",GREY,fs=8.4)
lab(45.0,64.5,"H1c: indirect (+)",GREY,fs=8.2)

# ---- direct proposed relationships ------------------------------------------
arrow((29,66.5),(53,46.5),GREEN,2.2)
lab(43.5,55.5,"H1a (+)  substantive",GREEN)
arrow((29,63.5),(53,42.0),GREEN,2.2,rad=-0.10)
lab(40.0,47.0,"H1b (+)  strategic",GREEN)
for y0,y1 in [(53,42.5),(39,40.0),(25,38.0),(11,37.0)]:
    arrow((29,y0),(53,y1),BLUE,1.4)
arrow((85,42.5),(102,42.5),PURPLE,2.2)
lab(93.5,44.6,"H2 (+)",PURPLE)

# ---- proposed moderations (dashed) ------------------------------------------
arrow((62,16),(62,35),RED,1.7,ls=(0,(5,3)))
lab(62,28.5,"H3a (\u2212)  substantive",RED)
arrow((76,16),(76,35),RED,1.7,ls=(0,(5,3)))
lab(77,22.0,"H3b (+)  strategic",RED)
arrow((29,51.5),(47.0,44.5),TEAL,1.7,ls=(0,(5,3)),rad=-0.26)
lab(37.5,40.5,"H4 (+)  substantive",TEAL)

# ---- legend and H5 note ------------------------------------------------------
handles=[Line2D([],[],color=GREEN,lw=2.2,label="Proposed direct relationship (hypothesised)"),
         Line2D([],[],color=BLUE,lw=1.4,label="Proposed direct relationship (unnumbered)"),
         Line2D([],[],color=RED,lw=1.7,ls=(0,(5,3)),label="Proposed moderation"),
         Line2D([],[],color=GREY,lw=1.5,label="Proposed mediating mechanism (H1c)"),
         Patch(fc="#EAF5EA",ec=GREEN,label="ESG driver"),
         Patch(fc="#E8F0FB",ec=BLUE,label="TOE-IE factors"),
         Patch(fc="#FBEAEA",ec=RED,label="Moderator: managerial myopia"),
         Patch(fc="#F2E8F7",ec=PURPLE,label="Outcome: operational performance")]
ax.legend(handles=handles,loc="lower right",bbox_to_anchor=(1.005,0.02),
          fontsize=7.6,framealpha=1,borderpad=0.7)

ax.add_patch(FancyBboxPatch((3,0.4),46,5.0,boxstyle="round,pad=0.4,rounding_size=0.8",
             ec=GREY,fc="#F7F7F7",lw=1.0,linestyle=(0,(4,2))))
ax.text(26,2.9,"H5 \u2014 proposed three-way conditional proposition;\n"
               "not tested in the current design.",
        ha="center",va="center",fontsize=7.6,color="#555",linespacing=1.35)
ax.text(53,2.0,"Signs denote expected theoretical directions, not estimated effects.",
        ha="left",va="center",fontsize=7.2,color="#777",style="italic")

fig.tight_layout(pad=0.4)
fig.savefig("Fig1_Conceptual_Draft.pdf")
fig.savefig("Fig1_Conceptual_Draft.eps",format="eps")
fig.savefig("Fig1_Conceptual_Draft.png",dpi=300)
plt.close(fig)
print("written: PDF, EPS, PNG")
