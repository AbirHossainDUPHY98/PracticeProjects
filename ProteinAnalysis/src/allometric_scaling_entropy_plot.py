import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("../results/features.tsv", sep="\t")
stats_df = pd.read_csv("../results/allometric_scaling.tsv", sep="\t")

colors = {
    "Homo sapiens": "#004e7c",
    "Mus musculus": "#006d50",
    "Bos taurus": "#a34800"
}

entropy_stats = stats_df[stats_df["Feature"] == "entropy"].copy()

fig, axes = plt.subplots(2, 2, figsize=(12, 10), dpi=150)
axes = axes.flatten()

for i, org_full in enumerate(colors.keys()):
    ax = axes[i]
    subset = df[df["organism"] == org_full]
    
    ax.hexbin(subset["length"], subset["entropy"], gridsize=30, cmap="viridis", mincnt=1)
    
    stat = entropy_stats[entropy_stats["Organism"] == org_full].iloc[0]
    z = np.polyfit(subset["length"], subset["entropy"], 1)
    ax.plot(subset["length"], np.poly1d(z)(subset["length"]), "r--", lw=2)
    
    ax.text(0.95, 0.05, f"β={stat['Beta(Slope)']:.4e}\nR²={stat['R_squared']:.3f}", 
            transform=ax.transAxes, verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9))
    
    ax.set_title(org_full, fontweight="bold")

ax_all = axes[3]
for org, color in colors.items():
    subset = df[df["organism"] == org]
    ax_all.scatter(subset["length"], subset["entropy"], c=color, label=org, 
                   alpha=0.2, s=3, edgecolor="none")
    
    z = np.polyfit(subset["length"], subset["entropy"], 1)
    ax_all.plot(subset["length"], np.poly1d(z)(subset["length"]), c=color, lw=1)

leg = ax_all.legend(loc="lower right", fontsize=10, frameon=True, shadow=True, markerscale=1.5)
for lh in leg.legend_handles: 
    lh.set_alpha(1.0)

for ax in axes:
    ax.set_xlabel("Length (aa)", fontsize=10)
    ax.set_ylabel("Entropy (bits)", fontsize=10)
    
    ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0)) 
    ax.tick_params(axis='x', labelsize=9)

plt.suptitle("Entropy vs. Sequence Length Allometry", fontsize=14, fontweight="bold", y=0.98)

plt.subplots_adjust(hspace=0.4, wspace=0.3)

plt.savefig("../results/allometric_scaling_entropy.png", dpi=150, bbox_inches="tight")
plt.show()
