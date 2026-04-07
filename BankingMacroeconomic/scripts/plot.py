import pandas as pd
import matplotlib.pyplot as plt
import os
df = pd.read_csv("unemployed_rate.csv")
# print(df.head())

plt.figure(figsize=(10,8))
plt.plot(df['year'], df['value'], marker='o', linestyle='-', color='blue')
plt.title("Unemployment Rate Over Years")
plt.xlabel("Year")
plt.ylabel("Unemployment Rate")
plt.grid(True)
plt.savefig("unemployment_rate.png")
plt.show()

plt.figure(figsize=(10,8))
plt.plot(df['year'], df['change_per_year'], marker='o', linestyle='-', color='red')
plt.title("Change Of Unemployement Rate Over Years")
plt.xlabel("Year")
plt.ylabel("Change of unemployment rate")
plt.grid(True)
plt.savefig("Change_of_unemployment_rate.png")
plt.show()


