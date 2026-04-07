import pandas as pd
import os

raw_file = "../data_raw/IMF-FSI-A.BD.FSKNL_PT.csv"
clean_dir = "../data_clean"
os.makedirs(clean_dir, exist_ok=True)
clean_file = os.path.join(clean_dir, "fsi_loans_total.csv")

df = pd.read_csv(raw_file)

df = df.rename(columns={
    "period": "year",
    df.columns[1]: "value"
})

df["indicator"] = "Loans_total"

df["year"] = df["year"].astype(int)
df["value"] = pd.to_numeric(df["value"], errors='coerce')

df = df[["indicator", "year", "value"]]

df.to_csv(clean_file, index=False)
print(f"Cleaned CSV saved to {clean_file}")

