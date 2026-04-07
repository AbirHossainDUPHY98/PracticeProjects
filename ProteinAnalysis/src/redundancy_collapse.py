import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_regression

df = pd.read_csv("../results/features.tsv", sep="\t")

aa_cols = [col for col in df.columns if col.startswith('freq_')]
feature_cols = ['entropy', 'hydrophobicity'] + aa_cols

results_list = []

for organism, group in df.groupby('organism'):
    print(f"Calculating Redundancy for {organism}...")
    
    clean_group = group[feature_cols].dropna()
    if len(clean_group) < 50: continue
    
    data = clean_group.values
    n_features = len(feature_cols)
    mi_matrix = np.zeros((n_features, n_features))

    for i in range(n_features):
        mi_scores = mutual_info_regression(data, data[:, i], discrete_features=False)
        mi_matrix[i, :] = mi_scores

    for i in range(n_features):
        for j in range(i + 1, n_features):
            results_list.append({
                'Organism': organism,
                'Feature_A': feature_cols[i],
                'Feature_B': feature_cols[j],
                'Mutual_Information': round(mi_matrix[i, j], 4)
            })

mi_df = pd.DataFrame(results_list)
mi_df.to_csv("../results/mutual_information_collapse.tsv", sep="\t", index=False)

top_collapses = mi_df.sort_values(by=['Organism', 'Mutual_Information'], ascending=[True, False])
top_collapses.groupby('Organism').head(5).to_csv("../results/top_redundancies.tsv", sep="\t")

print("Analysis Complete. Check ../results/mutual_information_collapse.tsv")
