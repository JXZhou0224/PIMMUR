import json
import os
import random

from API import BaseLLM, LLMFactory
from typing import Any
from agent import Agent
from Metrics import Positivity, BaseMetric

class SimulationFactory:
    _registry: dict[str,Any] = {}

    @classmethod
    def register(cls, sim_name):
        def wrapper(simulation_class):
            cls._registry[sim_name] = simulation_class
        return wrapper
    
    def get_simulation(self, sim_name, config: dict[str, Any], llm: BaseLLM, save_dir = "result") -> Any:
        if sim_name not in self._registry:
            raise ValueError(f"Simulation {sim_name} is not registered.")
        return self._registry[sim_name](config, llm, config["topic"], save_dir)

class BaseSimulation:
    '''
    supports basic functions
    - set up agent_list
    - load LLM
    - basic saving
    '''
    def __init__(self, config: dict[str, Any], llm: BaseLLM,topic: str,save_dir = "result"):
        # save params, load agents
        os.makedirs(save_dir,exist_ok=True)
        self.config = config
        self.llm = llm
        self.topic = topic
        self.agents:list[Agent] = []
        self.history = []
        self.save_dir = save_dir
        agent_configs:list[dict[str, Any]] = config["agents"]
        for ins in agent_configs:
            self.agents.append(Agent(ins,llm, topic))
    def run(self):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def save(self):
        json.dump(self.config,open(os.path.join(self.save_dir,"config.json"),"w"),indent=2)
        json.dump(self.history,open(os.path.join(self.save_dir,"history.json"),"w"),indent=2)

@SimulationFactory.register("herd_effect") 
class HerdEffect(BaseSimulation):
    '''
    IMPORTANT: the Agent of interest must be the last agent in the list
    '''
    def __init__(self, config, llm, topic,save_dir = "result"):
        self.opinion_arc = []
        super().__init__(config, llm, topic,save_dir)

    def run(self, rounds: int = 10):
        init_response = self.agents[-1].query("What is your answer regarding the topic? Please answer with only A, B or C with no explanation")
        self.opinion_arc.append(init_response)
        for i in range(rounds):
            print(f"Round {i+1}")
            for agent in self.agents:
                response = agent.chat()
                for agent_j in self.agents:
                    if agent_j != agent:
                        agent_j.record(agent.profile["name"], response)
                print(f"{agent.profile['name']}: {response}")
                self.history.append({
                    "round": i + 1,
                    "agent": agent.profile["name"],
                    "response": response
                })
            response = self.agents[-1].query("What is your answer regarding the topic? Please answer with only A, B or C with no explanation")
            self.opinion_arc.append(response)
            print(f"Agent of interest: {str(self.opinion_arc)}")
        print("Simulation finished.")
        print("Opinion arc:", self.opinion_arc)

    def save(self):
        json.dump(self.opinion_arc,open(os.path.join(self.save_dir,"opinion_arc.json"),"w"),indent=2)        
        return super().save()

query_relation_prompt="""
Now according to your "Your_opinion_towards_other_agents", reflect on your past chatting history,
and write a new version of the "Your_opinion_towards_other_agents"
You should write a concise, one-sentence summary of your opinion and attitude towards each agent. Do not add or delete names of agents.
Please output only in json format. Do not include ```json or ```
"""

@SimulationFactory.register("social_balance")
class SocialBalance(BaseSimulation):
    def __init__(self, config, llm, topic, save_dir="result"):
        self.relation_arc = []
        super().__init__(config, llm, topic, save_dir)
        self.agent_list = [agent.profile["name"] for agent in self.agents]

    def run(self, rounds: int = 10):
        self.agent_list = [agent.profile["name"] for agent in self.agents]
        self.record_relation()
        for i in range(rounds):
            print(f"Round {i + 1}")
            for agent in self.agents:
                response = agent.chat()
                for agent_j in self.agents:
                    if agent_j != agent:
                        agent_j.record(agent.profile["name"], response)
                print(f"{agent.profile['name']}: {response}")
                self.history.append({
                    "round": i + 1,
                    "agent": agent.profile["name"],
                    "response": response
                })
                rsp = json.loads(agent.query(query_relation_prompt))
                agent.profile["Your_opinion_towards_other_agents"] = rsp
            self.record_relation()
            print(f"round {i+1} ends")
            for agent in self.agents:
                print(f"{agent.profile['name']}'s opinion towards other agents: {json.dumps(agent.profile['Your_opinion_towards_other_agents'],indent=2)}")

        print("Simulation finished.")

    def record_relation(self):
        cur_relations = [agent.profile["Your_opinion_towards_other_agents"] for agent in self.agents]
        self.relation_arc.append(self.encode_relation(self.agent_list, cur_relations))

    def encode_relation(self,agent_list:list[str], relations:list[dict[str, str]]) -> str:
        '''
        relation must be in the same order as agent length
        encode the relations into a dict
        '''
        encoded = ""
        cnt = 0
        relation_dict = {}
        metric = Positivity()
        for relation in relations:
            cur_agent = agent_list[cnt]
            cnt += 1
            for name in agent_list:
                if name == cur_agent:
                    continue
                relation_str=relation[name]
                res = metric.get_max(relation_str)
                if res == "pos":
                    encoded += "2"
                else:
                    encoded += "0"
        return encoded

    

    def encode_relation_binary(self,agent_list:list[str], relations:list[dict[str, str]]) -> str:
        '''
        Deprecated
        relation must be in the same order as agent length
        encode the relations into a dict
        '''
        encoded = ""
        cnt = 0
        relation_dict = {}
        for relation in relations:
            cur_agent = agent_list[cnt]
            cnt += 1
            for name in agent_list:
                if name == cur_agent:
                    continue
                if relation[name] == "friend":
                    encoded += "2"
                elif relation[name] == "neutral":
                    encoded += "1"
                elif relation[name] == "enemy":
                    encoded += "0"
                else:
                    raise Exception("invalid relation")
        return encoded

    def save(self):
        json.dump(self.history, open(os.path.join(self.save_dir, "history.json"), "w"), indent=2)

generate_story_prompt = """
You are an experienced pyschologist specialized in character study.
Based on the big five traits for a person named {name}, write a short profile story of {name} that aligns well with his/her traits.

The generated story should:
1. include his/her age, occupation, and a brief background.
2. one to two major beliefs he/she holds that are typical for his Big Five traits.
3. the whole text should be less than 200 words.

The goal is that the generated story should provide a comprehensive yet concise overview of the character, making it easy for an actor to act out this person by solely using this story.

Below are {name}'s big five:
{big_five}

Now, please generate the profile story without any explanation.
"""

chat_prompt = """
You are {name}. Below is your profile:
{profile}
Please adhere to the profile for the task below.

You are at a dinner reception and you have just been introduced to {target}.
And you have just started a conversation with him.
Here is your conversation history so far.
{history}

Now please generate what you would say to {target}. Only output your reponse with no explanation.
"""

opinion_prompt="""
You are {name}. Below is your profile:
{profile}
Please adhere to the profile for the task below.

You are at a dinner reception and you have just been introduced to {target}.
And you have just had a conversation with him.
Here is your conversation history.
{history}

Now, based on your conversation please output a one sentence remark on your impression of {target}. please output your impression with no explanation.
"""

make_friend_prompt="""
You are {name}. Below is your profile:
{profile}
Please adhere to the profile for the task below.

Here are your impression of each person you have met.
{impressions}

Now, from the people you have met above, please select exactly {friend_m} people from the list to make friend with. If there are less than {friend_m} people in the list you may output less than the number required (an empty list [] is allowed).,Please output in the following json format, do not use ```json or ```:
[
    {{"count":1, "name": "name1", "reason": ""}},
    {{"count":2, "name": "name2", "reason": ""}},
    ...
]

"""

@SimulationFactory.register("network_growth")
class NetworkGrowth():

    def __init__(self,llm: BaseLLM,agent_n,friend_m,chat_round):
        from config_generators import load_name
        self.llm = llm
        self.names = random.sample(load_name(),agent_n)
        self.agent_n = agent_n
        self.friend_m = friend_m
        self.chat_round = chat_round
        self.friendship = {name: 0 for name in self.names}
        self.agents =  {}
        self.friend_graph = {name: [] for name in self.names}

    def load(self):
        self.friendship = json.load(open(f"friendship_log.json", "r"))
        self.agents = json.load(open(f"agents_log.json", "r"))
        self.friend_graph = json.load(open(f"friend_graph_log.json", "r"))
        self.names = list(self.friendship.keys())

    def run(self):
        for i in range(self.agent_n):
            if i < len(self.agents):
                continue
            name = self.names[i]
            profile = self.generate_profile(name)
            opinion = {}
            for agent in self.agents:
                ret = self.chat([profile,self.agents[agent]])
                opinion[agent] = ret
            self.agents[name] = profile
            impressions=[{"name":k,"impression":v} for k,v in opinion.items()]
            random.shuffle(impressions)
            rsp = self.llm.generate(make_friend_prompt.format(
                name=name,
                profile=json.dumps(profile, indent=2),
                impressions=json.dumps(impressions, indent=2),
                friend_m=self.friend_m
            ))
            rsp = json.loads(rsp)
            for ins in rsp:
                self.friendship[ins["name"]] += 1
                self.friendship[name] += 1
                self.friend_graph[name].append(ins["name"])
            print(self.friendship)
            print(self.friend_graph)
            json.dump(self.friend_graph, open(f"friend_graph_log.json", "w"), indent=2)
            json.dump(self.friendship, open(f"friendship_log.json", "w"), indent=2)
            json.dump(self.agents, open(f"agents_log.json", "w"), indent=2)
            json.dump(opinion, open(f"impressions/impression_log_{name}.json", "w"), indent=2)
        return self.friendship
    def chat(self,profiles):
        """chat for a few rounds and generate an opinion of profile 1 towards 2"""
        history = []
        for i in range(self.chat_round):
            for j in range(2):
                response = self.llm.generate(chat_prompt.format(
                    name = profiles[j]["name"],
                    profile = json.dumps(profiles[j],indent=2),
                    target = profiles[1-j]["name"],
                    history = "\n".join([msg["name"]+" said: "+msg["content"] for msg in history])
                ))
                history.append({"name": profiles[j]["name"], "content": response})
        opinion = self.llm.generate(opinion_prompt.format(
            name = profiles[0]["name"],
            profile = json.dumps(profiles[0],indent=2),
            target = profiles[1]["name"],
            history = "\n".join([msg["name"]+" said: "+msg["content"] for msg in history])
        ))
        return opinion

    def generate_big_five(self) -> dict[str,str]:
        res = {}
        levels = ["low", "medium", "high"]
        res["openness"] = random.choice(levels)
        res["carefulness"] = random.choice(levels)
        res["extraversion"] = random.choice(levels)
        res["agreeableness"] = random.choice(levels)
        res["neuroticism"] = random.choice(levels)
        return res

    def generate_profile(self,name:str) -> dict[str,Any]:
        big_five = self.generate_big_five()
        big_five_str = "\n".join([f"{k}: {v}" for k, v in big_five.items()])

        profile = self.llm.generate(generate_story_prompt.format(
            name=name,
            big_five=big_five_str
        ))
        return {
            "name": name,
            "big_five_traits": big_five,
            "profile": profile
        }
    
