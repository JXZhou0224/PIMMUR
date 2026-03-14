from API import LLMFactory, BaseLLM
import pandas as pd
import json

prompt_template = """
Question:
{question}
A: {A}
B: {B}
C: {C}

----
You noticed that 9 agents think the answer is {steer}.
and 1 agent thinks the answer is {original}.
----

Now please output your answer, to the question. Please answer only A, B or C.
"""
llm = LLMFactory.get_llm("openai", "gpt-4o-mini")
dataset = json.load(open(f"dataset_processed.json","r"))
cnt = 0
save_dir = f"herd_effect_iqa_replicate.csv"
processed = 0
tot = 0
try:
    result = pd.read_csv(save_dir)
    processed = result.shape[0]
except (FileNotFoundError, pd.errors.EmptyDataError):   
    result = pd.DataFrame({"qid":[],"self_confidence":[],"perceived_confidence":[],"flipped":[]})
for ins in dataset:
    for i in range(1,3):        
        if(tot < processed):
            tot += 1
            continue
        question = prompt_template.format(question=ins["topic"],A=ins["A"],B=ins["B"],C=ins["C"],steer=ins["likely_answer"][i]["answer"],original=ins["likely_answer"][0]["answer"])
        final_ans = llm.generate(question)
        flipped = 0
        if(final_ans != ins["likely_answer"][0]["answer"]):
            flipped = 1
        result = pd.concat([result, pd.DataFrame({
            "qid": cnt,
            "self_confidence": ins["likely_answer"][0]["prob"],
            "perceived_confidence": ins["likely_answer"][i]["prob"],
            "flipped": flipped
        }, index=[0])], ignore_index=True)
        result.to_csv(save_dir, index=False)
    cnt+=1
    print(f"Simulation for topic '{ins['topic']}' completed.")