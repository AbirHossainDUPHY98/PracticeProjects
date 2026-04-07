import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import os

INPUT_FILE = "../results/features.tsv"
OUTPUT_DIR = "../results"
CUMULATIVE_THRESHOLD = 0.95

def main():
    df = pd.read_csv(INPUT_FILE, sep="\t")
    aa_cols = [c for c in df.columns if c.startswith('freq_')]
    features = ['entropy', 'hydrophobicity'] + aa_cols
    
    results_summary, all_embeddings = [], []
    pca_variance_details, pca_loadings_details, pca_scores_details = [], [], []
    
    for organism, group in df.groupby('organism'):
        clean_group = group.dropna(subset=features).copy()
        data = clean_group[features]
        
        if len(data) < 2:
            continue
        
        scaled_data = StandardScaler().fit_transform(data)
        pca = PCA().fit(scaled_data)
        variance_ratio = pca.explained_variance_ratio_
        cumulative_variance = np.cumsum(variance_ratio)
        dim_95 = np.argmax(cumulative_variance >= CUMULATIVE_THRESHOLD) + 1
        

        pca_scores = pca.transform(scaled_data)
        n_samples = min(1000, len(pca_scores))
        for idx in range(n_samples):
            pca_scores_details.append({
                'organism': organism,
                'protein_idx': idx,
                'PC1': round(float(pca_scores[idx, 0]), 4),
                'PC2': round(float(pca_scores[idx, 1]), 4)
            })
        
        for i in range(min(50, len(variance_ratio))):
            pca_variance_details.append({
                'organism': organism,
                'component': i + 1,
                'variance_explained': round(variance_ratio[i], 6),
                'cumulative_variance': round(cumulative_variance[i], 6)
            })
        
        for feat, loading in zip(features, pca.components_[0]):
            pca_loadings_details.append({
                'organism': organism,
                'feature': feat,
                'loading_pc1': round(loading, 6),
                'abs_loading': round(abs(loading), 6)
            })
        
        tsne = TSNE(n_components=2, perplexity=min(30, len(data)-1),
                    random_state=42, init='pca', learning_rate='auto')
        embedding = tsne.fit_transform(scaled_data)
        clean_group['tsne_1'] = embedding[:, 0]
        clean_group['tsne_2'] = embedding[:, 1]
        all_embeddings.append(clean_group)
        
        results_summary.append({
            'Organism': organism,
            'PCA_95_Dim': dim_95,
            'Top_PC_Variance': round(variance_ratio[0], 4),
            'Protein_Count': len(data)
        })
    
    pd.DataFrame(results_summary).to_csv(f"{OUTPUT_DIR}/intrinsic_dimensionality.tsv", sep="\t", index=False)
    pd.concat(all_embeddings, ignore_index=True).to_csv(f"{OUTPUT_DIR}/tsne_projections+features.tsv", sep="\t", index=False)
    pd.DataFrame(pca_variance_details).to_csv(f"{OUTPUT_DIR}/pca_variance_components.tsv", sep="\t", index=False)
    pd.DataFrame(pca_loadings_details).to_csv(f"{OUTPUT_DIR}/pca_pc1_loadings.tsv", sep="\t", index=False)
    pd.DataFrame(pca_scores_details).to_csv(f"{OUTPUT_DIR}/pca_scores_pc1_pc2.tsv", sep="\t", index=False)
    

if __name__ == "__main__":
    main()
