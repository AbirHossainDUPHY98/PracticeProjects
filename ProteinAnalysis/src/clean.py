import pandas as pd
from pathlib import Path

INPUT = "../raw_data/proteins_raw.tsv"
OUTPUT_CLEAN = "../clean_data/proteins_clean.tsv"
OUTPUT_REMOVED = "../clean_data/removed_sequences.tsv"

Path("../clean_data").mkdir(exist_ok=True)

df = pd.read_table(INPUT)

allowed = set("ACDEFGHIKLMNPQRSTVWYUXO")  # Allowed amino acid letters

def classify_sequence(seq):
    if not isinstance(seq, str) or len(seq) == 0:
        return "invalid_empty"
    bad = set(seq) - allowed
    if not bad:
        return "valid"
    return "invalid_chars"

df["seq_status"] = df["sequence"].apply(classify_sequence)

clean_df = df[df["seq_status"].isin(["valid", "valid_ambiguous"])].copy()
removed_df = df[df["seq_status"] == "invalid_chars"].copy()

clean_df.drop(columns=["seq_status"]).to_csv(OUTPUT_CLEAN, sep="\t", index=False)
removed_df.to_csv(OUTPUT_REMOVED, sep="\t", index=False)

print("\n=== CLEANING REPORT ===")
print(df["seq_status"].value_counts())
print(f"\nKept: {len(clean_df)}")
print(f"\nRemoved: {len(removed_df)}")

#=== CLEANING REPORT ===
#seq_status
#valid            29998
#invalid_chars        2
#Name: count, dtype: int64
#
#Kept: 29998
#
#Removed: 2
