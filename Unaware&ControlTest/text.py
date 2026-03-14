import json

with open("Logs_claude-sonnet-4-20250514.jsonl", "r") as file:
    lines = file.readlines()
data = [json.loads(line) for line in lines]
for entry in data:
    print(f"Filename: {entry['filename']}")
    print(f"Result: {entry['result']}")
    print("-" * 40)
    ans = input("unaware? (y/n): ")
    if(ans == 'y'):
        ans = "yes"
    else:
        ans = "no"
    with open("Results_claude-sonnet-4-20250514.txt", "a") as file:
        file.write(f"{entry['filename']} {ans}\n")