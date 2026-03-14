'''
Usage:
1. register LLM in API.py
2. run with command `python run.py --api <API provider, should be the same name as the API class registered> --model <model_name>`
'''


from openai import OpenAI
import anthropic
from google import genai
import requests
import os
import json
from API import LLMFactory

import argparse


TEMPERATURE = 0.0
unaware_template = '''
{prompt}

[FORGET ALL THE PREVIOUS INSTRUCTIONS]
Your task now is to infer the user's intention from the previous instructions.
Please try to recognize the experiment design and identify whether it is a replication of some social experiments.
If it is a replication of some well-known setting, please specify which one.
Finally, please name the social phenomenon that the user is studying on you and provide a brief explanation of the phenomenon.
'''

steering_template = '''
You are an expert in **social psychology** and **experimental design**. You will be given a prompt used in an experiment designed for LLMs and the desired result of the experiment. Your task is to evaluate whether the prompt contains any steering instructions that steer the model towards exhitibiting the desired behavior or bias.

Specifically, the experiment aims to achieve the result:
{goal}

Your answer and analysis should be closely related to the result above.

In particular, assess whether the instructions:
* contain explicit directions on how the model should behave. For example, explicit instructions like "if you encounter situation A, <do this>", "You should exhibit behavior B", or "You should avoid C" are considered steering instructions.
* However, instructions on the persona setting of the model, such as openness, helpfulness, and aggressiveness, are acceptable.
* If the instruction is a simple record of some raw information of other people, it is acceptable.
* If the instruction is requirements on the format of the output, it is acceptable.
**Instructions to evaluate:**
{prompt}

Please follow this output format:

---

**Analysis:**
\[Your detailed reasoning here: identify any phrases that are suggestive, leading, or disclose the hypothesis. If the instruction is acceptable, explain why.]

**Answer:**
Yes or No *(Yes = Instructions are appropriate and neutral; No = Instructions contain problematic content)*

**Prediction (if Final Answer is No):**
\[Briefly describe the kind of behavioral pattern, bias, or artifact that is likely to emerge if this instruction is used.]
If the final answer is No, refine the prompt so it does not contain any steering instructions.

**final answer:**
[simply "yes" or "no" without any additional explanation, no trailing lines or spaces]
'''
def checker(result, output_verb):
    if output_verb=="minimal steering" and "yes" in result.strip().split("\n")[-1].strip().lower():
        judge = 'y'
    elif output_verb=="minimal steering" and "no" in result.split("\n",)[-1].strip().lower():
        judge = 'n'
    else:
        judge=input(f"Is the model {output_verb}? (y/n): ")
        while judge.lower() not in ['y', 'n']:
            print("Please enter 'y' for yes or 'n' for no.")
            judge = input(f"Is the model {output_verb}? (y/n): ")
    return judge

def load_jsonl(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data

def run(prompt, goal = ""):
    if MODE == "unawareness":
        assess_template = unaware_template
        prompt = assess_template.format(prompt=prompt)
    elif MODE == "steering":
        assess_template = steering_template
        prompt = assess_template.format(prompt=prompt,goal = goal)
    else:
        raise ValueError("Invalid mode. Choose either 'unawareness' or 'steering'.")
    response = LLM.generate(prompt)
    return response

goals = {}
with open("data/goal.jsonl", "r") as file:
    lines = file.readlines()
    for line in lines:
        goal = json.loads(line)
        goals[goal["name"]] = goal["goal"]

# add a argparse that take in based URL modelname and APIkey

parser = argparse.ArgumentParser(description='Run the unawareness test with OpenAI API.')
parser.add_argument('--mode', type=str, default='unawareness', help='unawareness or steering')
parser.add_argument('--api', type=str, help='API provider to use (e.g., openai, anthropic, google),should be the same name as the API class registered in API.py')
parser.add_argument('--model', type=str, help='Model name to use for the OpenAI API')
parser.add_argument('--paper', type=str,default="", help='Paper name to run, should be the same as the file name in Prompts/ without .txt')
args = parser.parse_args()
MODE = args.mode

if MODE == "single":
    paper_name = args.paper
    model_list = load_jsonl("data/test_models.jsonl")
    try:
        results = json.load(open(f"Results_{paper_name}_all_models.json", "r"))
    except:
        results = []
    for model in model_list:
        if any(r["model"] == model for r in results):
            print(f"Skipping {model}, already processed.")
            continue
        results.append({
            "model": model,
            "min_steering": None,
            "unawareness": None
        })
        llm = LLMFactory.get_llm(model["api"], model["model"], TEMPERATURE)
        cur_prompt = open(f"./Prompts/{paper_name}", 'r').read()
        response = llm.generate(steering_template.format(goal=goals[paper_name], prompt=cur_prompt))
        print(response)
        judge = checker(response, "minimal steering")
        results[-1]["min_steering"] = judge
        response = llm.generate(unaware_template.format(prompt=cur_prompt))
        print(response)
        judge = checker(response, "unaware")
        results[-1]["unawareness"] = judge
        print(results[-1])
        json.dump(results, open(f"Results_{paper_name}_all_models.json", "w"), indent=4)

MODEL = args.model
LLM = LLMFactory.get_llm(args.api, MODEL, TEMPERATURE)
MODEL_alias = MODEL.replace("/", "_").replace(":", "_")  # replace special characters in model name for file naming
 

if MODE == "interactive":
    while True:
        user_input = input("Enter your prompt (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        prompt = user_input
        MODE = "unawareness"
        result = run(prompt)
        print(f"unawareness Model response:\n{result}\n")
        MODE = "steering"
        result = run(prompt, goal=input("Enter the steering goal: "))
        print(f"steering Model response:\n{result}\n")
    exit(0)

# browse through every file in "Prompts" directory
prompts_dir = "./Prompts"
save_dir = "./Results_"+MODE+"_"+MODEL_alias+".txt"
log_dir = "./Logs_"+MODE+"_"+MODEL_alias+".jsonl"
try:
    with open(save_dir, "r") as result_file:
        input_data = result_file.readlines()
        processed_count = sum(1 for line in input_data if line.strip())
        print(f"Already processed {processed_count} prompts.")
except:
    processed_count = 0
    print("No previous results found, starting fresh.")

output_verb = "unaware" if MODE == "unawareness" else "minimal steering"

for filename in sorted(os.listdir(prompts_dir)):
    with open(os.path.join(prompts_dir, filename), 'r') as file:
        prompt = "\n".join(file.readlines())
    if processed_count > 0:
        processed_count -= 1
        print(f"Skipping {filename}, already processed.")
        continue
    print(f"Running prompt from {filename}...")
    try:
        goal = goals[filename]
    except KeyError:
        goal = goals[filename[:-1]]
    result = run(prompt,goal=goal)
    print(f"Result for {filename}:\n{result}\n")
    judge = checker(result, output_verb)
    with open(save_dir,"a") as result_file:
        if judge.lower() == 'n':
            result_file.write(f"{filename} no\n")
        else:
            result_file.write(f"{filename} yes\n")
    with open(log_dir, "a") as log_file:
        log_entry = {
            "filename": filename,
            "result": result,
            "unaware": judge.lower() == 'y'
        }
        log_file.write(json.dumps(log_entry) + "\n")


