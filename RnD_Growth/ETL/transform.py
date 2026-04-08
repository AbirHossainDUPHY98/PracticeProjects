import os
import pandas as pd

RAW        = "../raw_data"
OUT        = "../processed"
YEAR_MIN   = 2000
YEAR_MAX   = 2022
CHUNK_SIZE = 500_000
REGION_COUNTRIES = [
    # East Asia
    "CHN", "JPN", "KOR", "TWN", "SGP", "HKG", "MYS", "THA", "VNM", "IDN",
    # Western Europe
    "DEU", "FRA", "GBR", "SWE", "FIN", "NLD", "CHE", "DNK", "NOR", "AUT",
    "BEL", "IRL",
    # North America
    "USA", "CAN",
    # Others
    "IND", "ISR", "AUS",
]

WB_AGGREGATES = [
    "AFE","AFW","ARB","CEB","EAR","EAS","TEA","EAP","EMU","ECS","TEC","ECA",
    "EUU","FCS","IBD","IBT","IDB","LTE","LCN","LAC","TLA","LMY","MEA","MIC",
    "NAC","OED","OSS","PST","SAS","TSA","SSF","TSS","SSA","SST","WLD","HIC",
    "LIC","LMC","UMC","PRE","INX",
]

ALPHA2_TO_ALPHA3 = {
    'AD':'AND','AE':'ARE','AF':'AFG','AG':'ATG','AI':'AIA','AL':'ALB','AM':'ARM',
    'AO':'AGO','AR':'ARG','AT':'AUT','AU':'AUS','AZ':'AZE','BA':'BIH','BB':'BRB',
    'BD':'BGD','BE':'BEL','BF':'BFA','BG':'BGR','BH':'BHR','BI':'BDI','BJ':'BEN',
    'BM':'BMU','BN':'BRN','BO':'BOL','BR':'BRA','BS':'BHS','BT':'BTN','BW':'BWA',
    'BY':'BLR','BZ':'BLZ','CA':'CAN','CD':'COD','CF':'CAF','CG':'COG','CH':'CHE',
    'CI':'CIV','CK':'COK','CL':'CHL','CM':'CMR','CN':'CHN','CO':'COL','CR':'CRI',
    'CU':'CUB','CV':'CPV','CY':'CYP','CZ':'CZE','DE':'DEU','DJ':'DJI','DK':'DNK',
    'DM':'DMA','DO':'DOM','DZ':'DZA','EC':'ECU','EE':'EST','EG':'EGY','ER':'ERI',
    'ES':'ESP','ET':'ETH','FI':'FIN','FJ':'FJI','FM':'FSM','FO':'FRO','FR':'FRA',
    'GA':'GAB','GB':'GBR','GD':'GRD','GE':'GEO','GG':'GGY','GH':'GHA','GI':'GIB',
    'GL':'GRL','GM':'GMB','GN':'GIN','GR':'GRC','GT':'GTM','GW':'GNB','GY':'GUY',
    'HN':'HND','HR':'HRV','HT':'HTI','HU':'HUN','ID':'IDN','IE':'IRL','IL':'ISR',
    'IM':'IMN','IN':'IND','IQ':'IRQ','IR':'IRN','IS':'ISL','IT':'ITA','JE':'JEY',
    'JM':'JAM','JO':'JOR','JP':'JPN','KE':'KEN','KG':'KGZ','KH':'KHM','KI':'KIR',
    'KM':'COM','KN':'KNA','KP':'PRK','KR':'KOR','KW':'KWT','KY':'CYM','KZ':'KAZ',
    'LA':'LAO','LB':'LBN','LC':'LCA','LI':'LIE','LK':'LKA','LR':'LBR','LS':'LSO',
    'LT':'LTU','LU':'LUX','LV':'LVA','LY':'LBY','MA':'MAR','MC':'MCO','MD':'MDA',
    'ME':'MNE','MG':'MDG','MK':'MKD','ML':'MLI','MM':'MMR','MN':'MNG','MT':'MLT',
    'MU':'MUS','MW':'MWI','MX':'MEX','MY':'MYS','MZ':'MOZ','NE':'NER','NG':'NGA',
    'NI':'NIC','NL':'NLD','NO':'NOR','NP':'NPL','NZ':'NZL','OM':'OMN','PA':'PAN',
    'PE':'PER','PG':'PNG','PH':'PHL','PK':'PAK','PL':'POL','PN':'PCN','PS':'PSE',
    'PT':'PRT','PW':'PLW','PY':'PRY','QA':'QAT','RO':'ROU','RS':'SRB','RU':'RUS',
    'RW':'RWA','SA':'SAU','SB':'SLB','SC':'SYC','SD':'SDN','SE':'SWE','SG':'SGP',
    'SH':'SHN','SI':'SVN','SK':'SVK','SL':'SLE','SM':'SMR','SN':'SEN','SO':'SOM',
    'SR':'SUR','SS':'SSD','ST':'STP','SV':'SLV','SY':'SYR','SZ':'SWZ','TC':'TCA',
    'TD':'TCD','TG':'TGO','TH':'THA','TJ':'TJK','TL':'TLS','TM':'TKM','TN':'TUN',
    'TO':'TON','TR':'TUR','TT':'TTO','TW':'TWN','TZ':'TZA','UA':'UKR','UG':'UGA',
    'US':'USA','UY':'URY','UZ':'UZB','VE':'VEN','VG':'VGB','VN':'VNM','VU':'VUT',
    'WS':'WSM','YE':'YEM','ZA':'ZAF','ZM':'ZMB','ZW':'ZWE',
}

def log(msg):
    print(f"[transform] {msg}")

def save(df, name):
    path = os.path.join(OUT, name)
    df.to_csv(path, index=False)
    log(f"Saved {name}  →  {df.shape[0]:,} rows × {df.shape[1]} cols")

os.makedirs(OUT, exist_ok=True)

log("Building patent lookup from g_patent.tsv ...")
patent_lookup = {}
pat_total = 0

for i, chunk in enumerate(pd.read_csv(
    os.path.join(RAW, "g_patent.tsv"),
    sep="\t",
    usecols=["patent_id", "patent_type", "patent_date"],
    chunksize=CHUNK_SIZE,
    low_memory=False,
)):
    chunk["patent_id"]   = chunk["patent_id"].astype(str)
    chunk["patent_date"] = pd.to_datetime(chunk["patent_date"], errors="coerce")
    chunk["patent_year"] = chunk["patent_date"].dt.year

    chunk = chunk[chunk["patent_year"].between(YEAR_MIN, YEAR_MAX)]
    chunk = chunk.dropna(subset=["patent_year", "patent_type"])
    chunk["patent_year"] = chunk["patent_year"].astype(int)

    for row in chunk[["patent_id", "patent_year", "patent_type"]].itertuples(index=False):
        patent_lookup[row.patent_id] = (row.patent_year, row.patent_type)

    pat_total += len(chunk)
    log(f"  g_patent chunk {i+1}  |  kept so far: {pat_total:,}")

log(f"  patent_lookup built  →  {len(patent_lookup):,} patents in window")

log("Building location lookup from g_location_disambiguated.tsv ...")
loc = pd.read_csv(
    os.path.join(RAW, "g_location_disambiguated.tsv"),
    sep="\t",
    low_memory=False,
    usecols=["location_id", "disambig_country"],
)
loc["country"] = loc["disambig_country"].map(ALPHA2_TO_ALPHA3)
location_lookup = loc.set_index("location_id")["country"].to_dict()
log(f"  location_lookup built  →  {len(location_lookup):,} locations")

log("Processing g_inventor_disambiguated.tsv in chunks ...")

MERGED_PATH  = os.path.join(OUT, "merged_patents.csv")
chunk_counts = []
total_rows   = 0
unmapped_country = 0
unmapped_patent  = 0
first_chunk  = True

for i, chunk in enumerate(pd.read_csv(
    os.path.join(RAW, "g_inventor_disambiguated.tsv"),
    sep="\t",
    usecols=["patent_id", "inventor_id", "location_id"],
    chunksize=CHUNK_SIZE,
    low_memory=False,
)):
    chunk["patent_id"] = chunk["patent_id"].astype(str)

    chunk["patent_year"] = chunk["patent_id"].map(
        lambda x: patent_lookup.get(x, (None, None))[0])
    chunk["patent_type"] = chunk["patent_id"].map(
        lambda x: patent_lookup.get(x, (None, None))[1])

    unmapped_patent += chunk["patent_year"].isna().sum()

    chunk = chunk.dropna(subset=["patent_year", "patent_type"]).copy()
    chunk["patent_year"] = chunk["patent_year"].astype(int)

    chunk["country"] = chunk["location_id"].map(location_lookup)
    unmapped_country += chunk["country"].isna().sum()
    chunk = chunk.dropna(subset=["country"])

    chunk = chunk.drop(columns=["location_id"])

    total_rows += len(chunk)

    chunk.to_csv(MERGED_PATH, mode="a", index=False, header=first_chunk)
    first_chunk = False

    agg = (
        chunk
        .groupby(["country", "patent_year", "patent_type"])
        .agg(
            patent_set   = ("patent_id",   lambda x: set(x)),
            inventor_set = ("inventor_id", lambda x: set(x)),
        )
        .reset_index()
    )
    chunk_counts.append(agg)

    log(f"  inv chunk {i+1}  |  kept rows: {len(chunk):,}  |  total so far: {total_rows:,}")

log(f"  Done.  Total merged rows: {total_rows:,}")
log(f"  Unmapped patents (outside window): {unmapped_patent:,}")
log(f"  Unmapped countries: {unmapped_country:,}")
log(f"  merged_patents.csv written incrementally")

log("Consolidating chunk aggregates into patent_counts ...")

combined = pd.concat(chunk_counts, ignore_index=True)

patent_counts = (
    combined
    .groupby(["country", "patent_year", "patent_type"])
    .agg(
        patent_count   = ("patent_set",   lambda x: len(set.union(*x))),
        inventor_count = ("inventor_set", lambda x: len(set.union(*x))),
    )
    .reset_index()
    .rename(columns={"country": "country_code", "patent_year": "year"})
)

log(f"  patent_counts shape: {patent_counts.shape}")
log(f"  patent types found: {patent_counts['patent_type'].unique().tolist()}")
save(patent_counts, "patent_counts.csv")

log("Loading wb_raw_all_country_all_year.csv ...")
wb = pd.read_csv(os.path.join(RAW, "wb_raw_all_country_all_year.csv"))

wb_clean = wb[~wb["country_code"].isin(WB_AGGREGATES)].copy()

wb_clean = wb_clean[wb_clean["year"].between(YEAR_MIN, YEAR_MAX)]

if "country" in wb_clean.columns:
    wb_clean = wb_clean.drop(columns=["country"])

log(f"  wb_clean shape: {wb_clean.shape}")
log(f"  rd_gdp coverage: {wb_clean['rd_gdp'].notna().sum():,} / {len(wb_clean):,} rows")
save(wb_clean, "wb_clean.csv")

log("Building analytical subsets ...")

subset_A = pd.merge(
    patent_counts,
    wb_clean[["country_code", "year", "gdp_growth", "population"]],
    on=["country_code", "year"],
    how="inner",
).dropna(subset=["gdp_growth"])

log(f"  subset_A  countries: {subset_A['country_code'].nunique()}  "
    f"rows: {len(subset_A):,}")
save(subset_A, "subset_A.csv")

subset_B = pd.merge(
    patent_counts,
    wb_clean[["country_code", "year", "gdp_growth", "population",
              "rd_gdp", "tertiary_enrollment"]],
    on=["country_code", "year"],
    how="inner",
).dropna(subset=["rd_gdp"])

log(f"  subset_B  countries: {subset_B['country_code'].nunique()}  "
    f"rows: {len(subset_B):,}")
save(subset_B, "subset_B.csv")

subset_C = pd.merge(
    patent_counts,
    wb_clean,
    on=["country_code", "year"],
    how="inner",
)
subset_C = subset_C[subset_C["country_code"].isin(REGION_COUNTRIES)]

log(f"  subset_C  countries: {subset_C['country_code'].nunique()}  "
    f"rows: {len(subset_C):,}")
save(subset_C, "subset_C.csv")

OECD_PATH = os.path.join(RAW, "oecd_raw_all_country_all_year.csv")

if os.path.exists(OECD_PATH):
    log("Loading oecd_raw_all_country_all_year.csv ...")
    oecd = pd.read_csv(OECD_PATH)

    oecd.columns = (
        oecd.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )

    oecd = oecd.rename(columns={
        'country' : 'country_code',
        'b'       : 'rd_business',       # BERD
        'g'       : 'rd_government',     # GOVERD
        'gv'      : 'rd_gdp_pct',        # GERD as % of GDP
        't_rs'    : 'researchers_count', # Total researchers FTE
    })

    oecd = oecd[oecd["year"].between(YEAR_MIN, YEAR_MAX)]

    oecd = oecd.dropna(subset=["country_code", "year"])
    oecd["year"] = oecd["year"].astype(int)

    log(f"  oecd_clean shape: {oecd.shape}")
    log(f"  OECD countries: {oecd['country_code'].nunique()}")
    save(oecd, "oecd_clean.csv")

    log("  OECD variable coverage:")
    for col in oecd.columns:
        if col not in ["country_code", "year"]:
            pct = oecd[col].notna().mean() * 100
            log(f"    {col:<25} {pct:.1f}%")
else:
    log("  oecd_raw_all_country_all_year.csv not found — skipping OECD step.")
    log("  Download from: https://stats.oecd.org → MSTI → Export as CSV")
    log("  Expected filename: raw_data/oecd_raw_all_country_all_year.csv")

# ── STEP 7: final summary ──────────────────────────────────────────────────────

log("")
log("=" * 55)
log("TRANSFORMATION COMPLETE")
log("=" * 55)

outputs = {
    "patent_counts" : "Patents + inventors by country + year + type",
    "wb_clean"      : "World Bank — aggregates removed, years filtered",
    "subset_A"      : "Patents + GDP growth  (broadest, ~180 countries)",
    "subset_B"      : "Patents + rd_gdp      (R&D focused, ~60-80 countries)",
    "subset_C"      : "Patents + all WB vars (regional deep dive)",
    "oecd_clean"    : "OECD — BERD, GOVERD, GERD%, researchers FTE",
}

for fname, desc in outputs.items():
    path = os.path.join(OUT, f"{fname}.csv")
    if os.path.exists(path):
        df   = pd.read_csv(path, nrows=0)
        size = os.path.getsize(path) / 1024
        log(f"  {fname:<20} {desc}")
        log(f"  {'':20} cols: {list(df.columns)}")
        log(f"  {'':20} size: {size:.0f} KB")
        log("")
