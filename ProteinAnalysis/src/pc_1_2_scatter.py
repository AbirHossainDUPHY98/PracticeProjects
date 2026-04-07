import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os

sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.1)

INPUT = "../results/pca_scores_pc1_pc2.tsv"
OUTPUT = "../results/pc1_pc2_scatter.png"
ORGANISMS = ["Homo sapiens", "Mus musculus", "Bos taurus"]
COLORS = {"Homo sapiens": "#2E86AB", "Mus musculus": "#A23B72", "Bos taurus": "#F18F01"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default=INPUT)
    parser.add_argument("-o", "--output", default=OUTPUT)
    args = parser.parse_args()

    df = pd.read_csv(args.input, sep="\t")
    df = df[df["organism"].isin(ORGANISMS)]

    fig, ax = plt.subplots(figsize=(9, 7), dpi=300)

    for org in ORGANISMS:
        subset = df[df["organism"] == org]
        ax.scatter(subset["PC1"], subset["PC2"], 
                   c=COLORS[org], label=org, alpha=0.5, 
                   s=20, edgecolors='none', zorder=2)

    for org in ORGANISMS:
        subset = df[df["organism"] == org]
        if len(subset) > 10:
            sns.kdeplot(data=subset, x="PC1", y="PC2", 
                       levels=3, linewidths=2, 
                       color=COLORS[org], alpha=1, zorder=3)

    ax.set_xlabel("PC1 (Hydrophobicity Axis)", fontsize=10)
    ax.set_ylabel("PC2 (Composition Axis)", fontsize=10)
    ax.set_title("PC1 vs PC2: Organism Clustering", fontsize=12, fontweight="bold", pad=15)
    ax.legend(loc="best", frameon=True, edgecolor="#cccccc")
    ax.grid(True, linestyle="--", alpha=0.4)

    plt.tight_layout()
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    plt.savefig(args.output, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()

if __name__ == "__main__":
    main()
