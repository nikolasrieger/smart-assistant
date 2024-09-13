from lib.llm_models.model import Model
from enum import Enum
from sys import platform

OS = platform

class PromptTemplate():
    def __init__(self):
        self.__prompt = ""

    def _set_prompt(self, prompt: str):
        self.__prompt = prompt

    def prompt(self):
        return self.__prompt
    
    def generation_config(self):
        return Model.set_generation_config()
    
class GenerateStepsTemplate(PromptTemplate):
    def __init__(self, action_text: str, context: str = ""):
        super().__init__()
        prompt = """Imagine you are a IT-specialist. You get following computer-related task from your boss: {}. Your OS is {}.
        Here is some context to help you from a quick internet search: {}.
        Break down the task into smaller actions based on your knowledge. Use this JSON schema:
            Step = {{"step_name": str}}
        Return a 'list[Step]'. If you don't know which steps to perform or you can't perform it on a comptuer, 
        return an empty JSON.""".format(action_text, OS,  context)
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type ="application/json")
    
class ReflectStepsTemplate(PromptTemplate):
    def __init__(self, action_text: str, steps: list):
        super().__init__()
        prompt = """Imagine you are a IT-specialist. You get following task from your boss: {}. Your OS is {}.
        Break down the task into smaller actions based on your knowledge. You got already this list of steps: {}.
        Reflect if each step makes sense and if the steps are in the correct order. Change wrong steps and/ or add missing steps.
        Use this JSON schema:
            Step = {{"step_name": str}}
        Return a 'list[Step]'. If you don't know which steps to perform return an empty JSON.""".format(action_text, OS, steps)
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type ="application/json")
    
class ExtractTaskTemplate(PromptTemplate):
    def __init__(self, action_text: str, tasks: Enum):
        super().__init__()
        prompt = """Imagine you are a IT-specialist. You get following task: {}. Your OS is {}.
        Break down the task into smaller tasks based on your knowledge. 
        You have a list of possible tasks you can choose from: Task={}. Return one or more tasks from the list, you have to perform in the correct order.
        Add a description, where you add details to the chosen task like what to locate, where to click on, etc. 
        Use this JSON schema:
            Step = {{"step_name": Task, "description": str}}
        Return a 'list[Step]'. If you don't know which steps to perform return an empty JSON.
        """.format(action_text, OS, list(tasks))
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type ="application/json")
    
class EvaluateStepTemplate(PromptTemplate):
    def __init__(self, action_text: str, finished_steps: list, next_step: dict, tasks: Enum, additional_info: str):
        super().__init__()
        if additional_info != "": info = "You got this additional info from your boss: {}, include it in your evaluation.".format(additional_info)
        else: info = ""
        prompt = """Imagine you are a IT-specialist. You get following task from your boss: {}. {} Your OS is {}. 
        Here is a list of steps you already performed: {}. 
        Evaluate the next step: {} you have to perform, if it is not done and makes sense, just return it, else return a fitting next step.
        You have a list of possible tasks you can choose from: Task={}. 
        Add a description, where you add details to the chosen task like what to locate, where to click on, etc.
        Use this JSON schema:
            Step = {{"step_name": Task, "description": str}}
        Return a 'list[Step]'. If you don't know which steps to perform return an empty JSON.""".format(action_text, info, OS, finished_steps, next_step, list(tasks))
        self._set_prompt(prompt)

    def generation_config(self):
        return Model.set_generation_config(response_mime_type ="application/json")
