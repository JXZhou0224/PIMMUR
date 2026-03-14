import os        
import openai
import anthropic
import together
from google import genai

class BaseLLM:
    def __init__(self, model_name, temperature=0.0):
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, prompt):
        raise NotImplementedError("This method should be implemented by subclasses.")

class LLMFactory:   
    _registry: dict[str,BaseLLM] = {}

    @classmethod   
    def register(cls,provider):
        def wrapper(llm_class):
            cls._registry[provider] = llm_class
            return llm_class
        return wrapper
    
    @classmethod
    def get_llm(self, provider, model_name, temperature=0.0) -> BaseLLM:
        if provider not in self._registry:
            raise ValueError(f"Model {provider} is not registered.")
        return self._registry[provider](model_name, temperature)
    

    
@LLMFactory.register("openai")
class Openai(BaseLLM):

    def generate(self, prompt):
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )
        return response.choices[0].message.content.strip()


@LLMFactory.register("anthropic")
class Anthropic(BaseLLM):

    def generate(self, prompt):
        client = anthropic.Anthropic(# defaults to os.environ.get("ANTHROPIC_API_KEY")
            )
        message = client.messages.create(
            model=self.model_name,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text.strip()

@LLMFactory.register("together")
class Together(BaseLLM):
    def generate(self, prompt):
        
        client = together.Together(api_key=os.getenv("TOGETHER_API_KEY"))
        response = client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )
        return response.choices[0].message.content.strip()

@LLMFactory.register("google")
class GoogleAI(BaseLLM):
    def generate(self, prompt):
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )
        return response.text