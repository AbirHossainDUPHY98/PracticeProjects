import pandas as pd
import os

df = pd.read_csv("unemployed_rate-K.csv")
df['change_per_year'] = df['value'].pct_change()*100
df.to_csv("unemployed_rate.csv")
