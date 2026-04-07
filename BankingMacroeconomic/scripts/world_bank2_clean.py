import pandas as pd
import numpy as np
import os

raw_file = "world_bank2.csv"
clean_dir = "../data_clean"
os.makedirs(clean_dir, exist_ok=True)
clean_file = os.path.join(clean_dir, "world_bank2_clean.csv")

df = pd.read_csv(raw_file, encoding='cp1252')

df = df.dropna(how='all')

df = df[df['Country Name'] == 'Bangladesh']

year_cols = [c for c in df.columns if '[YR' in c]
df = df[['Series Name'] + year_cols]

df_long = df.melt(id_vars=['Series Name'], value_vars=year_cols,
                  var_name='year', value_name='value')

df_long['year'] = df_long['year'].str.extract(r'\[YR(\d+)\]')[0].astype(int)

df_long['value'] = df_long['value'].replace('..', np.nan).astype(float)

df_long['series_name'] = df_long['Series Name'].str.lower().str.replace(r'[^a-z0-9]+', '_', regex=True)

df_long = df_long.drop(columns=['Series Name'])

df_long.to_csv(clean_file, index=False)
print(f"Cleaned CSV saved to {clean_file}")

