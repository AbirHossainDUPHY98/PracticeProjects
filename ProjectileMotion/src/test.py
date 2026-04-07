import pandas as pd
import numpy as np

df = pd.read_csv("atmosphere_nasa_clean.csv")
# print(f"Data types: {df.dtypes}")
# print(f"Basic stats: {df.describe()}")
h_data= df['altitudes_km'].values
rho_data= df['density_kg_m3'].values
print(f"Missing values in altitude: {pd.isna(h_data).sum()}")
print(f"Missing values in density: {pd.isna(rho_data.sum())}")
if np.any(rho_data<0):
    print("negative density found!")
if not np.all(np.diff(h_data)>0):  # check if altitude is monotonically increasing
    print("altitude is not strictly increasing")
    
