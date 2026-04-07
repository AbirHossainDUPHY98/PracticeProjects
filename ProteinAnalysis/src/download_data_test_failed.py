import requests
import pandas as pd
import time
from tqdm import tqdm
from requests.utils import parse_header_links

URL = "https://rest.uniprot.org/uniprotkb/search"
FIELDS = "accession,id,sequence,organism_name,protein_name,length,gene_names"
BATCH_SIZE = 500
SLEEP_TIME = 0.5

def fetch(query, target_count):
    all_results = []
    url = URL
    params = {
        "query": query,
        "fields": FIELDS,
        "format": "json",
        "size": BATCH_SIZE
    }

    with tqdm(total=target_count, desc=f"Downloading {query.split(':')[0]}") as pbar:
        while len(all_results) < target_count and url:
            r = requests.get(url, params=params)  
            r.raise_for_status()
            data = r.json()

            results = data.get("results", [])
            if not results:
                break

            all_results.extend(results)
            pbar.update(len(results))

            links = r.headers.get("Link", "")
            next_url = None

            if links:
                parsed = parse_header_links(links.rstrip('>').replace('>,', '>, '))
                for link in parsed:
                    if link.get("rel") == "next":
                        next_url = link.get("url")

            url = next_url
            params = {}
            time.sleep(SLEEP_TIME)

    return all_results[:target_count]

def process_entry(entry):
    seq_data = entry.get("sequence", {})
    entry_type = entry.get("entryType", "").lower()
    is_reviewed = "reviewed" in entry_type
    return {
            "accession": entry.get("primaryAccession"),
            "sequence": seq_data.get("value", ""),
            "organism": entry.get("organism", {}).get("scientificName", ""),
            "reviewed": is_reviewed,
            "length": seq_data.get("length")
            } 

if __name__ == "__main__":
    targets = [
        ("organism_id:9606", "human", 15000),
        ("organism_id:9913", "cow", 8000),
        ("organism_id:10090", "mouse", 7000)
    ]

    all_rows = []
    for query, label, count in targets:
        print(f"\n>>> Fetching {label} ({count} target)...")

        raw = fetch(query, count)
        rows = [process_entry(p) for p in raw]
        all_rows.extend(rows)
        reviewed_count = sum(1 for r in rows if r['reviewed'])
        print(f"   ✓ Got {len(rows)} ({reviewed_count} reviewed) for {label}")

    df = pd.DataFrame(all_rows)
    df.to_csv("../raw_data/proteins_raw.tsv", sep="\t", index=False)
    
    print(f"\n*** Complete ***")
    print(f"Total: {len(df)} rows")
    print(f"Reviewed:\n{df['reviewed'].value_counts()}")
    print(f"Organisms:\n{df['organism'].value_counts()}")
