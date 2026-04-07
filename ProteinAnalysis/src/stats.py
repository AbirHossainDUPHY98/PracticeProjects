import pandas as pd

df = pd.read_table("../results/features.tsv")

print(df.groupby("organism")[["length","hydrophobicity","entropy"]].mean())
print(df.groupby("reviewed")[["length","entropy"]].mean())
