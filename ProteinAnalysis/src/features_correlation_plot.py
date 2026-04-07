import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("../results/features.tsv", sep="\t")

numeric_cols = ['length', 'molecular_weight', 'hydrophobicity', 'entropy',
                'freq_A', 'freq_C', 'freq_D', 'freq_E', 'freq_F', 'freq_G',
                'freq_H', 'freq_I', 'freq_K', 'freq_L', 'freq_M', 'freq_N',
                'freq_P', 'freq_Q', 'freq_R', 'freq_S', 'freq_T', 'freq_V',
                'freq_W', 'freq_Y']

corr = df[numeric_cols].corr()

plt.figure(figsize=(12, 10))
sns.heatmap(corr, cmap="coolwarm", center=0, annot=False, square=True, 
            cbar_kws={"label": "Pearson correlation"})
plt.title("Feature Correlation Matrix", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("../results/features_correlation_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()
