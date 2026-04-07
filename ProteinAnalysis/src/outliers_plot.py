import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.0)

INPUT = "../results/features.tsv"
OUTPUT = "../results/outlier_analysis.png"
OUTLIER_THRESHOLD = 0.01
MAX_LABELS = 10

COLORS = {
    "Disordered/Regulatory": "#2E86AB",
    "Membrane/Structural":   "#E94F37",
    "Hydrophobic":           "#F18F01",
    "Hydrophilic":           "#A23B72",
}

def main():
    df = pd.read_csv(INPUT, sep="\t")

    hl, hh = df["hydrophobicity"].quantile([OUTLIER_THRESHOLD, 1 - OUTLIER_THRESHOLD])
    el, eh = df["entropy"].quantile([OUTLIER_THRESHOLD, 1 - OUTLIER_THRESHOLD])

    df["is_outlier"] = (
        df["hydrophobicity"].lt(hl) | df["hydrophobicity"].gt(hh)
    ) & (
        df["entropy"].lt(el) | df["entropy"].gt(eh)
    )

    def classify(row):
        h, e = row["hydrophobicity"], row["entropy"]
        if h < hl and e > eh: return "Disordered/Regulatory"
        if h > hh and e < el: return "Membrane/Structural"
        if h > hh:            return "Hydrophobic"
        if h < hl:            return "Hydrophilic"
        return "Normal"

    df["outlier_type"] = df.apply(classify, axis=1)

    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)

    normal = df[~df["is_outlier"]]
    ax.scatter(normal["hydrophobicity"], normal["entropy"],
               c="#CCCCCC", alpha=0.3, s=15, label="Normal proteins", zorder=1)

    outliers = df[df["is_outlier"]]
    for otype, color in COLORS.items():
        sub = outliers[outliers["outlier_type"] == otype]
        ax.scatter(sub["hydrophobicity"], sub["entropy"],
                   c=color, alpha=0.7, s=40, label=otype,
                   edgecolors="black", linewidth=0.5, zorder=2)

    for _, row in outliers.nlargest(MAX_LABELS, "molecular_weight").iterrows():
        ax.annotate(row["accession"], xy=(row["hydrophobicity"], row["entropy"]),
                    xytext=(5, 5), textcoords="offset points", fontsize=7,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                              edgecolor="#333333", alpha=0.7),
                    arrowprops=dict(arrowstyle="->", color="#333333", lw=0.5))

    line_kw = dict(color="#E94F37", linestyle="--", alpha=0.5, linewidth=1)
    for v in (hl, hh): ax.axvline(v, **line_kw)
    for h in (el, eh): ax.axhline(h, **line_kw)

    ax.set(xlabel="Hydrophobicity", ylabel="Sequence Entropy (bits)")
    ax.set_title(f"Extreme Proteins — Outlier Analysis (Top/Bottom {OUTLIER_THRESHOLD*100:.0f}%)",
                 fontsize=12, fontweight="bold", pad=15)
    ax.legend(loc="upper right", frameon=True, fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.4)

    ax.text(hl - 0.3, eh + 0.1, "Disordered\nRegulatory",
            fontsize=8, ha="right", color="#2E86AB", fontweight="bold")
    ax.text(hh + 0.3, el - 0.1, "Membrane\nStructural",
            fontsize=8, ha="left", color="#E94F37", fontweight="bold")

    plt.tight_layout()
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    plt.savefig(OUTPUT, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()

if __name__ == "__main__":
    main()
