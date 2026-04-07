import pandas as pd

df = pd.read_table("../raw_data/proteins_raw.tsv")

print(f"Total rows: {len(df)}")
print(f"Missing values:\n{df.isnull().sum()}\n")

print(f"Duplicate accessions: {df['accession'].duplicated().sum()}\n")

valid_aa = set('ACDEFGHIKLMNPQRSTVWY')
def check_sequence(seq):
    if not isinstance(seq, str): return False
    return all(aa in valid_aa for aa in seq)

df['valid_seq'] = df['sequence'].apply(check_sequence)
print(f"Invalid sequences: {(~df['valid_seq']).sum()}\n")

df['seq_len'] = df['sequence'].str.len()
mismatch = df[df['seq_len'] != df['length']]
print(f"Length mismatches: {len(mismatch)}\n")

if len(mismatch) > 0:
    print("Example mismatches:")
    print(mismatch[['accession', 'length', 'seq_len']].head())



## Output: 
#Total rows: 30000
#Missing values:
#accession    0
#sequence     0
#organism     0
#reviewed     0
#length       0
#dtype: int64
#
#Duplicate accessions: 0
#
#Invalid sequences: 75
#
#Length mismatches: 0
# So needs cleaning
# XUO are biologically correct, reference in cleaning script.
