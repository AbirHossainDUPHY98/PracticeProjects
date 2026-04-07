import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("../results/features.tsv", sep="\t")

features = [
    ("length", "Sequence Length"),
    ("molecular_weight", "Molecular Weight"),
    ("hydrophobicity", "Hydrophobicity"),
    ("entropy", "Entropy")
]

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes = axes.flatten()

colors = {"Homo sapiens": "#0072B2", "Mus musculus": "#009E73", "Bos taurus": "#D55E00"}

for ax, (col, title) in zip(axes, features):
    sns.boxplot(data=df, x="organism", y=col, 
                order=["Homo sapiens", "Mus musculus", "Bos taurus"],
                palette=colors, ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel(title)
    ax.set_title(title)

plt.suptitle("Physicochemical Features by Organism", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("feature_summary.png", dpi=300, bbox_inches="tight")
plt.show()
