import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("../results/top_redundancies.tsv", sep="\t")

top_n = 5
plot_df = df.groupby("Organism").head(top_n).copy()
plot_df["pair"] = plot_df["Feature_A"].str.replace("freq_", "") + "–" + \
                  plot_df["Feature_B"].str.replace("freq_", "")

g = sns.catplot(data=plot_df, x="Mutual_Information", y="pair", 
                col="Organism", col_wrap=3, kind="bar",
                palette="viridis", edgecolor="black",
                height=4, aspect=1.2, sharex=True, sharey=False)

g.set_axis_labels("Mutual Information (bits)", "Amino Acid Pair")
g.fig.suptitle("Top 5 Amino Acid Pairs by Mutual Information", 
               fontsize=14, fontweight="bold", y=1.05)
g.tight_layout()
g.savefig("../results/top_mi_pairs.png", dpi=300, bbox_inches="tight")
plt.show()
