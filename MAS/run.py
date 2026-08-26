import argparse,json
from simulation import HerdEffect,SocialBalance,NetworkGrowth,BaseSimulation,SimulationFactory
from API import LLMFactory, BaseLLM
from config_generators import GeneratorFactory,BaseGenerator,HerdEffectGenerator
import pandas as pd
import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="Run the MAS simulation.")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file.")
    return parser.parse_args()

def load_config(config_dir):
    return json.load(open(config_dir,"r"))


question_template = """
{question}

A: {A}
B: {B}
C: {C}
"""
def herd_effect(config):
    llm = LLMFactory.get_llm(config["provider"], config["model"])
    dataset = json.load(open(f"datasets/{config['dataset']}","r"))
    generator = HerdEffectGenerator()
    cnt = 0
    save_dir = f"result/{config['name']}"
    processed = 0
    tot = 0
    try:
        result = pd.read_csv(f"{save_dir}/result.csv")
        processed = result.shape[0]
    except (FileNotFoundError, pd.errors.EmptyDataError):   
        result = pd.DataFrame({"qid":[],"self_confidence":[],"perceived_confidence":[],"flipped":[]})
    for ins in dataset:
        question = question_template.format(question=ins["topic"],A=ins["A"],B=ins["B"],C=ins["C"])
        for i in range(0,3):        
            if(tot < processed):
                tot += 1
                continue
            sim_config = generator.generate(question,"A",ins["likely_answer"][i]["answer"],config["agent_n"],config["agreeing_agent_n"])
            simulation = HerdEffect(sim_config,llm,question,save_dir=save_dir)
            simulation.run(config["rounds"])
            final_ans = simulation.opinion_arc[-1]
            flipped = 0
            if(final_ans != ins["likely_answer"][0]["answer"]):
                flipped = 1
            result = pd.concat([result, pd.DataFrame({
                "qid": cnt,
                "self_confidence": ins["likely_answer"][0]["prob"],
                "perceived_confidence": ins["likely_answer"][i]["prob"],
                "flipped": flipped
            }, index=[0])], ignore_index=True)
            result.to_csv(f"{save_dir}/result.csv", index=False)
            open(f"{save_dir}/log.jsonl","a").write(json.dumps(simulation.opinion_arc)+"\n")
        cnt+=1
        print(f"Simulation for topic '{ins['topic']}' completed.")

social_balance_topic = """
Throughout the conversation, please express your likes and dislikes towards other agents actively, according to entry in your profile.
"""

def social_balance(config):
    llm = LLMFactory.get_llm(config["provider"], config["model"])
    generator = GeneratorFactory.get_generator(config["config_generator"])
    cnt = 0
    save_dir = f"result/{config['name']}"
    processed = 0
    tot = 0
    try:
        result = pd.read_csv(f"{save_dir}/result.csv")
        processed = result.shape[0]
    except (FileNotFoundError, pd.errors.EmptyDataError):   
        result = pd.DataFrame({"n":[],"result":[]})
    for iter in range(config["simulation_n"]):       
        if(tot < processed):
            tot += 1
            continue
        sim_config = generator.generate(config["agent_n"],cnt)
        simulation = SocialBalance(sim_config,llm,social_balance_topic,save_dir=save_dir)
        simulation.run(config["rounds"])
        final_ans = simulation.relation_arc[-1]
        result = pd.concat([result, pd.DataFrame({
            "n": cnt,
            "result": final_ans
        }, index=[0])], ignore_index=True)
        result.to_csv(f"{save_dir}/result.csv", index=False)
        open(f"{save_dir}/log.jsonl","a").write(json.dumps(simulation.relation_arc)+"\n")
        cnt+=1
        print(f"Simulation for {iter} completed.")

def network_growth(config):
    do_load = ''
    while do_load.lower() not in ['y','n']:
        do_load = input("Load existing data? (y/n): ")
    llm = LLMFactory.get_llm(config["provider"], config["model"])
    cur_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    sim = NetworkGrowth(llm,agent_n=config["agent_n"],friend_m=config["friend_m"],chat_round=config["rounds"])
    if do_load.lower() == 'y':
        sim.load()
    friend_count = sim.run()
    res = [{"name": agent, "friends_n": friends_n} for agent, friends_n in friend_count.items()]
    df = pd.DataFrame(res)
    df.to_csv(f"result/{config['name']}/result_{cur_time}.csv", index=False)
    
def default(config):
    sim_config = GeneratorFactory.get_generator(config["config_generator"]).generate(**config["config_args"])
    llm = LLMFactory.get_llm(config["provider"], config["model"])
    simulation:BaseSimulation = SimulationFactory.get_simulation(config["name"])(sim_config,llm,save_dir=f"result/{config['name']}")
    simulation.run()
    simulation.save()
    
function_mapping = {
    "herd_effect": herd_effect,
    "social_balance": social_balance,
    "network_growth": network_growth
}


if __name__ == "__main__":
    args = parse_args()
    config = load_config(args.config)
    if config["name"] not in function_mapping:
        default(config)
    else:
        function_mapping[config["name"]](config)
