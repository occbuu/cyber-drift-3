"""Draw the two-phase publication overview of the PACT alert-certification layer.

The only decoration kept is the pair of dashed frames, because they carry
information: everything inside the first happens before deployment on known
traffic alone, everything inside the second happens while traffic is scored.
Boxes, rules and arrows are plain, monochrome and thin, which is what a method
figure in this literature looks like.  The layout comes from one grid, so both
rows share their margins and their gutter.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT_PDF = ROOT / "elsarticle_21" / "figures" / "fig_pact_overview.pdf"
OUT_PNG = ROOT / "elsarticle_21" / "figures" / "fig_pact_overview.png"

INK, MUTED, RULE = "#1A1A1A", "#4A4A4A", "#9A9A9A"
DECISION_FILL = "#F2F2F2"

LEFT, RIGHT = 0.035, 0.965
ROW1_Y, ROW2_Y, BOX_H = 0.615, 0.200, 0.225
STRIP_Y, STRIP_H = 0.048, 0.088


def track(count, gap):
    width = (RIGHT - LEFT - (count - 1) * gap) / count
    return [LEFT + i * (width + gap) for i in range(count)], width


def box(ax, x, y, w, h, number, title, body, *, fill="white", body_size=6.8):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="square,pad=0", linewidth=0.55,
        edgecolor=MUTED, facecolor=fill, zorder=2,
    ))
    ax.text(x + 0.010, y + h - 0.014, number, ha="left", va="top",
            fontsize=6.2, color=RULE, zorder=3)
    ax.text(x + w / 2, y + h * 0.63, title, ha="center", va="center",
            fontsize=8.0, color=INK, zorder=3)
    ax.text(x + w / 2, y + h * 0.27, body, ha="center", va="center",
            fontsize=body_size, color=MUTED, linespacing=1.45, zorder=3)


def arrow(ax, start, end, *, dashed=False):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=6.5, linewidth=0.5,
        color=MUTED, linestyle=(0, (2.5, 2)) if dashed else "-",
        shrinkA=0, shrinkB=0, zorder=3,
    ))


def note(ax, x, y, text, *, ha="center", boxed=False):
    ax.text(x, y, text, ha=ha, va="center", fontsize=6.4, color=MUTED,
            fontstyle="italic", zorder=4,
            bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none") if boxed else None)


plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "mathtext.fontset": "stix",
})

fig, ax = plt.subplots(figsize=(7.0, 3.9))
fig.patch.set_facecolor("white")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")


def phase(y0, y1, label, align="left"):
    ax.add_patch(FancyBboxPatch(
        (LEFT - 0.016, y0), RIGHT - LEFT + 0.032, y1 - y0,
        boxstyle="square,pad=0", linewidth=0.5, edgecolor=RULE,
        linestyle=(0, (4, 3)), facecolor="none", zorder=1,
    ))
    ax.text(LEFT if align == "left" else RIGHT, y1 - 0.028, label,
            ha=align, va="center", fontsize=7.6, color=INK, zorder=4)


phase(0.575, 0.925, "(a)  known-only training and calibration")
phase(0.022, 0.500, "(b)  deployment and monitoring", align="right")

# (a) evidence construction -------------------------------------------------
xs1, w1 = track(4, 0.026)
row1 = [
    ("1", "Deployment stream", "known and unknown flows;\nlabels hidden", 6.8),
    ("2", "Detector score", "any open-set detector;\nPCF: MD, RMD, 1-NN", 6.8),
    ("3", "Known-only split", "tuning half fixes the score;\ncalibration half, size $n$", 6.8),
    ("4", "Alert p-values", r"$p=\dfrac{1+\#\{s(X_j)\geq s(x)\}}{n+1}$", 7.2),
]
for x, (num, title, body, size) in zip(xs1, row1):
    box(ax, x, ROW1_Y, w1, BOX_H, num, title, body, body_size=size)
for x in xs1[:-1]:
    arrow(ax, (x + w1, ROW1_Y + BOX_H / 2), (x + w1 + 0.026, ROW1_Y + BOX_H / 2))

# (b) certification decision ------------------------------------------------
xs2, w2 = track(3, 0.068)
row2 = [
    ("5", "Feasibility gate",
     "$n \\geq n_{\\mathrm{marg}} = 1/(q\\hat\\pi) - 1$ ?\n"
     "$n \\geq n_{\\mathrm{cond}} \\approx \\log(L/\\delta)/(q\\hat\\pi)$ ?"),
    ("6", "Exchangeability audit", "$D_+ \\leq \\tau$ on verified\nknown traffic ?"),
    ("7", "Selection with a cap", "BH at $q$ on $\\tilde p_r$ (certified)\n"
                                  "or on $p$ (degraded), $\\leq L$ alerts"),
]
for x, (num, title, body) in zip(xs2, row2):
    box(ax, x, ROW2_Y, w2, BOX_H, num, title, body, fill=DECISION_FILL)
for x in xs2[:-1]:
    arrow(ax, (x + w2, ROW2_Y + BOX_H / 2), (x + w2 + 0.068, ROW2_Y + BOX_H / 2))
note(ax, xs2[0] + w2 + 0.034, ROW2_Y + BOX_H / 2 + 0.042, "feasible", boxed=True)
note(ax, xs2[1] + w2 + 0.034, ROW2_Y + BOX_H / 2 + 0.042, "pass", boxed=True)

# the candidate stream leaves box 4 and enters box 5 one phase below
turn_y = 0.540
centre1, centre5 = xs1[3] + w1 / 2, xs2[0] + w2 / 2
ax.plot([centre1, centre1], [ROW1_Y, turn_y], color=MUTED, linewidth=0.5, zorder=3)
ax.plot([centre1, centre5], [turn_y, turn_y], color=MUTED, linewidth=0.5, zorder=3)
arrow(ax, (centre5, turn_y), (centre5, ROW2_Y + BOX_H))
note(ax, (centre1 + centre5) / 2, turn_y, "candidate stream", boxed=True)

# each gate carries its own refusal; selection carries the queue
for centre, text, right in (
    (xs2[0] + w2 / 2, r"$n<n_{\mathrm{marg}}$: refuse", False),
    (xs2[1] + w2 / 2, "audit rejects: refuse", False),
    (xs2[2] + w2 / 2, "alert queue", True),
):
    arrow(ax, (centre, ROW2_Y), (centre, STRIP_Y + STRIP_H), dashed=not right)
    note(ax, centre + (-0.012 if right else 0.012),
         (ROW2_Y + STRIP_Y + STRIP_H) / 2, text, ha="right" if right else "left")

# what the operator actually receives
ax.add_patch(FancyBboxPatch(
    (LEFT, STRIP_Y), RIGHT - LEFT, STRIP_H, boxstyle="square,pad=0",
    linewidth=0.55, edgecolor=MUTED, facecolor="white", zorder=2,
))
ax.text(0.5, STRIP_Y + STRIP_H * 0.68,
        "state: certified ($n \\geq n_{\\mathrm{cond}}$, audit passes)  ·  "
        "degraded ($n_{\\mathrm{marg}} \\leq n < n_{\\mathrm{cond}}$)  ·  refuse",
        ha="center", va="center", fontsize=7.4, color=INK, zorder=3)
ax.text(0.5, STRIP_Y + STRIP_H * 0.26,
        "record: $q$  ·  $\\hat\\pi$  ·  $n$  ·  audit statistic  ·  emitted alerts  ·  reason code",
        ha="center", va="center", fontsize=6.8, color=MUTED, zorder=3)

fig.savefig(OUT_PDF, format="pdf", bbox_inches="tight", pad_inches=0.04)
fig.savefig(OUT_PNG, format="png", dpi=400, bbox_inches="tight", pad_inches=0.04)
print(OUT_PDF)
print(OUT_PNG)
