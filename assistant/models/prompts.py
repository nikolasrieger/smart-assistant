from models.model import Model

class PromptTemplate():
    def __init__(self):
        self.__prompt = ""

    def _set_prompt(self, prompt: str):
        self.__prompt = prompt

    def prompt(self):
        return self.__prompt
    
    def generation_config(self):
        return {}
    
class GenerateStepsTemplate(PromptTemplate):
    def __init__(self, action_text: str):
        super().__init__()
        prompt = """Imagine you are a IT-specialist. You get following task from your boss: {}. 
        Break down the task into smaller actions based on your knowledge. Use this JSON schema:
            Step = {{"step_name": str}}
        Return a 'list[Step]'. If you don't know which steps to perform return an empty JSON.""".format(action_text)
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type ="application/json")
    
class ReflectStepsTemplate(PromptTemplate):
    def __init__(self, action_text: str, steps: list):
        super().__init__()
        prompt = """Imagine you are a IT-specialist. You get following task from your boss: {}. 
        Break down the task into smaller actions based on your knowledge. You got already this list of steps: {}.
        Reflect if each step makes sense and if the steps are in the correct order. Change wrong steps and/ or add missing steps.
        Use this JSON schema:
            Step = {{"step_name": str}}
        Return a 'list[Step]'. If you don't know which steps to perform return an empty JSON.""".format(action_text, steps)
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type ="application/json")
