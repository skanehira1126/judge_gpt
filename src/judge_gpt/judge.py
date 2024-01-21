import openai


class JudgeGPT:

    def __init__(
        self,
        model: str,
        prompt_judge: str,
        seed: int = None,
        temperature: float = 1.0,
    ):
        
        self.client = openai.OpenAI()

        self.model = model
        self.prompt = prompt_judge
        self.seed = seed
        self.temperature = temperature

    

