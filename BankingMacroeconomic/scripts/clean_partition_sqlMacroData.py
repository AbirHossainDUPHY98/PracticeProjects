import pandas as pd
import os
# df = pd.read_csv("macro_prepared.csv")
df = pd.read_csv("macro_banking_overlap.csv")
df = df.drop_duplicates()
df = df.dropna(subset=['value', 'change_per_year'])
for indicator in df['indicator_name'].unique():
    subset = df[df['indicator_name'] == indicator]
    filename = os.path.join(os.getcwd(), f"{indicator}.csv")
    subset.to_csv(filename,index=False)
print('Done')
