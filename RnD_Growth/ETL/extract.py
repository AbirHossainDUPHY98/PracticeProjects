import requests
import pandas as pd
from io import StringIO
import os
import time

OUTPUT_DIR = "../raw_data/"
CHUNK_SIZE = 500_000

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── World Bank ────────────────────────────────────────────────────────────────
WB_BASE_URL = "https://api.worldbank.org/v2/country/all/indicator"
WB_PER_PAGE = 1000

WB_INDICATORS = {
    "rd_gdp":              "GB.XPD.RSDV.GD.ZS",
    "gdp_growth":          "NY.GDP.MKTP.KD.ZG",
    "population":          "SP.POP.TOTL",
    "tertiary_enrollment": "SE.TER.ENRR",
}

# ── OECD MSTI ─────────────────────────────────────────────────────────────────
OECD_MEASURES = ["G", "B", "GV", "T_RS"]
OECD_URL = (
    f"https://sdmx.oecd.org/public/rest/data/OECD.STI.STP,DSD_MSTI@DF_MSTI,"
    f"/.A.{'+'.join(OECD_MEASURES)}...?"
    f"startPeriod=1981&endPeriod=2024"
    f"&dimensionAtObservation=AllDimensions"
    f"&format=csvfile"
)
OECD_HEADERS = {
    "Accept":     "application/vnd.sdmx.data+csv; version=1.0",
    "User-Agent": "Mozilla/5.0 (data-download-script)",
}

def save_chunks(df: pd.DataFrame, prefix: str) -> None:
    n_chunks = max(1, (len(df) - 1) // CHUNK_SIZE + 1)
    for i in range(n_chunks):
        chunk = df.iloc[i * CHUNK_SIZE : (i + 1) * CHUNK_SIZE]
        path  = os.path.join(OUTPUT_DIR, f"{prefix}_raw_all_country_all_year.csv")
        chunk.to_csv(path, index=False)
        print(f"  Saved {len(chunk):,} rows → {path}")

# World Bank
def wb_fetch_all_pages(indicator_code: str) -> list[dict]:
    url, page, total, rows = f"{WB_BASE_URL}/{indicator_code}", 1, None, []

    while True:
        params = {"format": "json", "per_page": WB_PER_PAGE, "page": page}

        for attempt in range(3):
            try:
                resp = requests.get(url, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as exc:
                print(f"  Attempt {attempt + 1} failed for page {page}: {exc}")
                time.sleep(2 ** attempt)
        else:
            print(f"  Skipping page {page} after 3 failures.")
            break

        if not isinstance(data, list) or len(data) < 2 or not data[1]:
            break

        meta = data[0]
        if total is None:
            total = int(meta.get("total", 0))
            print(f"  Total records: {total:,}")

        for item in data[1]:
            if item["value"] is not None:
                rows.append({
                    "country":      item["country"]["value"],
                    "country_code": item["countryiso3code"],
                    "year":         int(item["date"]),
                    "indicator":    indicator_code,
                    "value":        item["value"],
                })

        fetched = (page - 1) * WB_PER_PAGE + len(data[1])
        print(f"  Page {page}/{meta.get('pages', '?')} — {fetched:,}/{total:,}", end="\r")

        if page >= int(meta.get("pages", 1)):
            break
        page += 1

    print()
    return rows


def run_worldbank() -> None:
    print("\n" + "═" * 60)
    print("World Bank — fetching all indicators")
    print("═" * 60)

    all_records = []
    for name, code in WB_INDICATORS.items():
        print(f"\n  [{name}]")
        rows = wb_fetch_all_pages(code)
        print(f"  {len(rows):,} non-null records retrieved.")
        all_records.extend(rows)

    df_long = pd.DataFrame(all_records)
    code_to_name = {v: k for k, v in WB_INDICATORS.items()}
    df_long["indicator"] = df_long["indicator"].map(code_to_name)

    df_pivot = (
        df_long
        .pivot_table(
            index=["country", "country_code", "year"],
            columns="indicator",
            values="value",
            aggfunc="first",
        )
        .reset_index()
    )
    df_pivot.columns.name = None

    print(f"\n  Final shape: {df_pivot.shape}")
    print(df_pivot.tail().to_string())
    save_chunks(df_pivot, "wb")

# OECD MSTI
def run_oecd() -> None:
    print("\n" + "═" * 60)
    print("OECD MSTI — fetching all measures")
    print("═" * 60)

    for attempt in range(4):
        try:
            print(f"  Attempt {attempt + 1}…")
            resp = requests.get(OECD_URL, headers=OECD_HEADERS, timeout=120)
            resp.raise_for_status()
            break
        except Exception as exc:
            wait = 2 ** attempt
            print(f"  Error: {exc}. Retrying in {wait}s…")
            time.sleep(wait)
    else:
        raise RuntimeError("OECD fetch failed after 4 attempts.")

    try:
        df = pd.read_csv(StringIO(resp.text), low_memory=False)
    except Exception:
        lines = [l for l in resp.text.splitlines() if not l.startswith("#")]
        df    = pd.read_csv(StringIO("\n".join(lines)), low_memory=False)

    df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")
    df.rename(columns={
        "REFERENCE_AREA": "REF_AREA",
        "REFAREA":        "REF_AREA",
        "TIMEPERIOD":     "TIME_PERIOD",
        "OBSVALUE":       "OBS_VALUE",
    }, inplace=True)

    if "MEASURE" in df.columns:
        df = df[df["MEASURE"].isin(OECD_MEASURES)].copy()

    keep = [c for c in ["REF_AREA", "MEASURE", "TIME_PERIOD", "OBS_VALUE"] if c in df.columns]
    df_clean = df[keep].copy()
    df_clean.columns = ["Country", "Indicator", "Year", "Value"][: len(keep)]
    df_clean["Year"]  = pd.to_numeric(df_clean["Year"],  errors="coerce")
    df_clean["Value"] = pd.to_numeric(df_clean["Value"], errors="coerce")
    df_clean.dropna(subset=["Value"], inplace=True)

    df_pivot = (
        df_clean
        .pivot_table(
            index=["Country", "Year"],
            columns="Indicator",
            values="Value",
            aggfunc="first",
        )
        .reset_index()
    )
    df_pivot.columns.name = None
    df_pivot.sort_values(["Country", "Year"], inplace=True)
    df_pivot.reset_index(drop=True, inplace=True)

    print(f"\n  Final shape: {df_pivot.shape}")
    print(df_pivot.tail().to_string())
    save_chunks(df_pivot, "oecd")

if __name__ == "__main__":
    run_worldbank()
    run_oecd()
    print("\n" + "═" * 60)
    print(f"Done. Files saved in: {os.path.abspath(OUTPUT_DIR)}/")
    print("═" * 60)
