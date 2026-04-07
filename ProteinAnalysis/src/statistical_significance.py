import pandas as pd
import numpy as np
from scipy import stats
from itertools import combinations
import os

INPUT_FILE = "../results/features.tsv"
OUTPUT_FILE = "../results/statistical_significance_matrix.tsv"
SIGNIFICANCE_THRESHOLD = 0.05

def main():
    df = pd.read_csv(INPUT_FILE, sep="\t")
    organisms = df['organism'].unique()
    
    aa_cols = [c for c in df.columns if c.startswith('freq_')]
    features = ['entropy', 'hydrophobicity', 'length', 'molecular_weight'] + aa_cols
    
    results = []
    
    for feature in features:
        groups = [df[df['organism'] == org][feature].dropna() for org in organisms]
        
        if any(len(g) < 2 for g in groups):
            continue
        
        f_stat, pval_anova = stats.f_oneway(*groups)
        
        h_stat, pval_kw = stats.kruskal(*groups)
        
        pairwise_pvals = {}
        for org1, org2 in combinations(organisms, 2):
            g1, g2 = df[df['organism'] == org1][feature].dropna(), df[df['organism'] == org2][feature].dropna()
            _, pval = stats.mannwhitneyu(g1, g2, alternative='two-sided')
            pairwise_pvals[f"{org1}_vs_{org2}"] = round(pval, 6)
        
        results.append({
            'feature': feature,
            'pval_anova': round(pval_anova, 6),
            'pval_kruskal': round(pval_kw, 6),
            'significant_anova': pval_anova < SIGNIFICANCE_THRESHOLD,
            'significant_kw': pval_kw < SIGNIFICANCE_THRESHOLD,
            **pairwise_pvals
        })
    
    results_df = pd.DataFrame(results)
    n_tests = len(results_df)
    results_df['pval_anova_bonf'] = results_df['pval_anova'] * n_tests
    results_df['pval_kw_bonf'] = results_df['pval_kruskal'] * n_tests
    results_df['significant_anova_bonf'] = results_df['pval_anova_bonf'] < SIGNIFICANCE_THRESHOLD
    results_df['significant_kw_bonf'] = results_df['pval_kw_bonf'] < SIGNIFICANCE_THRESHOLD
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    results_df.to_csv(OUTPUT_FILE, sep="\t", index=False)

if __name__ == "__main__":
    main()
