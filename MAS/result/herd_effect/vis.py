import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
STEP = 0.15
# Read CSV
exp = "result.csv"
rep = "herd_effect_replicate.csv"
df = pd.read_csv(rep)  # columns: self-confidence, perceived confidence, flip

df['self_bin'] = round((df['self_confidence'] / STEP).round() * STEP, 1)
df['perc_bin'] = round((df['perceived_confidence'] / STEP).round() * STEP, 1)

# Compute mean flip rate per bin
pivot_table = df.pivot_table(
    index='perc_bin',
    columns='self_bin',
    values='flipped',
    aggfunc='mean'
)

# Ensure sorted order
pivot_table = pivot_table.sort_index(ascending=False)
pivot_table = pivot_table[pivot_table.columns.sort_values()]
print(pivot_table)

# Plot
plt.figure(figsize=(8,5))
sns.heatmap(
    pivot_table,
    annot=True,
    fmt=".2f",
    cmap="RdBu_r",
    vmin=0, vmax=1,
    cbar_kws={'label': 'Flip Rate'}
)
plt.xlabel("Self Confidence")
plt.ylabel("Perceived Confidence")
plt.show()
