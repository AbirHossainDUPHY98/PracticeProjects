import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv('../results/statistical_significance_matrix.tsv', sep='\t')

features = df['feature'].tolist()
x = np.arange(len(features))
alpha_line = -np.log10(0.05)

def safe_log(vals):
    return [-np.log10(max(v, 1e-300)) for v in vals]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
fig.suptitle('Statistical Significance across Organisms\n(ANOVA / Kruskal-Wallis + Bonferroni)', fontsize=13, fontweight='bold')

w = 0.18
offsets = np.linspace(-1.5*w, 1.5*w, 4)
tests = {
    'ANOVA':      df['pval_anova'],
    'Kruskal-W':  df['pval_kruskal'],
    'ANOVA+Bonf': df['pval_anova_bonf'],
    'KW+Bonf':    df['pval_kw_bonf'],
}
colors = ['#4c72b0', '#55a868', '#c44e52', '#8172b2']
for i, (label, pv) in enumerate(tests.items()):
    ax1.bar(x + offsets[i], safe_log(pv), w, label=label, color=colors[i], alpha=0.85)

ax1.axhline(alpha_line, color='red', linestyle='--', linewidth=1.2, label='α = 0.05')
ax1.set_xticks(x)
ax1.set_xticklabels(features, rotation=45, ha='right', fontsize=8)
ax1.set_ylabel('–log₁₀(p-value)')
ax1.set_title('Global Tests (Raw & Bonferroni)')
ax1.legend(fontsize=9, loc='upper right', bbox_to_anchor=(1, 1), framealpha=0.9)
ax1.grid(axis='y', alpha=0.3)

pw_offsets = np.linspace(-w, w, 3)
pairwise = {
    'Hs vs Bt': df['Homo sapiens_vs_Bos taurus'],
    'Hs vs Mm': df['Homo sapiens_vs_Mus musculus'],
    'Bt vs Mm': df['Bos taurus_vs_Mus musculus'],
}
pw_colors = ['#e78ac3', '#a6d854', '#ffd92f']
for i, (label, pv) in enumerate(pairwise.items()):
    ax2.bar(x + pw_offsets[i], safe_log(pv), w, label=label, color=pw_colors[i], alpha=0.85)

ax2.axhline(alpha_line, color='red', linestyle='--', linewidth=1.2, label='α = 0.05')
ax2.set_xticks(x)
ax2.set_xticklabels(features, rotation=45, ha='right', fontsize=8)
ax2.set_ylabel('–log₁₀(p-value)')
ax2.set_title('Pairwise Post-hoc')
ax2.legend(fontsize=9, loc='upper right', bbox_to_anchor=(1, 1), framealpha=0.9)
ax2.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('../results/statistical_significance_plot.png', dpi=150, bbox_inches='tight')
print("Done.")
