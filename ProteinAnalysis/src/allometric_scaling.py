import pandas as pd
import numpy as np
from scipy.stats import linregress  # linear least-squares regression for two sets of measurements. It gives back m,c, r-value: the correlation coefficient:: r^2 shows how the variation is explained by the model, p-value: This is significance factor:: lower value(<0.05) is of greater significance, Standard Error. 


df = pd.read_csv("../results/features.tsv", sep="\t")

aa_cols = [col for col in df.columns if col.startswith('freq_')]
target_features = ['hydrophobicity', 'entropy'] + aa_cols

results = []

for organism, group in df.groupby('organism'):
    
    for feature in target_features:
        clean_data = group[(group[feature] > 0) & (group['length'] > 0)]  # check for data acceptability: every feature and that feature's length must be greater than 0.
        
        if len(clean_data) > 30: # Ensure statistical significance
            log_x = np.log10(clean_data['length'])
            log_y = np.log10(clean_data[feature])
            
            beta, alpha, r_val, p_val, std_err = linregress(log_x, log_y)
            
            results.append({
                'Organism': organism,
                'Feature': feature,
                'Beta(Slope)': round(beta, 4),
                'R_squared': round(r_val**2, 4),
                'P_value': p_val
            })

scaling_summary = pd.DataFrame(results)
scaling_summary.to_csv("../results/allometric_scaling.tsv", sep="\t", index=False)

