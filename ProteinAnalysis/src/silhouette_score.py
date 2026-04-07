import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.1)

INPUT = "../results/clustering_silhouette_scores.tsv"
OUTPUT = "../results/silhouette_analysis.png"
THRESHOLD = 0.5

def main():
    df = pd.read_csv(INPUT, sep="\t")
    best = df.loc[df["silhouette_score"].idxmax()]

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)

    colors = ["#2E86AB" if s >= THRESHOLD else "#E94F37" for s in df["silhouette_score"]]
    ax.bar(df["k"].astype(str), df["silhouette_score"],
           color=colors, edgecolor="#666666", linewidth=0.5, alpha=0.9)

    ax.axhline(THRESHOLD, color="#E94F37", linestyle="--",
               linewidth=1.5, alpha=0.8, label=f"Threshold ({THRESHOLD})")

    for i, (_, row) in enumerate(df.iterrows()):
        ax.text(i, row["silhouette_score"] + 0.005, f"{row['silhouette_score']:.2f}",
                ha="center", fontsize=9, fontweight="bold", color="#333333")

    ax.set(xlabel="Number of Clusters (k)", ylabel="Silhouette Score",
           ylim=(0, df["silhouette_score"].max() * 1.3))
    ax.set_title("Cluster Quality Assessment — Silhouette Analysis",
                 fontsize=12, fontweight="bold", pad=15)
    ax.legend(loc="upper right", frameon=True)
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)

    plt.figtext(0.5, 0.01,
                f"Best: k={best['k']}, score={best['silhouette_score']:.2f} — below threshold, no clear clustering",
                ha="center", fontsize=9, style="italic",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFF9C4", alpha=0.8))

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    plt.savefig(OUTPUT, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()

if __name__ == "__main__":
    main()
