import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

IN         = "../processed"
OUT        = "analytical_data"
CHUNK_SIZE = 500_000

def log(msg):
    print(f"[load] {msg}")

def save_parquet(df, name):
    path = os.path.join(OUT, name)
    df.to_parquet(path, engine="pyarrow", compression="snappy", index=False)
    size = os.path.getsize(path) / 1024
    log(f"Saved {name}  →  {df.shape[0]:,} rows  {size:.0f} KB")

os.makedirs(OUT, exist_ok=True)

log("Loading patent_counts.csv ...")
patent_counts = pd.read_csv(os.path.join(IN, "patent_counts.csv"))

patent_counts["country_code"]   = patent_counts["country_code"].astype("category")
patent_counts["year"]           = patent_counts["year"].astype("int16")
patent_counts["patent_type"]    = patent_counts["patent_type"].astype("category")
patent_counts["patent_count"]   = patent_counts["patent_count"].astype("int32")
patent_counts["inventor_count"] = patent_counts["inventor_count"].astype("int32")

save_parquet(patent_counts, "patent_counts.parquet")

log("Loading wb_clean.csv ...")
wb_clean = pd.read_csv(os.path.join(IN, "wb_clean.csv"))

wb_clean["country_code"]        = wb_clean["country_code"].astype("category")
wb_clean["year"]                = wb_clean["year"].astype("int16")
wb_clean["gdp_growth"]          = wb_clean["gdp_growth"].astype("float32")
wb_clean["population"]          = wb_clean["population"].astype("float64")
wb_clean["rd_gdp"]              = wb_clean["rd_gdp"].astype("float32")
wb_clean["tertiary_enrollment"] = wb_clean["tertiary_enrollment"].astype("float32")

save_parquet(wb_clean, "wb_clean.parquet")

for name in ["subset_A", "subset_B", "subset_C"]:
    log(f"Loading {name}.csv ...")
    df = pd.read_csv(os.path.join(IN, f"{name}.csv"))

    df["country_code"]   = df["country_code"].astype("category")
    df["year"]           = df["year"].astype("int16")
    df["patent_type"]    = df["patent_type"].astype("category")
    df["patent_count"]   = df["patent_count"].astype("int32")
    df["inventor_count"] = df["inventor_count"].astype("int32")
    df["gdp_growth"]     = df["gdp_growth"].astype("float32")
    df["population"]     = df["population"].astype("float64")

    if "rd_gdp" in df.columns:
        df["rd_gdp"] = df["rd_gdp"].astype("float32")
    if "tertiary_enrollment" in df.columns:
        df["tertiary_enrollment"] = df["tertiary_enrollment"].astype("float32")

    save_parquet(df, f"{name}.parquet")

log("Loading oecd_clean.csv ...")
oecd_clean = pd.read_csv(os.path.join(IN, "oecd_clean.csv"))

oecd_clean["country_code"]       = oecd_clean["country_code"].astype("category")
oecd_clean["year"]               = oecd_clean["year"].astype("int16")
oecd_clean["rd_business"]        = oecd_clean["rd_business"].astype("float32")
oecd_clean["rd_government"]      = oecd_clean["rd_government"].astype("float32")
oecd_clean["rd_gdp_pct"]         = oecd_clean["rd_gdp_pct"].astype("float32")
oecd_clean["researchers_count"]  = oecd_clean["researchers_count"].astype("float32")

save_parquet(oecd_clean, "oecd_clean.parquet")

log("")
log("=" * 55)
log("LOAD COMPLETE")
log("=" * 55)

outputs = [
    "patent_counts.parquet",
    "wb_clean.parquet",
    "subset_A.parquet",
    "subset_B.parquet",
    "subset_C.parquet",
    "oecd_clean.parquet",
    "merged_patents.parquet",
]

for name in outputs:
    path = os.path.join(OUT, name)
    if os.path.isdir(path):
        size = sum(
            os.path.getsize(os.path.join(root, f))
            for root, _, files in os.walk(path)
            for f in files
        ) / 1024
        partitions = len([
            d for d in os.listdir(path)
            if os.path.isdir(os.path.join(path, d))
        ])
        log(f"  {name:<35} {size:.0f} KB  ({partitions} partitions)")
    elif os.path.isfile(path):
        df   = pd.read_parquet(path)
        size = os.path.getsize(path) / 1024
        log(f"  {name:<35} {size:.0f} KB  cols: {list(df.columns)}")
    log("")
