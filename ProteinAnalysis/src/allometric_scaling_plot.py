import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

df = pd.read_csv("../results/features.tsv", sep="\t")

stats = pd.read_csv("../results/allometric_scaling.tsv", sep="\t")

colors = {
    "Homo sapiens": "#0072B2",
    "Mus musculus": "#009E73",
    "Bos taurus": "#D55E00"
}

plt.figure(figsize=(9, 6))

for org in ["Homo sapiens", "Mus musculus", "Bos taurus"]:
    subset = df[df["organism"] == org]
    plt.scatter(subset["length"], subset["hydrophobicity"], 
                c=colors[org], label=org, alpha=0.15, s=10, edgecolor="none")
    z = np.polyfit(subset["length"], subset["hydrophobicity"], 1)
    p = np.poly1d(z)
    x_vals = np.array([subset["length"].min(), subset["length"].max()])
    plt.plot(x_vals, p(x_vals), c=colors[org], linewidth=2)

for i, (_, row) in enumerate(stats[stats["Feature"] == "hydrophobicity"].iterrows()):
    org_name = row["Organism"]
    plt.text(0.8, 0.45 - i*0.07, 
             f"{org_name}: β={row['Beta(Slope)']:.3f}, R²={row['R_squared']:.3f}",
             transform=plt.gca().transAxes, fontsize=9, 
             bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

plt.xlabel("Sequence Length (amino acids)")
plt.ylabel("Hydrophobicity (Kyte-Doolittle score)")
plt.title("Allometric Scaling: Hydrophobicity vs. Protein Length")
leg = plt.legend(loc="upper right", fontsize="large", framealpha=1, shadow=True, markerscale=2.0)
for lh in leg.legend_handles: 
    lh.set_alpha(1)
plt.grid(axis="y", alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig("../results/allometric_scaling_hydrophobicity.png", dpi=100, bbox_inches="tight")
plt.show()
