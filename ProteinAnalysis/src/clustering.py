import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import os

INPUT = "../results/features.tsv"
OUTPUT = "../results/clustering_silhouette_scores.tsv"
MAX_SAMPLES = 5000

def main():
    print("Loading data...")
    df = pd.read_csv(INPUT, sep="\t")
    
    aa_cols = [c for c in df.columns if c.startswith('freq_')]
    features = ['entropy', 'hydrophobicity', 'length', 'molecular_weight'] + aa_cols
    
    data = df[features].dropna()
    print(f"  Total samples: {len(data):,}")
    
    if len(data) > MAX_SAMPLES:
        print(f"  Sampling to {MAX_SAMPLES:,} for silhouette calculation...")
        data_sample = data.sample(n=MAX_SAMPLES, random_state=42)
    else:
        data_sample = data
    
    scaled = StandardScaler().fit_transform(data_sample)
    
    k_range = range(2, 16)
    results = []
    
    print(f"\nComputing silhouette scores for k=2 to k=15...")
    for k in k_range:
        print(f"  k={k}...", end=" ", flush=True)
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10, max_iter=300)
        labels = kmeans.fit_predict(scaled)
        score = silhouette_score(scaled, labels, sample_size=min(1000, len(scaled)))
        
        results.append({
            'k': k,
            'silhouette_score': round(score, 4),
            'inertia': round(kmeans.inertia_, 2)
        })
        print(f"score={score:.4f}")
    
    pd.DataFrame(results).to_csv(OUTPUT, sep="\t", index=False)

if __name__ == "__main__":
    main()
