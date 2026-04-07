import pandas as pd
import os

input_file = "GDP_per_capita_BD_IND_PAK_2005_2025.csv"
output_file = "GDP_per_capita_BD_IND_PAK_2005_2025_clean.csv"

df = pd.read_csv(input_file)

df = df.rename(columns=lambda x: x.strip())  

expected_cols = ['Country', 'Year', 'GDP_per_capita']

df = df[expected_cols]

df['Year'] = df['Year'].astype(int)
df['GDP_per_capita'] = pd.to_numeric(df['GDP_per_capita'], errors='coerce')

df = df.sort_values(by=['Country', 'Year'])

df.to_csv(output_file, index=False)
print(f"Cleaned data saved to {os.path.abspath(output_file)}")

