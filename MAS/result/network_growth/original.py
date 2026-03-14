from API import LLMFactory
import pandas as pd
import random
N = 300
M = 3

prompt = """
You've entered a virtual social network.
You're tasked with connecting to exactly {m} individuals from the list below.
Each individual is accompanied by their current number of connections.

User:Friends
{user_friends}

Now, please output your answer with no other description. Please output exactly {m} lines, each line contains one name from the list above. If there are less than {m} names in the list, you may output less than {m} lines.
"""

llm = LLMFactory.get_llm("openai", "gpt-4o-mini", temperature=0.7)

with open("../../profile_samples/names.txt", "r") as f:
    name_list = f.read().strip().split("\n")

name_list = random.sample(name_list, N)
friend_counts = {}

for name in name_list:
    friend_str = "\n".join([f"{name}:{count}" for name, count in friend_counts.items()])
    formatted = prompt.format(user_friends=friend_str, m=M)
    response = llm.generate(formatted).split("\n")
    friend_counts[name] = 0
    if(len(friend_counts) == 1):
        continue
    for line in response:
        line = line.strip()
        if line in friend_counts:
            friend_counts[line] += 1
            friend_counts[name] += 1
data = pd.DataFrame(list(friend_counts.items()), columns=["User", "Friends"])
data.to_csv("original.csv", index=False)
