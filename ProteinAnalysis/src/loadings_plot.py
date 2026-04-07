"""PC1 Loadings Bar Chart — all organisms"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.15)

INPUT    = "../results/pca_pc1_loadings.tsv"
OUT_DIR  = "../results/"
TOP_N    = 15

ORGANISMS = ["Homo sapiens", "Mus musculus", "Bos taurus"]
COLORS    = {"Positive": "#3D7ABF", "Negative": "#E07B39"}

df = pd.read_csv(INPUT, sep="\t")

for org in ORGANISMS:
    sub = df[df["organism"] == org].copy()
    sub = sub.reindex(sub["loading_pc1"].abs().nlargest(TOP_N).index).sort_values("loading_pc1")
    colors = sub["loading_pc1"].apply(lambda x: COLORS["Positive"] if x >= 0 else COLORS["Negative"])

    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)
    bars = ax.barh(sub["feature"], sub["loading_pc1"], color=colors, edgecolor="white", linewidth=0.4)

    for bar, val in zip(bars, sub["loading_pc1"]):
        ax.text(val + (0.005 if val >= 0 else -0.005),
                bar.get_y() + bar.get_height() / 2,
                f"{val:+.2f}", va="center",
                ha="left" if val >= 0 else "right",
                fontsize=8, color=bar.get_facecolor())

    ax.axvline(0, color="black", linewidth=0.9)
    ax.set_xlabel("Loading Value")
    ax.set_title(f"PC1 Loadings — {org}", fontweight="bold", fontsize=12)

    handles = [plt.Rectangle((0, 0), 1, 1, color=c, label=l) for l, c in COLORS.items()]
    ax.legend(handles=handles, loc="lower right", fontsize=9, frameon=True, edgecolor="#ccc")

    plt.tight_layout()
    fname = org.replace(" ", "_").lower()
    plt.savefig(os.path.join(OUT_DIR, f"pc1_loadings_{fname}.png"),
                dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"✓ Saved: pc1_loadings_{fname}.png")
