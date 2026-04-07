import pandas as pd

df = pd.read_table("../results/features.tsv")

corr = df[[
    "length","molecular_weight","hydrophobicity","entropy"
]].corr()  # .corr() calculates Pearson Correlation coefficient. Measures how two variables move together. The inner [] is the list of the columns to check. The outer [] tells to return a new dataframe containing those columns. values {+1 - 0 -1}showing proportionality - no correlation - inverse proportionality. 

print(corr)

# Output: 
#                    length  molecular_weight  hydrophobicity   entropy
#length            1.000000          0.999458       -0.087812  0.132776
#molecular_weight  0.999458          1.000000       -0.091099  0.143257
#hydrophobicity   -0.087812         -0.091099        1.000000  0.138382
#entropy           0.132776          0.143257        0.138382  1.000000

