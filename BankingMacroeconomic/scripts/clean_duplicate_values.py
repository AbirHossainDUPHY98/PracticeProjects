import pandas as pd
import os

df = pd.read_csv("Loans_to_domestic_economy_million_BDT.csv")
df = df.drop_duplicates(subset=['year','value'])
# print(df)
df.to_csv("Loans_to_domestic_economy_million_BDT-K.csv", index=False)
