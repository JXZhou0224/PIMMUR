import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
class BaseMetric:
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, response:str) -> float:
        """
        Evaluate the response based on the metric.
        This method should be overridden by subclasses.
        
        :param response: The response to evaluate.
        :return: A float score representing the evaluation.
        """
        raise NotImplementedError("Subclasses should implement this method.")
    
class Length(BaseMetric):
    def __init__(self, name: str = "Length"):
        super().__init__(name)

    def evaluate(self, response: str) -> float:
        """
        Evaluate the length of the response.
        
        :param response: The response to evaluate.
        :return: The length of the response as a float.
        """
        return len(response.split())  # Return length as a float
    
class Positivity(BaseMetric):
    def __init__(self, name: str = "Positivity"):
        super().__init__(name)
        self.evaluator = SentimentIntensityAnalyzer()

    def evaluate(self, response: str) -> float:
        """
        Evaluate the positivity of the response.
        
        :param response: The response to evaluate.
        :return: A float score representing the positivity of the response.
        """
        sentiment = self.evaluator.polarity_scores(response)
        return sentiment['pos']
        
    def get_max(self, response: str) -> str:
        '''
        the most likely sentiment -> Literal["pos","neg"]
        '''
        sentiment = self.evaluator.polarity_scores(response)
        return "pos" if sentiment["pos"] >= sentiment["neg"] else "neg"
        
