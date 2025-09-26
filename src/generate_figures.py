# Metrics Bars


import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

import numpy as np
import pandas as pd

metrics_table = pd.DataFrame({
    "metric": ["Specificity",  "Actionability",  "Assumptions Identified",  "Comment Quality",  "Suggestions"],
    "baseline": [3.0,  3.1667,  0.0,  3.1667,  1.25],
    "clarified": [4.667,  4.667,  3.0833,  4.833,  4.5],
    "delta": [1.667,  1.5,  3.0833,  1.667,  3.25]
})

eval_scored = pd.DataFrame([
    [3, 4, 4, 5, 0, 0, 4, 5, 2, 5],
    [3, 5, 3, 5, 0, 12, 3, 5, 1, 4],
    [4, 5, 4, 5, 0, 0, 4, 5, 2, 8],
    [3, 4, 3, 3, 0, 0, 3, 4, 1, 1],
    [4, 5, 3, 5, 0, 12, 4, 5, 1, 8],
    [3, 5, 5, 3, 0, 0, 4, 4, 4, 1],
    [3, 5, 3, 5, 0, 0, 3, 5, 1, 5],
    [3, 5, 4, 5, 0, 5, 4, 5, 2, 9],
    [2, 4, 2, 5, 0, 0, 2, 5, 0, 4],
    [2, 4, 2, 5, 0, 0, 2, 5, 0, 3],
    [3, 5, 2, 5, 0, 8, 2, 5, 0, 3],
    [3, 5, 3, 5, 0, 0, 3, 5, 1, 3],
],  columns=[
    "spec_b", "spec_c",
    "act_b", "act_c",
    "assump_b", "assump_c",
    "qual_b", "qual_c",
    "sugg_b", "sugg_c"
])

delta_all = pd.DataFrame({
    "metric": ["Specificity"] * len(eval_scored) + ["Actionability"] * len(eval_scored) +
              ["Assumptions Identified"] * len(eval_scored) + ["Comment Quality"] * len(eval_scored) +
              ["Suggestions"] * len(eval_scored),
    "delta":  list(eval_scored["spec_c"] - eval_scored["spec_b"]) +
              list(eval_scored["act_c"] - eval_scored["act_b"]) +
              list(eval_scored["assump_c"] - eval_scored["assump_b"]) +
              list(eval_scored["qual_c"] - eval_scored["qual_b"]) +
              list(eval_scored["sugg_c"] - eval_scored["sugg_b"])
})

# metrics_table has columns: metric,  baseline,  clarified
x = np.arange(len(metrics_table['metric']))
width = 0.35
plt.figure(figsize=(6, 4))
plt.bar(x - width/2,  metrics_table['baseline'],  width,  label='Baseline')
plt.bar(x + width/2,  metrics_table['clarified'],  width,  label='Clarified')
plt.xticks(x,  [m.replace('_', ' ').title() for m in metrics_table['metric']],  rotation=30,  ha='right')
plt.ylabel("Average Score")
plt.title("Average Metric Scores: Baseline vs Clarified")
plt.legend()
plt.tight_layout()
plt.savefig("./results/plots/fig_metrics_bars.png",  dpi=300)


# Delta Bars

# Continuing from metrics_table
plt.figure(figsize=(6, 4))
plt.bar(x,  metrics_table['delta'])
plt.xticks(x,  [m.replace('_', ' ').title() for m in metrics_table['metric']],  rotation=30,  ha='right')
plt.ylabel("Delta (Clarified - Baseline)")
plt.title("Improvement by Metric")
plt.tight_layout()
plt.savefig("./results/plots/fig_delta_bars.png",  dpi=300)


# # Delta Boxplot

# # delta_all DataFrame has columns: metric,  delta
# plt.figure(figsize=(6, 4))
# data = [delta_all.loc[delta_all['metric']==m,  'delta'].dropna().values for m in metrics_table['metric']]
# plt.boxplot(data,  labels=[m.replace('_', ' ').title() for m in metrics_table['metric']],  vert=True)
# plt.ylabel("Per-PR Delta (Clarified - Baseline)")
# plt.title("Distribution of Improvements by Metric")
# plt.xticks(rotation=30,  ha='right')
# plt.tight_layout()
# plt.savefig("./results/plots/fig_delta_boxplot.png",  dpi=300)


# Architecture Diagram

W,  H = 1.8,  0.8  # box width/height


def draw_box(ax,  xy,  text,  color="#cce5ff"):
    x,  y = xy
    box = FancyBboxPatch((x,  y),  W,  H,  boxstyle="round, pad=0.3",  fc=color,  ec="black")
    ax.add_patch(box)
    ax.text(x + W/2,  y + H/2,  text,  ha="center",  va="center",  fontsize=12)
    # handy anchors on the edges
    return {
        "left":   (x,          y + H/2), 
        "right":  (x + W,      y + H/2), 
        "top":    (x + W/2,    y + H), 
        "bottom": (x + W/2,    y)
    }


def arrow(ax,  p1,  p2,  rad=0.0):
    ax.annotate(
        "",  xy=p2,  xytext=p1, 
        arrowprops=dict(arrowstyle="-|>",  lw=2,  connectionstyle=f"arc3, rad={rad}")
    )


fig,  ax = plt.subplots(figsize=(11, 5))

pr = draw_box(ax,  (0.0,  1.0),  "PR Examples\n(JSONL)",       color="#f2f2f2")
clar = draw_box(ax,  (3.0,  2.0),  "ClarifyCoder\n(asks)",        color="#ffe6cc")
you = draw_box(ax,  (6.0,  2.0),  "You (answers)",               color="#e6ffe6")
clarrev = draw_box(ax,  (9.0,  1.0),  "Clarified Reviewer\n(Gemini)",  color="#d9e6f2")
base = draw_box(ax,  (3.0,  0.0),  "Baseline Reviewer\n(Gemini)",  color="#d9e6f2")

# arrows: from box edge to box edge (with slight curvature to avoid text)
arrow(ax,  pr["right"],    clar["left"],    rad=0.15)
arrow(ax,  clar["right"],  you["left"],     rad=0.00)
arrow(ax,  you["right"],   clarrev["left"], rad=-0.15)
arrow(ax,  pr["right"],    base["left"],    rad=-0.12)

ax.set_xlim(-0.5,  11.5)
ax.set_ylim(-0.5,  3.5)
ax.axis("off")
ax.set_title("ClarifyCoder + Gemini Review Pipeline",  fontsize=18,  pad=15)
plt.tight_layout()
plt.savefig("./results/fig_architecture.png",  dpi=300,  bbox_inches="tight")
plt.show()
