import pandas as pd
import numpy as np

INPUT = "../clean_data/proteins_clean.tsv"
OUTPUT = "../results/features.tsv"

df = pd.read_table(INPUT)

aa_weights = {
    'A': 89.09, 'C': 121.15, 'D': 133.10, 'E': 147.13,
    'F': 165.19, 'G': 75.07, 'H': 155.16, 'I': 131.17,
    'K': 146.19, 'L': 131.17, 'M': 149.21, 'N': 132.12,
    'P': 115.13, 'Q': 146.15, 'R': 174.20, 'S': 105.09,
    'T': 119.12, 'V': 117.15, 'W': 204.23, 'Y': 181.19,
    'X': 0, 'U': 168.06, 'O': 255.31
}

hydrophobicity = {
    'A': 1.8,'C': 2.5,'D': -3.5,'E': -3.5,'F': 2.8,'G': -0.4,
    'H': -3.2,'I': 4.5,'K': -3.9,'L': 3.8,'M': 1.9,'N': -3.5,
    'P': -1.6,'Q': -3.5,'R': -4.5,'S': -0.8,'T': -0.7,
    'V': 4.2,'W': -0.9,'Y': -1.3,'X': 0,'U': 0,'O': 0
}

def compute_features(seq):
    seq = seq.upper()
    L = len(seq)
    
    molecularWeight = sum(aa_weights.get(a, 0) for a in seq)
    
    hydropathy = np.mean([hydrophobicity.get(a, 0) for a in seq])
    
    composition = {f"freq_{aa}": seq.count(aa)/L for aa in "ACDEFGHIKLMNPQRSTVWY"}
    
    entropy = -sum((seq.count(a)/L)*np.log2(seq.count(a)/L)
                   for a in set(seq) if seq.count(a) > 0)
    # Shannon entropy : H = - sum(i=1->N) (P(xi) * log(2 based) * P(xi))
    # so P here is the probability frequency of specific character appearing.
    # seq.count(0) > 0 for preventing log(0)
    # use set(0) to prevent duplicate character calculation.
    
    return {
        "molecular_weight": molecularWeight,
        "hydrophobicity": hydropathy,
        "entropy": entropy,
        **composition  # "**" operator is called the dictionary unpacking operator. tells create a new dictionary, include all the key-value pairs, then dump the contents of composition dictionary into this new one. so this merging of 2 dictionaries into one. 
    }

features = df["sequence"].apply(compute_features).apply(pd.Series)

features_added = pd.concat([df, features], axis=1)  # df is the original data, features is the new table. axis = 0 stack them on top of each other in rows. axis = 1 adds as colum. 
features_added.to_csv(OUTPUT, sep="\t", index=False)

print("Features computed:", features_added.shape) ## verification of number of rows and columns.

# output: Features computed: (29998, 28)

