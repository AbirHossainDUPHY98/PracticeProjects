# Developing a "Proteomic Complexity Index": PCI=(Mean Entropy×Feature Variance)/Redundancy Ratio -- rank organisms.
# New feature! 


import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.feature_selection import mutual_info_regression

df = pd.read_csv("../results/features.tsv", sep="\t")
aa_cols = [col for col in df.columns if col.startswith('freq_')]
feature_cols = ['entropy', 'hydrophobicity'] + aa_cols

pci_results = []

for organism, group in df.groupby('organism'):
    clean_data = group[feature_cols].dropna()
    if len(clean_data) < 50: continue
    
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(clean_data)
    
    mean_entropy = clean_data['entropy'].mean()
    
    pca = PCA().fit(scaled_data)
    total_variance = np.sum(pca.explained_variance_)
    
    sample_data = scaled_data[np.random.choice(len(scaled_data), min(500, len(scaled_data)), replace=False)]
    mi_scores = []
    for i in range(min(10, len(feature_cols))):
        target = sample_data[:, i]
        scores = mutual_info_regression(sample_data, target, discrete_features=False)
        mi_scores.append(np.mean(scores))
    
    redundancy_ratio = np.mean(mi_scores)
    pci = (mean_entropy * total_variance) / (redundancy_ratio + 1e-9) # avoid div by zero
    
    pci_results.append({
        'Organism': organism,
        'Mean_Entropy': round(mean_entropy, 4),
        'Feature_Variance': round(total_variance, 4),
        'Redundancy_Ratio': round(redundancy_ratio, 4),
        'PCI': round(pci, 2)
    })

pci_df = pd.DataFrame(pci_results).sort_values(by='PCI', ascending=False)
pci_df['Rank'] = range(1, len(pci_df) + 1)

pci_df.to_csv("../results/pci_rankings.tsv", sep="\t", index=False)

print("PCI Ranking Complete:")
print(pci_df[['Rank', 'Organism', 'PCI']])
