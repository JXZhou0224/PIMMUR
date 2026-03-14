import pandas as pd
from openai import OpenAI
import json
from math import exp
data = pd.read_csv("gpqa_diamond.csv")

processed = []

client = OpenAI()
for index, row in data.iterrows():
    cur = {
        "topic":row["Question"],
        "A":row["Correct Answer"],
        "B": row["Incorrect Answer 1"],
        "C": row["Incorrect Answer 2"],
        "D": row["Incorrect Answer 3"],
        "answer": row["Correct Answer"],
    }
    prompt = """
    Please answer the following question:
    {question}

    A: {A}
    B: {B}
    C: {C}
    D: {D}

    Now answer the question by replying strictly only one of A,B,C,D:
    """.format(question=cur["topic"],A=cur["A"],B=cur["B"],C=cur["C"],D=cur["D"])

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
        for token_info in response.choices[0].logprobs.content[0].top_logprobs:
            cur["likely_answer"].append({
                "answer": token_info.token,
                "prob": exp(token_info.logprob)
            })
            if(len(cur["likely_answer"]) >= 4):
                break
    processed.append(cur)
    print(cur)
json.dump(processed,open("gpqa_processed.json","w"),indent=2)


