import pandas as pd
from openai import OpenAI
import json
from math import exp

with open("dataset.jsonl", "r") as f:
    data = pd.read_json(f, lines=True)

example = """{"context": "She was staing overnight for the first time with her friends from the Brownie Troop.", "question": "How would Sasha feel afterwards?", "answerA": "sociable and friendly with others", "answerB": "embarassed and ashamed", "answerC": "would be proud for soiling the sleeping bag"}"""

processed = []

client = OpenAI()
for index, row in data.iterrows():
    cur = {
        "topic":row["context"]+row["question"],
        "A":row["answerA"],
        "B": row["answerB"],
        "C": row["answerC"],
    }
    prompt = """
Please answer the following question:
{question}

A: {A}
B: {B}
C: {C}

Now answer the question by replying strictly only one of A,B,C:
    """.format(question=cur["topic"],A=cur["A"],B=cur["B"],C=cur["C"])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        logprobs=True, # Set to True to get log probabilities
        top_logprobs=5 # Optional: specify the number of top logprobs to return
    )
    cur["likely_answer"] = []

    if response.choices[0].logprobs:
        vis = {"A": 0, "B": 0, "C": 0}
        for token_info in response.choices[0].logprobs.content[0].top_logprobs:
            if token_info.token in ["A", "B", "C"]:
                if vis[token_info.token] == 0:
                    cur["likely_answer"].append({
                        "answer": token_info.token,
                        "prob": exp(token_info.logprob)
                    })
                    vis[token_info.token] = 1
                if(len(cur["likely_answer"]) >= 3):
                    break
        for key in vis:
            if vis[key] == 0:
                cur["likely_answer"].append({
                    "answer": key,
                    "prob": 0.0
                })
    processed.append(cur)
    print(cur)
    json.dump(processed,open("dataset_processed.json","w"),indent=2)


