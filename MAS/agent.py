from API import BaseLLM
import prompt.agent_prompt as agent_prompt
import json
class Agent:
    def __init__(self,profile: dict[str,str],llm:BaseLLM,topic:str):
        self.profile = profile
        self.llm = llm
        self.memory:list[str] = []
        self.topic = topic

    def chat(self):
        prompt = agent_prompt.chat_prompt.format(profile=json.dumps(self.profile), topic=self.topic, memory=json.dumps(self.memory))
        response = self.llm.generate(prompt)
        self.record(self.profile["name"], response)
        return response
    
    def record(self,speaker:str, message: str):
        self.memory.append(f"{speaker}: {message}")

    def query(self,query: str):
        prompt = agent_prompt.query_prompt.format(profile=json.dumps(self.profile), topic=self.topic, memory=json.dumps(self.memory), query=query)
        response = self.llm.generate(prompt)
        return response
    