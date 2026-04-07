import pandas as pd

df = pd.read_csv("bd_macro_indicators_clean.csv")
df_long = df.melt(id_vars="year", var_name="indicator", value_name="value")
df_long.to_csv("bd_macro_indicators_long.csv", index=False)

