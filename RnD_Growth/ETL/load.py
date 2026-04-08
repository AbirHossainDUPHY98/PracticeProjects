"""
load.py
=======
R&D Growth Study — Load Layer
------------------------------
Reads cleaned CSVs from processed/
Enforces dtypes, compresses, writes to analytical_data/ as parquet.

Inputs  (../processed/):
    patent_counts.csv
    wb_clean.csv
    subset_A.csv  subset_B.csv  subset_C.csv
    oecd_clean.csv
    merged_patents.csv             ← large, read in chunks

Outputs (../analytical_data/):
    patent_counts.parquet
    wb_clean.parquet
    subset_A.parquet
    subset_B.parquet
    subset_C.parquet
    oecd_clean.parquet
    merged_patents.parquet/        ← partitioned directory by patent_year
        patent_year=2000/
        patent_year=2001/
        ...
        patent_year=2022/
"""

import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# ── CONFIG ─────────────────────────────────────────────────────────────────────

IN         = "../processed"
OUT        = "analytical_data"
CHUNK_SIZE = 500_000

# ── HELPERS ────────────────────────────────────────────────────────────────────

def log(msg):
    print(f"[load] {msg}")

def save_parquet(df, name):
    path = os.path.join(OUT, name)
    df.to_parquet(path, engine="pyarrow", compression="snappy", index=False)
    size = os.path.getsize(path) / 1024
    log(f"Saved {name}  →  {df.shape[0]:,} rows  {size:.0f} KB")

# ── STEP 0: setup ──────────────────────────────────────────────────────────────

os.makedirs(OUT, exist_ok=True)

# ── STEP 1: patent_counts ──────────────────────────────────────────────────────

log("Loading patent_counts.csv ...")
patent_counts = pd.read_csv(os.path.join(IN, "patent_counts.csv"))

patent_counts["country_code"]   = patent_counts["country_code"].astype("category")
patent_counts["year"]           = patent_counts["year"].astype("int16")
patent_counts["patent_type"]    = patent_counts["patent_type"].astype("category")
patent_counts["patent_count"]   = patent_counts["patent_count"].astype("int32")
patent_counts["inventor_count"] = patent_counts["inventor_count"].astype("int32")

save_parquet(patent_counts, "patent_counts.parquet")

# ── STEP 2: wb_clean ──────────────────────────────────────────────────────────

log("Loading wb_clean.csv ...")
wb_clean = pd.read_csv(os.path.join(IN, "wb_clean.csv"))

wb_clean["country_code"]        = wb_clean["country_code"].astype("category")
wb_clean["year"]                = wb_clean["year"].astype("int16")
wb_clean["gdp_growth"]          = wb_clean["gdp_growth"].astype("float32")
wb_clean["population"]          = wb_clean["population"].astype("float64")
wb_clean["rd_gdp"]              = wb_clean["rd_gdp"].astype("float32")
wb_clean["tertiary_enrollment"] = wb_clean["tertiary_enrollment"].astype("float32")

save_parquet(wb_clean, "wb_clean.parquet")

# ── STEP 3: subsets A, B, C ───────────────────────────────────────────────────

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

    # rd_gdp and tertiary_enrollment only exist in B and C
    if "rd_gdp" in df.columns:
        df["rd_gdp"] = df["rd_gdp"].astype("float32")
    if "tertiary_enrollment" in df.columns:
        df["tertiary_enrollment"] = df["tertiary_enrollment"].astype("float32")

    save_parquet(df, f"{name}.parquet")

# ── STEP 4: oecd_clean ────────────────────────────────────────────────────────

log("Loading oecd_clean.csv ...")
oecd_clean = pd.read_csv(os.path.join(IN, "oecd_clean.csv"))

oecd_clean["country_code"]       = oecd_clean["country_code"].astype("category")
oecd_clean["year"]               = oecd_clean["year"].astype("int16")
oecd_clean["rd_business"]        = oecd_clean["rd_business"].astype("float32")
oecd_clean["rd_government"]      = oecd_clean["rd_government"].astype("float32")
oecd_clean["rd_gdp_pct"]         = oecd_clean["rd_gdp_pct"].astype("float32")
oecd_clean["researchers_count"]  = oecd_clean["researchers_count"].astype("float32")

save_parquet(oecd_clean, "oecd_clean.parquet")

# ── STEP 5: merged_patents — chunked + partitioned by patent_year ─────────────
#
# Too large (675MB, 16M rows) to load fully.
# Written as a partitioned parquet directory — one sub-folder per year.
# This lets analysis notebooks filter by year at file level:
#   pd.read_parquet("merged_patents.parquet",
#                   filters=[("patent_year", "==", 2015)])
# pyarrow only reads the matching partition — rest is untouched.

log("Loading merged_patents.csv in chunks → partitioned parquet ...")

MERGED_OUT  = os.path.join(OUT, "merged_patents.parquet")
total_rows  = 0
writers     = {}   # patent_year → ParquetWriter

# pyarrow schema — enforced explicitly so all chunks write identical schema
SCHEMA = pa.schema([
    pa.field("patent_id",    pa.string()),
    pa.field("inventor_id",  pa.string()),
    pa.field("patent_year",  pa.int16()),
    pa.field("patent_type",  pa.dictionary(pa.int8(), pa.string())),
    pa.field("country",      pa.dictionary(pa.int16(), pa.string())),
])

os.makedirs(MERGED_OUT, exist_ok=True)

for i, chunk in enumerate(pd.read_csv(
    os.path.join(IN, "merged_patents.csv"),
    chunksize=CHUNK_SIZE,
    low_memory=False,
    dtype={
        "patent_id"   : str,
        "inventor_id" : str,
        "patent_year" : "int16",
        "patent_type" : "category",
        "country"     : "category",
    }
)):
    total_rows += len(chunk)

    # write each year group to its own partition file
    for year, group in chunk.groupby("patent_year"):
        year_dir = os.path.join(MERGED_OUT, f"patent_year={year}")
        os.makedirs(year_dir, exist_ok=True)

        if year not in writers:
            part_path = os.path.join(year_dir, "part-0.parquet")
            writers[year] = pq.ParquetWriter(part_path, SCHEMA, compression="snappy")

        table = pa.Table.from_pandas(
            group.reset_index(drop=True),
            schema=SCHEMA,
            preserve_index=False
        )
        writers[year].write_table(table)

    log(f"  chunk {i+1}  |  total rows so far: {total_rows:,}")

# close all open writers
for year, writer in writers.items():
    writer.close()

# size of entire partitioned directory
total_size = sum(
    os.path.getsize(os.path.join(root, f))
    for root, _, files in os.walk(MERGED_OUT)
    for f in files
) / 1024
log(f"Saved merged_patents.parquet/  →  {total_rows:,} rows  {total_size:.0f} KB")

# ── STEP 6: summary ───────────────────────────────────────────────────────────

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
