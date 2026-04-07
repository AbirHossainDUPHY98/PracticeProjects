import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("GDP_per_capita_BD_IND_PAK_2005_2025_clean.csv")

plt.figure(figsize=(10,6))  
sns.lineplot(data=df, x='Year', y='GDP_per_capita', hue='Country', marker='o')  

plt.title("GDP per Capita: Bangladesh vs India vs Pakistan (2005-2025)")
plt.ylabel("GDP per Capita (current US$)")
plt.xlabel("Year")
plt.grid(True)
plt.tight_layout() 

plt.savefig("GDP_per_capita_plot.png")  
plt.show()


