import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
STEP = 0.15
# Read CSV



exp1 = "herd_effect_socialiqa/result.csv"
rep1 = "herd_effect_socialiqa/herd_effect_iqa_replicate.csv"
exp2 = "herd_effect/result.csv"
rep2 = "herd_effect/herd_effect_replicate.csv"
def get_bin(file):
    df = pd.read_csv(file)  # columns: self-confidence, perceived confidence, flip
    df = df[df['perceived_confidence'] != df['self_confidence']]  # Filter out cases where self-confidence equals perceived confidence
    df['self_bin'] = round((df['self_confidence'] / STEP).round() * STEP, 1)
    df['perc_bin'] = round((df['perceived_confidence'] / STEP).round() * STEP, 1)
    return df

def get_pivot_table(df):
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
    return pivot_table

df1 = get_bin(exp1)
df2 = get_bin(exp2)

df = pd.concat([df1,df2],ignore_index=True)
pivot_table = get_pivot_table(df)
pivot_table.to_csv("ours_herd_effect_flip_rate_heatmap.csv", index=True)

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
