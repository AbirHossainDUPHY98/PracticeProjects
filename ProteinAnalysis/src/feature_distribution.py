import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import argparse
import os

sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.0)

INPUT = "../results/features.tsv"
OUTPUT = "../results/feature_distribution.png"
FEATURES = ["hydrophobicity", "entropy"]
ORGANISMS = ["Homo sapiens", "Mus musculus", "Bos taurus"]
COLORS = {"Homo sapiens": "#2E86AB", "Mus musculus": "#A23B72", "Bos taurus": "#F18F01"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default=INPUT)
    parser.add_argument("-o", "--output", default=OUTPUT)
    args = parser.parse_args()

    df = pd.read_csv(args.input, sep="\t")
    df = df[df["organism"].isin(ORGANISMS)]

    fig, axes = plt.subplots(len(FEATURES), 1, figsize=(9, 8), dpi=300, sharex=False)
    if len(FEATURES) == 1:
        axes = [axes]

    for idx, feature in enumerate(FEATURES):
        ax = axes[idx]
        
        # Create ridgeline plot
        for i, org in enumerate(ORGANISMS):
            subset = df[df["organism"] == org][feature].dropna()
            
            # Kernel density estimation
            kde = sns.kdeplot(subset, ax=ax, fill=False, 
                             color=COLORS[org], linewidth=3, label=org)
            
            # Fill under curve with transparency
            x, y = kde.get_lines()[0].get_data()
            ax.fill_between(x, y + i*0.3, i*0.3, color=COLORS[org], alpha=0.3)
            
            # Add organism label
            ax.text(subset.median(), (i + 0.8) * 0.3, org, 
                   color=COLORS[org], fontsize=9, ha='center', fontweight='bold')

        ax.set_ylabel(feature.capitalize(), fontsize=10)
        ax.set_xlabel("")
        ax.set_yticks([])
        ax.grid(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    axes[-1].set_xlabel("Value", fontsize=10)
    plt.suptitle("Feature Distributions Across Organisms", 
                fontsize=12, fontweight="bold", y=0.995)
    
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    plt.savefig(args.output, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()

if __name__ == "__main__":
    main()
