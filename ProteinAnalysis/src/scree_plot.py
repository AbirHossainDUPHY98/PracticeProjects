import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.ticker import PercentFormatter
import seaborn as sns

sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.15)

INPUT  = "../results/pca_variance_components.tsv"
OUTPUT = "../results/pca_scree_plot.png"

ORGANISMS = ["Homo sapiens", "Mus musculus", "Bos taurus"]
COLORS    = {"Homo sapiens": "#3D7ABF", "Mus musculus": "#E07B39", "Bos taurus": "#3BAF78"}
THRESHOLD = 0.95

df = pd.read_csv(INPUT, sep="\t")
df = df[df["organism"].isin(ORGANISMS)]

fig, ax1 = plt.subplots(figsize=(10, 5.5), dpi=300)
ax2 = ax1.twinx()

for org in ORGANISMS:
    sub, color = df[df["organism"] == org], COLORS[org]

    ax1.plot(sub["component"], sub["variance_explained"],
             color=color, marker="o", markersize=3.5, linewidth=1.8)
    ax2.plot(sub["component"], sub["cumulative_variance"],
             color=color, marker="s", markersize=2.2, linewidth=1.2,
             linestyle=":", alpha=0.6)

    n95 = sub.loc[sub["cumulative_variance"] >= THRESHOLD, "component"].min()
    if pd.notna(n95):
        ax2.annotate(f"PC {int(n95)}", xy=(n95, THRESHOLD), xytext=(6, 6),
                     textcoords="offset points", fontsize=7.5, color=color,
                     bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                               edgecolor=color, linewidth=0.8, alpha=0.9))

ax2.axhline(y=THRESHOLD, color="#C0392B", linestyle="--", linewidth=1.1, alpha=0.85)

ax1.set_xlabel("Principal Component")
ax1.set_ylabel("Variance Explained (%)")
ax2.set_ylabel("Cumulative Variance (%)", color="#555", fontsize=9)
ax2.set_ylim(0, 1.05)
ax1.grid(axis="x", linestyle="--", alpha=0.35)
for ax in (ax1, ax2):
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
ax2.tick_params(axis="y", labelcolor="#555", labelsize=8)

handles = [mlines.Line2D([], [], color=COLORS[o], marker="o",
                          markersize=4, linewidth=1.8, label=o) for o in ORGANISMS]
handles += [
    mlines.Line2D([], [], color="grey", marker="s", markersize=3,
                  linewidth=1.2, linestyle=":", label="Cumulative"),
    mlines.Line2D([], [], color="#C0392B", linewidth=1.1,
                  linestyle="--", label="95% threshold"),
]
ax1.legend(handles=handles, loc="center right", fontsize=8.5,
           frameon=True, framealpha=0.92, edgecolor="#ccc")

plt.suptitle("PCA Variance Explained by Organism", fontsize=12, fontweight="bold")
plt.tight_layout()
plt.savefig(OUTPUT, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
