from typing import Type
import random
def load_name():
    with open("profile_samples/names.txt", "r") as file:
        names = [line.strip() for line in file.readlines()]
    return names

def load_traits():
    with open("profile_samples/traits.txt", "r") as file:
        traits = [line.strip() for line in file.readlines()]
    return traits


class BaseGenerator:
    def generate(self):
        raise NotImplementedError("This method should be overridden by subclasses")
    
class GeneratorFactory:
    _registry: dict[str, Type[BaseGenerator]] = {}

    @classmethod
    def register(cls, provider):
        def wrapper(generator_class):
            cls._registry[provider] = generator_class
            return generator_class
        return wrapper
    
    @classmethod
    def get_generator(cls, provider,) -> BaseGenerator:
        if provider not in cls._registry:
            raise ValueError(f"Generator {provider} is not registered.")
        return cls._registry[provider]()

@GeneratorFactory.register("herd_effect")
class HerdEffectGenerator(BaseGenerator):
    def __init__(self):
        self.names = load_name()
        self.traits = load_traits()

    def generate(self, topic, agreeing_answer, disagreeing_answer, agent_n, agreeing_agent_n):
        '''
        notes: 
        1. agreeing_agent_n <= agent_n - 1 (one is the agent of interest)
        2. chat_order=0, agreeing first, chat_order=1, disagreeing first
        '''

        if (agreeing_agent_n > agent_n - 1) or (agreeing_agent_n < 0):
            raise ValueError("agreeing_agent_n must be in [0, agent_n - 1]")
        
        config = {
            "agent_n":agent_n,
            "agreeing_agent_n":agreeing_agent_n,
            "topic": topic,
            "agreeing_answer": agreeing_answer,
            "disagreeing_answer": disagreeing_answer,
            "agents": []
        }
        name_list = random.sample(self.names,agent_n)
        trait_list = random.sample(self.traits,agent_n)

        for i in range(agent_n):
            cur = {"name":name_list[i]}
            if i < agent_n - 1:
                cur["trait"] = trait_list[i]
            if i < agreeing_agent_n:
                cur["opinon_held_towards_the_topic"] = f"you think '{agreeing_answer}' is the correct answer"
            elif i < agent_n - 1:
                cur["opinon_held_towards_the_topic"] = f"you think '{disagreeing_answer}' is the correct answer"
            config["agents"].append(cur)
        
        return config
            

@GeneratorFactory.register("social_balance")
class SocialBalanceGenerator(BaseGenerator):
    def __init__(self):
        self.names = load_name()
        self.traits = load_traits()

    def generate(self, agent_n,count):
        if agent_n < 3:
            raise ValueError("agent_n must be at least 3")
        ls = []
        for i in range(6):
            if(count % 2 == 0):
                ls.append("enemy")
            else:
                ls.append("friend")
            count = count // 2
        config = {
            "agent_n": agent_n,
            "agents": []
        }
        name_list = random.sample(self.names, agent_n)
        trait_list = random.sample(self.traits, agent_n)

        for i in range(agent_n):
            cur = {"name": name_list[i]}
            cur["trait"] = trait_list[i]
            cur["Your_opinion_towards_other_agents"] = {}
            for name in name_list:
                if name != cur["name"]:
                    cur["Your_opinion_towards_other_agents"][name] = ls.pop()
            config["agents"].append(cur)

        return config