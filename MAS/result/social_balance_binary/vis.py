import pandas as pd
import json
import matplotlib.pyplot as plt

cases = {
    int("000000"): "friends",
    int("222222"): "enemies",
    int("222020"): "mix",
}

count = {
    "friends": 0,
    "enemies": 0,
    "mix": 0,
}

file = "result.csv"
data = pd.read_csv(file)
tot = 0
for index, row in data.iterrows():
    case = row['result']
    if case in cases:
        count[cases[case]] += 1
        tot += 1

print("Total cases:", tot)

plt.bar(count.keys(), count.values(),color=['blue', 'red', 'green'])
plt.xlabel('Case')
plt.ylabel('Count')
plt.title('Social Balance Cases')
plt.show()