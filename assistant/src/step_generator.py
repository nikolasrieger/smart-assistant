from lib.llm_models.model import Model
from lib.llm_models.prompts import GenerateStepsTemplate, ReflectStepsTemplate

class StepGenerator():
    def __init__(self, api_key: str):
        self.__model = Model(api_key)

    def generate_step_from_action(self, action_text: str):
        template = GenerateStepsTemplate(action_text)
        draft_steps = self.__model.generate(template.prompt(), template.generation_config())
        reflected_steps = self.__reflect_on_steps(action_text, draft_steps)
        return reflected_steps
    
    def __reflect_on_steps(self, action_text: str, steps: list):
        template = ReflectStepsTemplate(action_text, steps)
        result = self.__model.generate(template.prompt(), template.generation_config())
        return result
