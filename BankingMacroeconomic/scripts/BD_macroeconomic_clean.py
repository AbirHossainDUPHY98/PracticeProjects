import pandas as pd
import os

raw_file = "../data_raw/BD_economic_indicators.csv"
clean_dir = "../data_clean"
os.makedirs(clean_dir, exist_ok=True)
clean_file = os.path.join(clean_dir, "bd_macro_indicators.csv")

df = pd.read_csv(raw_file)

df.columns = df.columns.str.strip()

df = df.rename(columns={
    "Year": "year",
    "GDP": "gdp",
    "GDP per capita": "gdp_per_capita",
    "GDP growth": "gdp_growth",
    "Inflation rate": "inflation_rate",
    "Unemployed rate": "unemployed_rate",
    "Government debt": "government_debt",
    "Total Investment": "total_investment"
})

def clean_numeric(x):
    if pd.isna(x):
        return None
    x = str(x).replace("%", "").replace(",", "")
    try:
        return float(x)
    except:
        return None

for col in ["gdp", "gdp_per_capita", "gdp_growth", "inflation_rate",
            "unemployed_rate", "government_debt", "total_investment"]:
    df[col] = df[col].apply(clean_numeric)

df["year"] = df["year"].astype(int)

df.to_csv(clean_file, index=False)
print(f"Cleaned CSV saved to {clean_file}")

