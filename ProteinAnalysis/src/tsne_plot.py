import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_style("whitegrid")
sns.set_context("paper", font_scale=0.95)

INPUT = "../results/tsne_projections+features.tsv"
OUTPUT = "../results/tsne_landscape.png"
ORGANISMS = ["Homo sapiens", "Mus musculus", "Bos taurus"]
COLORS = {"Homo sapiens": "#2E86AB", "Mus musculus": "#A23B72", "Bos taurus": "#F18F01"}

def main():
    df = pd.read_csv(INPUT, sep="\t")
    df = df[df["organism"].isin(ORGANISMS)]
    if len(df) > 10000:
        df = df.sample(n=10000, random_state=42)
    print(f"  Using {len(df):,} points")

    fig, axes = plt.subplots(2, 2, figsize=(12, 10), dpi=300)
    x, y = df["tsne_1"], df["tsne_2"]
    scatter_kw = dict(alpha=0.5, s=8, edgecolors='none')

    ax = axes[0, 0]
    for org in ORGANISMS:
        sub = df[df["organism"] == org]
        ax.scatter(sub["tsne_1"], sub["tsne_2"], c=COLORS[org], label=org, **scatter_kw)
    ax.legend(loc="best", frameon=True, fontsize=8)
    ax.set_title("A. Colored by Organism", fontsize=10, fontweight="bold")

    for ax, (col, cmap, label, letter) in zip(axes.flat[1:], [
        ("hydrophobicity",  "coolwarm", "Hydrophobicity",         "B"),
        ("entropy",         "viridis",  "Entropy (bits)",          "C"),
        ("molecular_weight","magma",    "Molecular Weight (Da)",   "D"),
    ]):
        sc = ax.scatter(x, y, c=df[col], cmap=cmap, **scatter_kw)
        plt.colorbar(sc, ax=ax, label=label, shrink=0.8)
        ax.set_title(f"{letter}. Colored by {label.split(' (')[0]}", fontsize=10, fontweight="bold")

    for ax in axes.flat:
        ax.set(xlabel="t-SNE 1", ylabel="t-SNE 2")
        ax.grid(True, linestyle="--", alpha=0.3)

    plt.suptitle("t-SNE Protein Landscape — Physicochemical Property Gradients",
                 fontsize=12, fontweight="bold", y=0.995)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    plt.savefig(OUTPUT, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()

if __name__ == "__main__":
    main()
